#!/usr/bin/env python3
"""
One-time extraction: freeze terrain tiles from the Imperium Romanum map
into an authored terrain file.

Reads the source map, extracts the specified region, applies city site
removals and pre-placed improvements, then writes a terrain-only XML
file to data/base_terrain.xml.

After running this once, the frozen file becomes the authoritative
terrain source. Edit it directly to change map dimensions, terrain,
or landscape features.

Usage:
    python scripts/freeze_terrain.py
    # Writes to data/base_terrain.xml
"""

import re
import os
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# Source Map Parameters
# ============================================================

SOURCE_MAP = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/Old World"
    "/Maps/The Imperium Romanum.xml"
)
SOURCE_WIDTH = 127

# Extraction region (inclusive). Y-offset MUST be even for hex parity.
SRC_X_MIN = 20
SRC_X_MAX = 42
SRC_Y_MIN = 58
SRC_Y_MAX = 86

NEW_WIDTH = SRC_X_MAX - SRC_X_MIN + 1   # 23
NEW_HEIGHT = SRC_Y_MAX - SRC_Y_MIN + 1  # 29

# ============================================================
# Terrain Transformations
# ============================================================

# Fields to drop from source tiles
DROP_FIELDS = {"Metadata", "TribeSite", "NationSite", "Boundary"}

# City sites to remove (not relevant to Chapter 1)
REMOVE_CITY_SITES: set[int] = {
    10 * NEW_WIDTH + 10,  # 240 - Lugdunum
    18 * NEW_WIDTH + 9,   # 423 - Durocortorum
    7 * NEW_WIDTH + 17,   # 178 - Genua
    17 * NEW_WIDTH + 20,  # 411 - Augusta Vindelicorum
    23 * NEW_WIDTH + 14,  # 543 - Colonia
    25 * NEW_WIDTH + 4,   # 579 - Londinium
    16 * NEW_WIDTH + 3,   # 371 - Caesarodunum/Tours
}

# Pre-placed improvements: (x, y) -> improvement_type
PLACED_IMPROVEMENTS: dict[tuple[int, int], str] = {
    (7, 5): "IMPROVEMENT_GARRISON_1",
    (7, 2): "IMPROVEMENT_NETS",
    (7, 4): "IMPROVEMENT_NETS",
    (5, 5): "IMPROVEMENT_MINE",
    (6, 6): "IMPROVEMENT_MINE",
    (7, 6): "IMPROVEMENT_MINE",
    (4, 5): "IMPROVEMENT_QUARRY",
    (6, 3): "IMPROVEMENT_QUARRY",
    (5, 2): "IMPROVEMENT_QUARRY",
    # Farms near Genava
    (10, 12): "IMPROVEMENT_FARM",
    (11, 11): "IMPROVEMENT_FARM",
    (12, 11): "IMPROVEMENT_FARM",
    (10, 10): "IMPROVEMENT_FARM",
    (11, 10): "IMPROVEMENT_FARM",
    (12, 10): "IMPROVEMENT_FARM",
}

# ============================================================
# Parsing
# ============================================================

@dataclass
class TileData:
    """Raw tile data parsed from XML. Preserves all fields as-is."""
    src_id: int
    src_x: int
    src_y: int
    fields: list[tuple[str, Optional[str]]] = field(default_factory=list)


def parse_tiles(path: str) -> dict[int, TileData]:
    """Parse all tiles from the source map XML."""
    tiles: dict[int, TileData] = {}

    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    tile_blocks = re.split(r'<Tile\s*\n?\s*ID="(\d+)">', content)

    for i in range(1, len(tile_blocks), 2):
        tile_id = int(tile_blocks[i])
        block = tile_blocks[i + 1].split('</Tile>')[0]

        src_x = tile_id % SOURCE_WIDTH
        src_y = tile_id // SOURCE_WIDTH

        tile = TileData(src_id=tile_id, src_x=src_x, src_y=src_y)

        for m in re.finditer(r'<(\w+)\s*/>', block):
            tile.fields.append((m.group(1), None))

        for m in re.finditer(r'<(\w+)>([^<]*)</(\w+)>', block):
            if m.group(1) == m.group(3):
                tile.fields.append((m.group(1), m.group(2)))

        tiles[tile_id] = tile

    return tiles


# ============================================================
# Extraction & Transformation
# ============================================================

def extract_and_transform(
    tiles: dict[int, TileData],
) -> list[tuple[int, list[tuple[str, Optional[str]]]]]:
    """Extract tiles, apply city site removals and improvement overlays.

    Returns list of (new_id, fields) sorted by new_id.
    Each fields list contains only terrain foundation tags.
    """
    # Build improvement map: tile_id -> improvement_type
    imp_map: dict[int, str] = {
        y * NEW_WIDTH + x: imp
        for (x, y), imp in PLACED_IMPROVEMENTS.items()
    }

    result: list[tuple[int, list[tuple[str, Optional[str]]]]] = []

    for new_y in range(NEW_HEIGHT):
        for new_x in range(NEW_WIDTH):
            src_x = SRC_X_MIN + new_x
            src_y = SRC_Y_MIN + new_y
            src_id = src_y * SOURCE_WIDTH + src_x
            new_id = new_y * NEW_WIDTH + new_x

            tile = tiles.get(src_id)
            if tile is None:
                tile = TileData(src_id=src_id, src_x=src_x, src_y=src_y)
                tile.fields = [
                    ("Terrain", "TERRAIN_WATER"),
                    ("Height", "HEIGHT_OCEAN"),
                ]

            placed_imp = imp_map.get(new_id)
            is_removed_site = new_id in REMOVE_CITY_SITES
            source_has_improvement = any(
                tag == "Improvement" for tag, _ in tile.fields
            )

            out_fields: list[tuple[str, Optional[str]]] = []

            for tag, value in tile.fields:
                if tag in DROP_FIELDS:
                    continue

                # Remove city sites not relevant to Chapter 1
                if is_removed_site:
                    if tag == "CitySite":
                        continue
                    if tag == "Improvement" and value == "IMPROVEMENT_CITY_SITE":
                        # Replace with pre-placed improvement if scheduled
                        if placed_imp is not None:
                            out_fields.append(("Improvement", placed_imp))
                            placed_imp = None  # consumed
                        continue
                    if tag == "ElementName":
                        continue
                    if tag == "Terrain" and value == "TERRAIN_URBAN":
                        out_fields.append(("Terrain", "TERRAIN_LUSH"))
                        continue

                # Override Improvement if this tile has a pre-placed one
                if tag == "Improvement" and placed_imp is not None:
                    out_fields.append(("Improvement", placed_imp))
                    placed_imp = None  # consumed
                    continue

                out_fields.append((tag, value))

            # Add pre-placed improvement if source tile had none
            if placed_imp is not None and not source_has_improvement:
                out_fields.append(("Improvement", placed_imp))

            result.append((new_id, out_fields))

    return result


# ============================================================
# Output
# ============================================================

def write_frozen_xml(
    tiles: list[tuple[int, list[tuple[str, Optional[str]]]]],
    output_path: str,
) -> None:
    """Write the frozen terrain XML."""
    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append(f'<Root MapWidth="{NEW_WIDTH}">')

    for new_id, fields in tiles:
        lines.append(f'  <Tile')
        lines.append(f'    ID="{new_id}">')
        for tag, value in fields:
            if value is None:
                lines.append(f'    <{tag} />')
            else:
                lines.append(f'    <{tag}>{value}</{tag}>')
        lines.append('  </Tile>')

    lines.append('</Root>')
    lines.append('')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    # Count improvements
    imp_count = sum(
        1 for _, fields in tiles
        if any(tag == "Improvement" for tag, _ in fields)
    )
    site_count = sum(
        1 for _, fields in tiles
        if any(tag == "CitySite" for tag, _ in fields)
    )

    print(f"Frozen terrain: {output_path}")
    print(f"  Dimensions: {NEW_WIDTH} x {NEW_HEIGHT} = {len(tiles)} tiles")
    print(f"  City sites: {site_count}")
    print(f"  Improvements: {imp_count}")
    print(f"  Removed city sites: {len(REMOVE_CITY_SITES)}")
    print(f"  Source: {SOURCE_MAP}")
    print(f"  Region: x=[{SRC_X_MIN},{SRC_X_MAX}], y=[{SRC_Y_MIN},{SRC_Y_MAX}]")


# ============================================================
# Main
# ============================================================

def main() -> None:
    print(f"Reading source map: {SOURCE_MAP}")
    source_tiles = parse_tiles(SOURCE_MAP)
    print(f"  Parsed {len(source_tiles)} tiles (source map: {SOURCE_WIDTH} wide)")

    transformed = extract_and_transform(source_tiles)
    print(f"  Extracted and transformed {len(transformed)} tiles")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(project_dir, "data", "base_terrain.xml")

    write_frozen_xml(transformed, output_path)


if __name__ == "__main__":
    main()

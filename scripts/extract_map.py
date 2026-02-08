#!/usr/bin/env python3
"""
Extract a rectangular region from the Imperium Romanum map.

Reads the source map XML, extracts tiles in the specified x,y range,
remaps tile IDs to the new grid, and marks edge tiles as boundaries.

Usage:
    python scripts/extract_map.py
    # Writes to GallicWars/Maps/GallicWars1Map.xml
"""

import re
import os
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# Extraction Parameters
# ============================================================

SOURCE_MAP = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/Old World"
    "/Maps/The Imperium Romanum.xml"
)
SOURCE_WIDTH = 127

# Extraction region (inclusive)
SRC_X_MIN = 20
SRC_X_MAX = 42
SRC_Y_MIN = 58
SRC_Y_MAX = 86

NEW_WIDTH = SRC_X_MAX - SRC_X_MIN + 1   # 23
NEW_HEIGHT = SRC_Y_MAX - SRC_Y_MIN + 1  # 28


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
    # fields is a list of (tag, value) pairs.
    # Self-closing tags like <Boundary /> have value=None.
    # Regular tags like <Terrain>TERRAIN_WATER</Terrain> have the text value.


def parse_tiles(path: str) -> dict[int, TileData]:
    """Parse all tiles from the source map XML."""
    tiles: dict[int, TileData] = {}

    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Split into tile blocks
    tile_blocks = re.split(r'<Tile\s*\n?\s*ID="(\d+)">', content)
    # tile_blocks[0] is the header, then alternating: id_str, block_content

    for i in range(1, len(tile_blocks), 2):
        tile_id = int(tile_blocks[i])
        block = tile_blocks[i + 1].split('</Tile>')[0]

        src_x = tile_id % SOURCE_WIDTH
        src_y = tile_id // SOURCE_WIDTH

        tile = TileData(src_id=tile_id, src_x=src_x, src_y=src_y)

        # Parse fields from the block
        # Self-closing tags: <Boundary />, <Road />
        for m in re.finditer(r'<(\w+)\s*/>', block):
            tile.fields.append((m.group(1), None))

        # Regular tags: <Tag>Value</Tag>
        for m in re.finditer(r'<(\w+)>([^<]*)</(\w+)>', block):
            if m.group(1) == m.group(3):  # sanity check
                tile.fields.append((m.group(1), m.group(2)))

        tiles[tile_id] = tile

    return tiles


# ============================================================
# Extraction
# ============================================================

def extract_region(
    tiles: dict[int, TileData],
) -> list[tuple[int, TileData, bool]]:
    """Extract tiles in the region and compute new IDs.

    Returns list of (new_id, tile_data, is_boundary) sorted by new_id.
    Tiles on the outer 2 rows/columns of the extracted region become boundaries.
    """
    result: list[tuple[int, TileData, bool]] = []

    for new_y in range(NEW_HEIGHT):
        for new_x in range(NEW_WIDTH):
            src_x = SRC_X_MIN + new_x
            src_y = SRC_Y_MIN + new_y
            src_id = src_y * SOURCE_WIDTH + src_x

            new_id = new_y * NEW_WIDTH + new_x

            tile = tiles.get(src_id)
            if tile is None:
                # Shouldn't happen, but create an empty tile
                tile = TileData(src_id=src_id, src_x=src_x, src_y=src_y)
                tile.fields = [
                    ("Terrain", "TERRAIN_WATER"),
                    ("Height", "HEIGHT_OCEAN"),
                ]

            # Mark edges as boundaries (outer 2 tiles on each side)
            is_boundary = (
                new_x <= 1 or new_x >= NEW_WIDTH - 2 or
                new_y <= 1 or new_y >= NEW_HEIGHT - 2
            )

            # Add NationSite for Rome at Narbo (new 6,3)
            if new_x == 6 and new_y == 4:
                tile.fields.append(("NationSite", "NATION_ROME"))

            result.append((new_id, tile, is_boundary))

    return result


# ============================================================
# Output
# ============================================================

# Fields to drop from extracted tiles
DROP_FIELDS = {"Metadata", "Improvement", "TribeSite", "Road"}


def write_xml(
    extracted: list[tuple[int, TileData, bool]],
    output_path: str,
) -> None:
    """Write the extracted map as Old World XML."""
    lines: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Root',
        f'  MapWidth="{NEW_WIDTH}"',
        '  MapEdgesSafe="True">',
    ]

    for new_id, tile, is_boundary in extracted:
        lines.append(f'  <Tile')
        lines.append(f'    ID="{new_id}">')

        if is_boundary:
            lines.append('    <Boundary />')

        # Write tile fields, preserving order
        for tag, value in tile.fields:
            # Skip fields we want to drop
            if tag in DROP_FIELDS:
                continue
            # Skip Boundary from source — we handle it ourselves
            if tag == "Boundary":
                continue
            if value is None:
                # Self-closing tag (other than Boundary which we already handle)
                lines.append(f'    <{tag} />')
            else:
                lines.append(f'    <{tag}>{value}</{tag}>')

        lines.append('  </Tile>')

    lines.append('</Root>')
    lines.append('')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    print(f"Extracted {len(extracted)} tiles to {output_path}")
    print(f"  Source region: x=[{SRC_X_MIN},{SRC_X_MAX}], y=[{SRC_Y_MIN},{SRC_Y_MAX}]")
    print(f"  New dimensions: {NEW_WIDTH} x {NEW_HEIGHT} = {NEW_WIDTH * NEW_HEIGHT} tiles")


# ============================================================
# Main
# ============================================================

def main() -> None:
    print(f"Reading source map: {SOURCE_MAP}")
    tiles = parse_tiles(SOURCE_MAP)
    print(f"  Parsed {len(tiles)} tiles (source map: {SOURCE_WIDTH} wide)")

    extracted = extract_region(tiles)
    print(f"  Extracted {len(extracted)} tiles")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(
        project_dir, "GallicWars", "Maps", "GallicWars1Map.xml"
    )

    write_xml(extracted, output_path)


if __name__ == "__main__":
    main()

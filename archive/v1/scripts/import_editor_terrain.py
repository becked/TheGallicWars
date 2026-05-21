#!/usr/bin/env python3
"""Import specific terrain changes from the editor map back into base_terrain.xml.

Compares the editor map (save-file format) with the base terrain file and imports:
- Height changes (all)
- Terrain changes (ONLY where editor has TERRAIN_TUNDRA; skip TERRAIN_URBAN)
- River changes (RiverW, RiverSW, RiverSE): add new, update changed, remove deleted

Skips: CitySite, TribeSite, TERRAIN_URBAN, and all other fields.
Skips boundary tiles (x<2, x>=35, y<2, y>=39).
"""

import re
import sys
from pathlib import Path
from typing import Optional


MAP_WIDTH = 37
MAP_HEIGHT = 41  # 1517 tiles / 37 = 41

# Boundary: outer 2 rows/columns
BOUNDARY_X_MIN = 2
BOUNDARY_X_MAX = 35  # x >= 35 is boundary
BOUNDARY_Y_MIN = 2
BOUNDARY_Y_MAX = 39  # y >= 39 is boundary

RIVER_FIELDS = ("RiverW", "RiverSW", "RiverSE")

# Canonical field ordering for output
FIELD_ORDER = [
    "Terrain", "Height", "Vegetation", "Resource", "Road",
    "RiverW", "RiverSW", "RiverSE",
    "CitySite", "Improvement", "ElementName",
]


def tile_id_to_xy(tile_id: int) -> tuple[int, int]:
    """Convert tile ID to (x, y) coordinates. ID = y * MapWidth + x."""
    x = tile_id % MAP_WIDTH
    y = tile_id // MAP_WIDTH
    return x, y


def is_boundary(tile_id: int) -> bool:
    """Check if tile is in the boundary region (outer 2 rows/columns)."""
    x, y = tile_id_to_xy(tile_id)
    return x < BOUNDARY_X_MIN or x >= BOUNDARY_X_MAX or y < BOUNDARY_Y_MIN or y >= BOUNDARY_Y_MAX


def parse_tile_fields(tile_body: str) -> dict[str, Optional[str]]:
    """Parse fields from a tile block body text.

    Returns dict mapping field name to value.
    Self-closing tags like <CitySite /> have value None.
    Tags like <RiverSW>1</RiverSW> have string value "1".
    """
    fields: dict[str, Optional[str]] = {}

    # Match self-closing tags: <FieldName /> or <FieldName/>
    for m in re.finditer(r'<(\w+)\s*/>', tile_body):
        tag = m.group(1)
        if tag == "Boundary":
            continue  # Skip editor-only Boundary tag
        fields[tag] = None

    # Match value tags: <FieldName>value</FieldName>
    for m in re.finditer(r'<(\w+)>([^<]+)</\1>', tile_body):
        tag = m.group(1)
        if tag == "ID":
            continue
        fields[tag] = m.group(2).strip()

    return fields


def parse_tiles(content: str) -> dict[int, dict[str, Optional[str]]]:
    """Parse all <Tile> blocks from XML content."""
    tiles: dict[int, dict[str, Optional[str]]] = {}
    pattern = re.compile(r'<Tile\s+ID="(\d+)">(.*?)</Tile>', re.DOTALL)
    for m in pattern.finditer(content):
        tile_id = int(m.group(1))
        tiles[tile_id] = parse_tile_fields(m.group(2))
    return tiles


def format_tile(tile_id: int, fields: dict[str, Optional[str]]) -> str:
    """Format a tile block in base_terrain.xml style."""
    lines: list[str] = []
    lines.append("  <Tile")
    lines.append(f'    ID="{tile_id}">')

    # Output fields in canonical order
    output_keys: list[str] = []
    for key in FIELD_ORDER:
        if key in fields:
            output_keys.append(key)
    # Safety: any extra fields not in FIELD_ORDER
    for key in fields:
        if key not in output_keys:
            output_keys.append(key)

    for key in output_keys:
        value = fields[key]
        if value is None:
            lines.append(f"    <{key} />")
        else:
            lines.append(f"    <{key}>{value}</{key}>")

    lines.append("  </Tile>")
    return "\n".join(lines)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    base_path = project_root / "data" / "base_terrain.xml"
    editor_path = project_root / "docs" / "GallicWars1Map.xml"

    print(f"Base terrain: {base_path}")
    print(f"Editor map:   {editor_path}")
    print()

    base_content = base_path.read_text(encoding="utf-8-sig")
    editor_content = editor_path.read_text(encoding="utf-8-sig")

    base_tiles = parse_tiles(base_content)
    editor_tiles = parse_tiles(editor_content)

    print(f"Base tiles:   {len(base_tiles)}")
    print(f"Editor tiles: {len(editor_tiles)}")
    print()

    if len(base_tiles) != len(editor_tiles):
        print("ERROR: Tile count mismatch!")
        sys.exit(1)

    # Track changes for summary
    height_changes: list[tuple[int, str, str]] = []
    terrain_changes: list[tuple[int, str, str]] = []
    river_adds: list[tuple[int, str, str]] = []
    river_updates: list[tuple[int, str, str, str]] = []
    river_removes: list[tuple[int, str, str]] = []

    for tile_id in sorted(base_tiles.keys()):
        if is_boundary(tile_id):
            continue

        base = base_tiles[tile_id]
        editor = editor_tiles[tile_id]
        x, y = tile_id_to_xy(tile_id)

        # 1. Height changes (all)
        base_height = base.get("Height", "")
        editor_height = editor.get("Height", "")
        if base_height != editor_height and editor_height:
            height_changes.append((tile_id, base_height, editor_height))
            base["Height"] = editor_height

        # 2. Terrain changes (ONLY where editor has TERRAIN_TUNDRA)
        base_terrain = base.get("Terrain", "")
        editor_terrain = editor.get("Terrain", "")
        if base_terrain != editor_terrain:
            if editor_terrain == "TERRAIN_TUNDRA":
                terrain_changes.append((tile_id, base_terrain, editor_terrain))
                base["Terrain"] = editor_terrain
            # Skip TERRAIN_URBAN and all other terrain changes

        # 3. River changes: add, update, remove
        for rf in RIVER_FIELDS:
            base_val = base.get(rf)
            editor_val = editor.get(rf)

            if base_val is None and editor_val is not None:
                river_adds.append((tile_id, rf, editor_val))
                base[rf] = editor_val
            elif base_val is not None and editor_val is None:
                river_removes.append((tile_id, rf, base_val))
                del base[rf]
            elif base_val is not None and editor_val is not None and base_val != editor_val:
                river_updates.append((tile_id, rf, base_val, editor_val))
                base[rf] = editor_val

    # Print detailed summary
    print("=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)

    if height_changes:
        print(f"\n--- HEIGHT CHANGES ({len(height_changes)}) ---")
        for tid, old, new in height_changes:
            x, y = tile_id_to_xy(tid)
            print(f"  Tile {tid:4d} ({x:2d},{y:2d}): {old} -> {new}")

    if terrain_changes:
        print(f"\n--- TERRAIN CHANGES ({len(terrain_changes)}) ---")
        for tid, old, new in terrain_changes:
            x, y = tile_id_to_xy(tid)
            print(f"  Tile {tid:4d} ({x:2d},{y:2d}): {old} -> {new}")

    if river_adds:
        print(f"\n--- RIVER ADDITIONS ({len(river_adds)}) ---")
        for tid, field, value in river_adds:
            x, y = tile_id_to_xy(tid)
            print(f"  Tile {tid:4d} ({x:2d},{y:2d}): +{field}={value}")

    if river_updates:
        print(f"\n--- RIVER VALUE CHANGES ({len(river_updates)}) ---")
        for tid, field, old, new in river_updates:
            x, y = tile_id_to_xy(tid)
            print(f"  Tile {tid:4d} ({x:2d},{y:2d}): {field}: {old} -> {new}")

    if river_removes:
        print(f"\n--- RIVER REMOVALS ({len(river_removes)}) ---")
        for tid, field, old_val in river_removes:
            x, y = tile_id_to_xy(tid)
            print(f"  Tile {tid:4d} ({x:2d},{y:2d}): -{field} (was {old_val})")

    total = (len(height_changes) + len(terrain_changes) +
             len(river_adds) + len(river_updates) + len(river_removes))

    print(f"\n{'=' * 70}")
    print(f"TOTAL: {total} changes "
          f"({len(height_changes)} height, {len(terrain_changes)} terrain, "
          f"{len(river_adds)} river adds, {len(river_updates)} river updates, "
          f"{len(river_removes)} river removes)")
    print(f"{'=' * 70}")

    if total == 0:
        print("\nNo changes to apply. Files are identical for tracked fields.")
        return

    # Write updated base_terrain.xml
    out_lines: list[str] = []
    out_lines.append('<?xml version="1.0" encoding="utf-8"?>')
    out_lines.append(f'<Root MapWidth="{MAP_WIDTH}">')

    for tile_id in sorted(base_tiles.keys()):
        out_lines.append(format_tile(tile_id, base_tiles[tile_id]))

    out_lines.append("</Root>")
    out_lines.append("")  # trailing newline

    output = "\n".join(out_lines)
    base_path.write_text(output, encoding="utf-8-sig", newline="\n")

    print(f"\nWrote updated base_terrain.xml ({len(base_tiles)} tiles)")


if __name__ == "__main__":
    main()

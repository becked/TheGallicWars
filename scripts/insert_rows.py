#!/usr/bin/env python3
"""
Insert rows into the frozen terrain file.

Reads data/base_terrain.xml, inserts new rows after a specified row,
renumbers all tiles below the insertion point, and writes the result
back in-place.

New tiles copy Terrain and Height from the row above. All other fields
(rivers, vegetation, improvements, etc.) are left blank for manual
authoring.

Usage:
    python scripts/insert_rows.py --after 10 --count 5
    # Inserts 5 new rows after row 10
"""

import argparse
import os
import re
from typing import Optional


def parse_terrain(
    path: str,
) -> tuple[int, int, list[tuple[int, list[tuple[str, Optional[str]]]]]]:
    """Parse the frozen terrain file.

    Returns (width, height, tiles) where tiles is
    [(tile_id, fields), ...] sorted by tile_id.
    """
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    m = re.search(r'MapWidth="(\d+)"', content)
    if m is None:
        raise ValueError(f"No MapWidth found in {path}")
    width = int(m.group(1))

    tiles: list[tuple[int, list[tuple[str, Optional[str]]]]] = []
    tile_blocks = re.split(r'<Tile\s*\n?\s*ID="(\d+)">', content)

    for i in range(1, len(tile_blocks), 2):
        tile_id = int(tile_blocks[i])
        block = tile_blocks[i + 1].split('</Tile>')[0]

        fields: list[tuple[str, Optional[str]]] = []
        for fm in re.finditer(r'<(\w+)\s*/>', block):
            fields.append((fm.group(1), None))
        for fm in re.finditer(r'<(\w+)>([^<]*)</(\w+)>', block):
            if fm.group(1) == fm.group(3):
                fields.append((fm.group(1), fm.group(2)))

        tiles.append((tile_id, fields))

    height = len(tiles) // width
    return width, height, tiles


def get_field(
    fields: list[tuple[str, Optional[str]]],
    tag: str,
) -> Optional[str]:
    """Get the value of a field by tag name."""
    for t, v in fields:
        if t == tag:
            return v
    return None


def write_terrain(
    path: str,
    width: int,
    tiles: list[tuple[int, list[tuple[str, Optional[str]]]]],
) -> None:
    """Write the terrain file."""
    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append(f'<Root MapWidth="{width}">')

    for tile_id, fields in tiles:
        lines.append(f'  <Tile')
        lines.append(f'    ID="{tile_id}">')
        for tag, value in fields:
            if value is None:
                lines.append(f'    <{tag} />')
            else:
                lines.append(f'    <{tag}>{value}</{tag}>')
        lines.append('  </Tile>')

    lines.append('</Root>')
    lines.append('')

    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))


def insert_rows(
    width: int,
    height: int,
    tiles: list[tuple[int, list[tuple[str, Optional[str]]]]],
    after_row: int,
    count: int,
) -> list[tuple[int, list[tuple[str, Optional[str]]]]]:
    """Insert new rows after the specified row.

    Returns the new tile list with inserted rows and renumbered tiles.
    """
    # Build row lookup: row_y -> [(x, fields), ...]
    row_data: dict[int, dict[int, list[tuple[str, Optional[str]]]]] = {}
    for tile_id, fields in tiles:
        y = tile_id // width
        x = tile_id % width
        row_data.setdefault(y, {})[x] = fields

    # Get the template row (row above insertion point) for new tiles
    template_row = row_data.get(after_row, {}) if after_row >= 0 else {}

    result: list[tuple[int, list[tuple[str, Optional[str]]]]] = []

    # Rows 0..after_row: unchanged
    for y in range(after_row + 1):
        for x in range(width):
            tile_id = y * width + x
            fields = row_data.get(y, {}).get(x, [
                ("Terrain", "TERRAIN_WATER"),
                ("Height", "HEIGHT_OCEAN"),
            ])
            result.append((tile_id, fields))

    # New rows: after_row+1 .. after_row+count
    for row_offset in range(count):
        new_y = after_row + 1 + row_offset
        for x in range(width):
            tile_id = new_y * width + x
            # Copy terrain and height from template row
            template = template_row.get(x, [])
            terrain = get_field(template, "Terrain") or "TERRAIN_LUSH"
            height_val = get_field(template, "Height") or "HEIGHT_FLAT"
            fields: list[tuple[str, Optional[str]]] = [
                ("Terrain", terrain),
                ("Height", height_val),
            ]
            result.append((tile_id, fields))

    # Shifted rows: old after_row+1..end -> now after_row+count+1..end
    id_shift = count * width
    for y in range(after_row + 1, height):
        for x in range(width):
            old_fields = row_data.get(y, {}).get(x, [
                ("Terrain", "TERRAIN_WATER"),
                ("Height", "HEIGHT_OCEAN"),
            ])
            new_tile_id = (y + count) * width + x
            result.append((new_tile_id, old_fields))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insert rows into the frozen terrain file."
    )
    parser.add_argument(
        "--after", type=int, required=True,
        help="Insert new rows after this row number (use -1 for top of map)",
    )
    parser.add_argument(
        "--count", type=int, required=True,
        help="Number of rows to insert",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")

    print(f"Reading: {terrain_path}")
    width, height, tiles = parse_terrain(terrain_path)
    print(f"  Current: {width} x {height} = {len(tiles)} tiles")

    if args.after < -1 or args.after >= height:
        print(f"Error: --after must be between -1 and {height - 1}")
        return
    if args.count < 1:
        print("Error: --count must be at least 1")
        return
    if args.count % 2 != 0:
        print("Error: --count must be even to preserve hex row parity.")
        print("  Odd shifts flip even/odd row alignment, breaking river")
        print("  edges (RiverSW/RiverSE connect to different neighbors")
        print("  on even vs odd rows).")
        return

    new_tiles = insert_rows(width, height, tiles, args.after, args.count)
    new_height = height + args.count

    write_terrain(terrain_path, width, new_tiles)

    print(f"  New: {width} x {new_height} = {len(new_tiles)} tiles")
    print(f"  Inserted {args.count} rows after row {args.after}")
    print(f"  New rows {args.after + 1}..{args.after + args.count}: "
          f"terrain/height copied from row {args.after}")
    print(f"  Rows {args.after + args.count + 1}+ shifted down by {args.count}")

    # Print coordinate shift reminder
    print()
    print("REMINDER: Update coordinates in scripts/generate_scenario.py")
    print(f"  Any city/unit with y > {args.after} needs y += {args.count}")
    print()

    # Read generate_scenario.py to find affected coordinates
    gen_path = os.path.join(project_dir, "scripts", "generate_scenario.py")
    if os.path.exists(gen_path):
        with open(gen_path, 'r') as f:
            gen_content = f.read()
        # Find coordinate constants
        for m in re.finditer(
            r'^(\w+_[XY])\s*=\s*(\d+)', gen_content, re.MULTILINE
        ):
            name = m.group(1)
            val = int(m.group(2))
            if name.endswith('_Y') and val > args.after:
                print(f"  {name} = {val} -> {val + args.count}")
            elif name.endswith('_X'):
                # X coordinates unaffected by row insertion
                pass

        # Find territory bounds
        for m in re.finditer(
            r'territory_y_(\w+)=(\d+)', gen_content
        ):
            bound_type = m.group(1)
            val = int(m.group(2))
            if val > args.after:
                print(f"  territory_y_{bound_type}={val} -> {val + args.count}")


if __name__ == "__main__":
    main()

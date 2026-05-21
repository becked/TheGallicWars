#!/usr/bin/env python3
"""
Insert columns into the frozen terrain file.

Reads data/base_terrain.xml, inserts new columns after a specified column,
renumbers all tiles, and writes the result back in-place.

New tiles copy Terrain and Height from the column to their left. All other
fields (rivers, vegetation, improvements, etc.) are left blank for manual
authoring.

Usage:
    python scripts/insert_columns.py --after 13 --count 6
    # Inserts 6 new columns after column 13
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


def insert_columns(
    width: int,
    height: int,
    tiles: list[tuple[int, list[tuple[str, Optional[str]]]]],
    after_col: int,
    count: int,
) -> list[tuple[int, list[tuple[str, Optional[str]]]]]:
    """Insert new columns after the specified column.

    Returns the new tile list with inserted columns and renumbered tiles.
    """
    new_width = width + count

    # Build grid lookup: (y, x) -> fields
    grid: dict[tuple[int, int], list[tuple[str, Optional[str]]]] = {}
    for tile_id, fields in tiles:
        y = tile_id // width
        x = tile_id % width
        grid[(y, x)] = fields

    result: list[tuple[int, list[tuple[str, Optional[str]]]]] = []

    for y in range(height):
        # Columns 0..after_col: unchanged
        for x in range(after_col + 1):
            new_tile_id = y * new_width + x
            fields = grid.get((y, x), [
                ("Terrain", "TERRAIN_WATER"),
                ("Height", "HEIGHT_OCEAN"),
            ])
            result.append((new_tile_id, fields))

        # New columns: after_col+1 .. after_col+count
        template_fields = grid.get((y, after_col), [])
        terrain = get_field(template_fields, "Terrain") or "TERRAIN_LUSH"
        height_val = get_field(template_fields, "Height") or "HEIGHT_FLAT"
        for col_offset in range(count):
            new_x = after_col + 1 + col_offset
            new_tile_id = y * new_width + new_x
            fields: list[tuple[str, Optional[str]]] = [
                ("Terrain", terrain),
                ("Height", height_val),
            ]
            result.append((new_tile_id, fields))

        # Shifted columns: old after_col+1..width-1
        for x in range(after_col + 1, width):
            new_x = x + count
            new_tile_id = y * new_width + new_x
            fields = grid.get((y, x), [
                ("Terrain", "TERRAIN_WATER"),
                ("Height", "HEIGHT_OCEAN"),
            ])
            result.append((new_tile_id, fields))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insert columns into the frozen terrain file."
    )
    parser.add_argument(
        "--after", type=int, required=True,
        help="Insert new columns after this column number",
    )
    parser.add_argument(
        "--count", type=int, required=True,
        help="Number of columns to insert",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")

    print(f"Reading: {terrain_path}")
    width, height, tiles = parse_terrain(terrain_path)
    print(f"  Current: {width} x {height} = {len(tiles)} tiles")

    if args.after < -1 or args.after >= width:
        print(f"Error: --after must be between -1 and {width - 1}")
        return
    if args.count < 1:
        print("Error: --count must be at least 1")
        return

    new_tiles = insert_columns(width, height, tiles, args.after, args.count)
    new_width = width + args.count

    write_terrain(terrain_path, new_width, new_tiles)

    print(f"  New: {new_width} x {height} = {len(new_tiles)} tiles")
    print(f"  Inserted {args.count} columns after column {args.after}")
    print(f"  New columns {args.after + 1}..{args.after + args.count}: "
          f"terrain/height copied from column {args.after}")
    print(f"  Columns {args.after + args.count + 1}+ shifted right by {args.count}")

    # Print coordinate shift reminder
    print()
    print("REMINDER: Update coordinates in scripts/generate_scenario.py")
    print(f"  Any city/unit with x > {args.after} needs x += {args.count}")
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
            if name.endswith('_X') and val > args.after:
                print(f"  {name} = {val} -> {val + args.count}")

        # Find territory bounds
        for m in re.finditer(
            r'territory_x_(\w+)=(\d+)', gen_content
        ):
            bound_type = m.group(1)
            val = int(m.group(2))
            if val > args.after:
                print(f"  territory_x_{bound_type}={val} -> {val + args.count}")

        # Find extra_territory tuples with x > after
        for m in re.finditer(r'\((\d+),\s*(\d+)\)', gen_content):
            x_val = int(m.group(1))
            y_val = int(m.group(2))
            if x_val > args.after:
                print(f"  extra_territory ({x_val}, {y_val}) -> ({x_val + args.count}, {y_val})")


if __name__ == "__main__":
    main()

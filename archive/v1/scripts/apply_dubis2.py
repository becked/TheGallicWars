#!/usr/bin/env python3
"""Apply updated Dubis river edges from second map editor pass."""

import os
import re

MAP_WIDTH = 27


def tile_id(x: int, y: int) -> int:
    return y * MAP_WIDTH + x


# Full set of Dubis river edges from the updated map-edit.xml
# (translated from editor width=32 with x_offset=2)
SET_RIVERS: dict[int, dict[str, int]] = {
    tile_id(13, 18): {"RiverSE": 0},
    tile_id(14, 18): {"RiverW": 1},
    tile_id(14, 19): {"RiverSE": 0},
    tile_id(15, 19): {"RiverW": 1},
    tile_id(12, 20): {"RiverW": 1, "RiverSW": 1, "RiverSE": 1},  # NEW
    tile_id(13, 20): {"RiverW": 0},                                 # NEW
    tile_id(14, 20): {"RiverW": 1, "RiverSW": 1},
    tile_id(11, 21): {"RiverSW": 1, "RiverSE": 1},
    tile_id(12, 21): {"RiverSW": 1},                                # CHANGED: removed SE
    tile_id(13, 21): {"RiverSE": 1},                                # CHANGED: removed SW
    tile_id(14, 21): {"RiverW": 0, "RiverSE": 0},                  # Vesontio
    tile_id(15, 21): {"RiverW": 1},
    tile_id(13, 22): {"RiverSE": 1},
    tile_id(14, 22): {"RiverSW": 1},
}

# All tiles that might have old river data to clear
CLEAR: set[int] = set(SET_RIVERS.keys()) | {
    tile_id(15, 20),  # old horseshoe
    tile_id(16, 21),  # old horseshoe
    tile_id(15, 22),  # old horseshoe
    tile_id(16, 22),  # old horseshoe
}


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")

    with open(terrain_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    modified = 0
    for tid in sorted(CLEAR):
        x = tid % MAP_WIDTH
        y = tid // MAP_WIDTH

        pattern = rf'(<Tile\s*\n?\s*ID="{tid}">)(.*?)(</Tile>)'
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            print(f"  WARNING: tile {tid} ({x},{y}) not found!")
            continue

        header = m.group(1)
        inner = m.group(2)
        closer = m.group(3)

        new_inner = re.sub(
            r'\s*<River(?:W|SW|SE)>\d+</River(?:W|SW|SE)>', '', inner
        )

        rivers = SET_RIVERS.get(tid, {})
        if rivers:
            river_lines = ""
            for field, value in rivers.items():
                river_lines += f"\n    <{field}>{value}</{field}>"
            new_inner = new_inner.rstrip() + river_lines + "\n    "

        if new_inner != inner:
            content = content[:m.start()] + header + new_inner + closer + content[m.end():]
            modified += 1
            river_str = ", ".join(f"{k}={v}" for k, v in rivers.items()) if rivers else "cleared"
            print(f"  ({x},{y}) ID {tid}: {river_str}")

    with open(terrain_path, "w", encoding="utf-8-sig") as f:
        f.write(content)

    print(f"\nModified {modified} tiles")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Revert the Dubis river to start-of-session state.

Undoes the changes made by fix_dubis.py, restoring tiles to the
horseshoe state from the previous session.
"""

import os
import re

MAP_WIDTH = 27


def tile_id(x: int, y: int) -> int:
    return y * MAP_WIDTH + x


# Restore each tile to its pre-fix_dubis.py state
# Format: {tile_id: {field: value} or None for "remove all rivers"}
RESTORE: dict[int, dict[str, int] | None] = {
    # fix_dubis.py changed W+SW+SE → W+SW; restore SE
    tile_id(14, 18): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},

    # fix_dubis.py added W+SW; restore to no rivers
    tile_id(16, 18): None,

    # fix_dubis.py changed W+SW+SE → W+SW; restore SE
    tile_id(14, 19): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},

    # fix_dubis.py added W+SW; restore to no rivers
    tile_id(16, 19): None,

    # fix_dubis.py added W+SW; restore to no rivers
    tile_id(14, 20): None,

    # fix_dubis.py cleared all rivers; restore W+SW+SE
    tile_id(15, 20): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},

    # fix_dubis.py added W+SW; restore to no rivers
    tile_id(16, 20): None,

    # fix_dubis.py cleared all rivers; restore W+SW+SE
    tile_id(15, 21): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},

    # fix_dubis.py changed W+SW+SE → SW+SE; restore W
    tile_id(14, 22): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},

    # fix_dubis.py changed W+SW+SE → SW+SE; restore W
    tile_id(15, 22): {"RiverW": 0, "RiverSW": 0, "RiverSE": 0},
}


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")

    with open(terrain_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    for tid, rivers in RESTORE.items():
        x = tid % MAP_WIDTH
        y = tid // MAP_WIDTH

        # Find the tile block
        pattern = rf'(<Tile\s*\n?\s*ID="{tid}">)(.*?)(</Tile>)'
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            print(f"  WARNING: tile {tid} ({x},{y}) not found!")
            continue

        header = m.group(1)
        inner = m.group(2)
        closer = m.group(3)

        # Remove all existing river fields
        new_inner = re.sub(
            r'\s*<River(?:W|SW|SE)>\d+</River(?:W|SW|SE)>', '', inner
        )

        # Add back the rivers we want
        if rivers:
            river_lines = ""
            for field, value in rivers.items():
                river_lines += f"\n    <{field}>{value}</{field}>"
            new_inner = new_inner.rstrip() + river_lines + "\n    "

        content = content[:m.start()] + header + new_inner + closer + content[m.end():]

        river_str = (
            ", ".join(f"{k}={v}" for k, v in rivers.items())
            if rivers else "none"
        )
        print(f"  ({x},{y}) ID {tid}: → {river_str}")

    with open(terrain_path, "w", encoding="utf-8-sig") as f:
        f.write(content)

    print("\nReverted to start-of-session state.")


if __name__ == "__main__":
    main()

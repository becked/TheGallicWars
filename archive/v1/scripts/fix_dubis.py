#!/usr/bin/env python3
"""Fix the Dubis horseshoe river around Vesontio.

Strips all river data from the horseshoe area tiles, then places
minimal edges using proven patterns:
- W+SW for north-south segments (like the working Arar river)
- SW+SE for east-flowing segments
- W+SW+SE only at the junction/corner tile
"""

import os
import re

MAP_WIDTH = 27

def tile_id(x: int, y: int) -> int:
    return y * MAP_WIDTH + x

# Tiles to CLEAR all river data from (the horseshoe area)
# Include all tiles that might have unwanted Dubis river edges
CLEAR_TILES: set[int] = set()
for y in range(17, 23):
    for x in range(13, 18):
        CLEAR_TILES.add(tile_id(x, y))

# Also clear specific tiles we know have unwanted rivers
for coord in [(10, 20), (11, 20), (12, 21)]:
    # Don't clear (12,21) - that's the Arar river!
    pass

# Remove (12,21) from clear set - it's Arar, not Dubis
CLEAR_TILES.discard(tile_id(12, 21))

# River edges to SET on each tile
# Format: {tile_id: {field: value, ...}}
# Only river fields listed here will be added; all others stripped
RIVER_DATA: dict[int, dict[str, int]] = {
    # === WEST ARM (going north from Jura to junction) ===
    # Pattern: W+SW on each tile (like working Arar)
    tile_id(14, 18): {"RiverW": 0, "RiverSW": 0},         # south end
    tile_id(14, 19): {"RiverW": 0, "RiverSW": 0},         # west arm
    tile_id(14, 20): {"RiverW": 0, "RiverSW": 0},         # west arm

    # === JUNCTION (13,21) — Dubis meets Arar ===
    # W=1 connects to Arar, SW+SE wrap the corner to east-flowing top
    tile_id(13, 21): {"RiverW": 1, "RiverSW": 0, "RiverSE": 0},

    # === TOP (east-flowing, north of Vesontio) ===
    # Pattern: SW+SE on each tile
    tile_id(14, 22): {"RiverSW": 0, "RiverSE": 0},        # top
    tile_id(15, 22): {"RiverSW": 0, "RiverSE": 0},        # top

    # === NE CORNER (16,22) ===
    tile_id(16, 22): {"RiverW": 0},                         # entry from top

    # === EAST ARM (going south from corner to Jura) ===
    # Pattern: W+SW on each tile
    tile_id(16, 21): {"RiverW": 0, "RiverSW": 0},         # east arm
    tile_id(16, 20): {"RiverW": 0, "RiverSW": 0},         # east arm
    tile_id(16, 19): {"RiverW": 0, "RiverSW": 0},         # east arm
    tile_id(16, 18): {"RiverW": 0, "RiverSW": 0},         # south end
}

RIVER_FIELDS = {"RiverW", "RiverSW", "RiverSE"}


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")

    with open(terrain_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Parse into tile blocks
    # Split on <Tile ... ID="N"> patterns
    parts = re.split(r'(<Tile\s*\n?\s*ID="\d+")', content)

    result_parts: list[str] = []
    modified_count = 0

    for i, part in enumerate(parts):
        # Check if this is a tile header
        m = re.match(r'<Tile\s*\n?\s*ID="(\d+)"', part)
        if m:
            tid = int(m.group(1))
            # The tile content is in parts[i+1]
            if i + 1 < len(parts):
                tile_content = parts[i + 1]
                tile_end = tile_content.split("</Tile>", 1)
                if len(tile_end) == 2:
                    inner = tile_end[0]
                    after = tile_end[1]

                    if tid in CLEAR_TILES:
                        # Remove all river fields
                        new_inner = re.sub(
                            r'\s*<River(?:W|SW|SE)>\d+</River(?:W|SW|SE)>',
                            '', inner
                        )

                        # Add back the river fields we want
                        if tid in RIVER_DATA:
                            river_lines = ""
                            for field, value in RIVER_DATA[tid].items():
                                river_lines += f"\n    <{field}>{value}</{field}>"
                            # Insert before closing
                            new_inner = new_inner.rstrip() + river_lines + "\n    "

                        if new_inner != inner:
                            modified_count += 1
                            x = tid % MAP_WIDTH
                            y = tid // MAP_WIDTH
                            rivers = RIVER_DATA.get(tid, {})
                            river_str = ", ".join(
                                f"{k}={v}" for k, v in rivers.items()
                            ) if rivers else "none"
                            print(f"  ({x},{y}) ID {tid}: {river_str}")

                        parts[i + 1] = new_inner + "</Tile>" + after
                        continue

        result_parts.append(part)

    # Reassemble
    output = "".join(parts)

    with open(terrain_path, "w", encoding="utf-8-sig") as f:
        f.write(output)

    print(f"\nModified {modified_count} tiles")

    # Print the horseshoe path for verification
    print("\nDubis horseshoe path:")
    path = [
        (14, 18), (14, 19), (14, 20),  # west arm
        (13, 21),                        # junction
        (14, 22), (15, 22), (16, 22),   # top
        (16, 21), (16, 20), (16, 19), (16, 18),  # east arm
    ]
    for x, y in path:
        tid = tile_id(x, y)
        rivers = RIVER_DATA.get(tid, {})
        print(f"  ({x},{y}): {', '.join(f'{k}={v}' for k, v in rivers.items())}")


if __name__ == "__main__":
    main()

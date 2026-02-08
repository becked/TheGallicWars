#!/usr/bin/env python3
"""
DEPRECATED: Superseded by extract_map.py, which extracts tiles from
the Imperium Romanum map instead of generating them procedurally.
Kept for reference on terrain zone definitions and river edge patterns.

Generate the Gallic Wars Chapter 1 map XML.

Geographic scope: Eastern Gaul from Aedui territory to the Rhine,
covering Caesar's campaigns against the Helvetii and Ariovistus (58 BC).

Map: 50 tiles wide x 40 tiles tall = 2,000 tiles
Coordinate system: X = column (0=west, 49=east), Y = row
Tile ID = Y * 50 + X

IMPORTANT: In Old World's isometric view, Y increases toward the visual
NORTHEAST. So low Y = visual south (Provincia), high Y = visual north.
X increases toward visual east. The ASCII preview below shows Y=0 at top
(visual south) and Y=39 at bottom (visual north) to match the grid layout.

Usage:
    python scripts/generate_map.py
    # Writes to GallicWars/Maps/GallicWars1Map.xml

    python scripts/generate_map.py --preview
    # Print ASCII minimap to stdout (no file written)
"""

import argparse
import math
import os
import random
from dataclasses import dataclass
from typing import Optional

# ============================================================
# Map Constants
# ============================================================

MAP_WIDTH = 50
MAP_HEIGHT = 40
TOTAL_TILES = MAP_WIDTH * MAP_HEIGHT
SEED = 58  # 58 BC :)

# Terrain types
WATER = "TERRAIN_WATER"
URBAN = "TERRAIN_URBAN"
LUSH = "TERRAIN_LUSH"
TEMPERATE = "TERRAIN_TEMPERATE"
ARID = "TERRAIN_ARID"
MARSH = "TERRAIN_MARSH"

# Height types
OCEAN = "HEIGHT_OCEAN"
COAST = "HEIGHT_COAST"
LAKE = "HEIGHT_LAKE"
FLAT = "HEIGHT_FLAT"
HILL = "HEIGHT_HILL"
MOUNTAIN = "HEIGHT_MOUNTAIN"

# Vegetation types
TREES = "VEGETATION_TREES"
SCRUB = "VEGETATION_SCRUB"


# ============================================================
# Geographic Layout (Y=0 = visual south, Y=39 = visual north)
# ============================================================
#
#  Visual SOUTH (low Y)                    Visual NORTH (high Y)
#
#  Y: 0  1  2  ...  5  ...  10 ...  16 ... 23 ... 28 ... 35 .. 38 39
#     ~~  ~~  Provincia  Alps  LakeGeneva  Bibracte  Vesontio  Sequani ~~
#              Rome(5)   (SE)  Genava(10)  (12,23)   (30,28)   North
#
#  X: 0=west, 49=east
#     Rhine at x=46, Vosges x=37-40, Jura diagonal, Saone x=22
#
# Detailed layout (Y increases downward = visual north):
#
#  Y:  0-1   Boundary (ocean/coast)
#      2-4   Provincia Romana (Rome starts at 12,5)
#      2-6   Alps (narrow band, x>=36, near south boundary)
#      8-12  Lake Geneva area, Genava, Rhone river
#     13-31  Main Gaul: Aedui heartland (west), Jura, Sequani
#     17-35  Vosges mountains, Alsace plain
#     23     Bibracte (12, 23)
#     28     Vesontio (30, 28)
#     32-37  Northern Gaul / Sequani north
#     38-39  Boundary (ocean/coast)


# ============================================================
# Tile Data Structure
# ============================================================

@dataclass
class Tile:
    id: int
    x: int
    y: int
    terrain: str = TEMPERATE
    height: str = FLAT
    vegetation: Optional[str] = None
    boundary: bool = False
    river_w: Optional[int] = None
    river_sw: Optional[int] = None
    river_se: Optional[int] = None
    nation_site: Optional[str] = None
    city_site: Optional[str] = None
    element_name: Optional[str] = None
    resource: Optional[str] = None


# ============================================================
# Coordinate Helpers
# ============================================================

def xy_to_id(x: int, y: int) -> int:
    return y * MAP_WIDTH + x


def id_to_xy(tile_id: int) -> tuple[int, int]:
    return tile_id % MAP_WIDTH, tile_id // MAP_WIDTH


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ============================================================
# Map Generation
# ============================================================

def create_tiles() -> list[Tile]:
    """Create all tiles with default values."""
    tiles: list[Tile] = []
    for tile_id in range(TOTAL_TILES):
        x, y = id_to_xy(tile_id)
        tiles.append(Tile(id=tile_id, x=x, y=y))
    return tiles


def apply_boundaries(tiles: list[Tile], rng: random.Random) -> None:
    """Mark map edge tiles as boundaries.

    West, North, and East edges: land boundaries (land continues beyond the map).
    South edge: Mediterranean Sea (ocean/coast).
    """
    for t in tiles:
        x, y = t.x, t.y

        # South edge: Mediterranean Sea (highest priority at corners)
        if y <= 1:
            t.boundary = True
            t.terrain = WATER
            t.height = OCEAN if y == 0 else COAST

        # East edge: Germania continues beyond the Rhine
        elif x >= MAP_WIDTH - 2:
            t.boundary = True
            t.terrain = TEMPERATE
            t.height = FLAT
            if rng.random() < 0.15:
                t.vegetation = TREES

        # West edge: land continues westward into Gaul
        elif x <= 1:
            t.boundary = True
            t.terrain = TEMPERATE
            t.height = FLAT
            if rng.random() < 0.15:
                t.vegetation = TREES

        # North edge: land continues northward into Gaul
        elif y >= MAP_HEIGHT - 2:
            t.boundary = True
            t.terrain = TEMPERATE
            t.height = FLAT
            if rng.random() < 0.15:
                t.vegetation = TREES


def apply_base_terrain(tiles: list[Tile], rng: random.Random) -> None:
    """Apply the default Gallic terrain to all non-boundary tiles."""
    for t in tiles:
        if t.boundary:
            continue
        t.terrain = TEMPERATE
        t.height = FLAT
        if rng.random() < 0.12:
            t.vegetation = TREES
        elif rng.random() < 0.05:
            t.vegetation = SCRUB


def apply_provincia(tiles: list[Tile], rng: random.Random) -> None:
    """Southern Roman Provincia (low Y = visual south)."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (3 <= x <= 30 and 2 <= y <= 9):
            continue
        if t.height == MOUNTAIN:
            continue
        t.terrain = TEMPERATE
        if rng.random() < 0.20:
            t.height = HILL
        if rng.random() < 0.12:
            t.vegetation = SCRUB
        elif rng.random() < 0.10:
            t.vegetation = TREES


def apply_aedui_heartland(tiles: list[Tile], rng: random.Random) -> None:
    """Western zone: fertile Aedui territory around Bibracte.
    Rolling agricultural hills, lush terrain, oak forests."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (4 <= x <= 20 and 13 <= y <= 31):
            continue
        t.terrain = LUSH
        if rng.random() < 0.18:
            t.height = HILL
        if rng.random() < 0.28:
            t.vegetation = TREES
        elif rng.random() < 0.08:
            t.vegetation = SCRUB


def apply_sequani_territory(tiles: list[Tile], rng: random.Random) -> None:
    """Central-east: forested hills between Saone and Jura."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (24 <= x <= 34 and 21 <= y <= 35):
            continue
        t.terrain = TEMPERATE
        if rng.random() < 0.30:
            t.height = HILL
        if rng.random() < 0.35:
            t.vegetation = TREES
        elif rng.random() < 0.10:
            t.vegetation = SCRUB


def apply_jura_mountains(tiles: list[Tile], rng: random.Random) -> None:
    """Jura mountain range: runs NE-SW.
    Ridge shifts east as Y increases (going north visually).
    Roughly from (30, 7) in the south to (35, 23) in the north."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (7 <= y <= 23):
            continue

        # Ridge line shifts east as it goes north (higher Y)
        ridge_x = 30.0 + (y - 7) * 0.35
        dist = abs(x - ridge_x)

        if dist > 4.5:
            continue

        if dist < 1.5:
            t.height = MOUNTAIN
            t.terrain = TEMPERATE
            t.vegetation = TREES if rng.random() < 0.5 else None
        elif dist < 3.0:
            t.height = HILL
            t.terrain = TEMPERATE
            t.vegetation = TREES if rng.random() < 0.7 else SCRUB
        else:
            if rng.random() < 0.5:
                t.height = HILL
            t.vegetation = TREES if rng.random() < 0.4 else None


def apply_vosges_mountains(tiles: list[Tile], rng: random.Random) -> None:
    """Vosges mountain range: runs N-S along x~37-40, y~17-35.
    Forested mountains west of the Alsace plain."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (35 <= x <= 42 and 17 <= y <= 35):
            continue

        ridge_x = 38.0
        dist = abs(x - ridge_x)

        if dist < 1.5:
            t.height = MOUNTAIN
            t.terrain = TEMPERATE
            t.vegetation = TREES if rng.random() < 0.6 else None
        elif dist < 3.0:
            t.height = HILL
            t.terrain = TEMPERATE
            t.vegetation = TREES if rng.random() < 0.5 else SCRUB
        elif dist < 4.0:
            if rng.random() < 0.4:
                t.height = HILL
            t.vegetation = TREES if rng.random() < 0.3 else None


def apply_alps(tiles: list[Tile], rng: random.Random) -> None:
    """Alps along the visual south edge (low Y): high impassable mountains.
    Narrow band in the SE of the grid (low Y, high X)."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y

        # Alps: near the south boundary, eastern side
        if x >= 36 and y <= 6:
            edge_dist = min(x - 2, y - 2)  # distance from boundary
            if edge_dist <= 2:
                t.height = MOUNTAIN
                t.terrain = ARID if rng.random() < 0.3 else TEMPERATE
                t.vegetation = None
            elif edge_dist <= 4 and rng.random() < 0.5:
                t.height = MOUNTAIN if rng.random() < 0.4 else HILL
                t.terrain = TEMPERATE
                t.vegetation = SCRUB if rng.random() < 0.3 else None


def apply_alsace_plain(tiles: list[Tile], rng: random.Random) -> None:
    """Flat open plain between Vosges (west) and Rhine (east).
    Good cavalry country - where the Battle of Vosges is fought."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (42 <= x <= 44 and 17 <= y <= 35):
            continue
        t.terrain = TEMPERATE
        t.height = FLAT
        t.vegetation = None
        if rng.random() < 0.08:
            t.vegetation = SCRUB


def apply_rhine(tiles: list[Tile]) -> None:
    """Rhine river: major water barrier on the far east.
    Represented as a column of water tiles."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if x == 46 and 2 <= y <= 37:
            t.terrain = WATER
            t.height = COAST
            t.vegetation = None


def apply_mediterranean(tiles: list[Tile], rng: random.Random) -> None:
    """Create an irregular Mediterranean coastline along the south edge.

    The boundary tiles at y=0-1 provide the base ocean. This function
    extends water into y=2-4 to create bays and a natural-looking coast.
    The deepest bay (Gulf of Lion) is around x=18-28.
    """
    tile_map: dict[tuple[int, int], Tile] = {(t.x, t.y): t for t in tiles}

    # Control points: (x, extra_depth) where extra_depth is how many rows
    # of water ABOVE the y=1 boundary. depth=1 → water at y=2, depth=2 → y=2-3
    coast_control: list[tuple[int, float]] = [
        (2, 0.0),      # western start
        (6, 0.5),       # slight bay begins
        (12, 1.0),      # coast curves in near Provincia
        (18, 2.0),      # Gulf of Lion begins
        (24, 2.5),      # deepest point
        (28, 2.0),      # bay continues
        (32, 1.0),      # approaching Rhone delta
        (36, 0.5),      # Alps approach the coast
        (40, 0.0),      # Alps meet the coast
        (47, 0.0),      # eastern edge
    ]

    for x in range(2, MAP_WIDTH - 2):
        # Interpolate depth from control points
        depth = 0.0
        for i in range(len(coast_control) - 1):
            x1, d1 = coast_control[i]
            x2, d2 = coast_control[i + 1]
            if x1 <= x <= x2:
                frac = (x - x1) / (x2 - x1) if x2 > x1 else 0.0
                depth = d1 + (d2 - d1) * frac
                break

        # Add jitter for natural look
        depth += rng.uniform(-0.4, 0.4)
        int_depth = max(0, round(depth))

        for dy in range(int_depth):
            y = 2 + dy
            t = tile_map.get((x, y))
            if t and not t.boundary:
                t.terrain = WATER
                t.height = COAST
                t.vegetation = None


def apply_lake_geneva(tiles: list[Tile]) -> None:
    """Lake Geneva (Lacus Lemannus): large lake.
    Center at (34, 10) - between Provincia and main Gaul."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        lake_cx, lake_cy = 34.0, 10.0
        dx = (x - lake_cx) / 3.0
        dy = (y - lake_cy) / 1.5
        if dx * dx + dy * dy < 1.0:
            t.terrain = WATER
            t.height = LAKE
            t.vegetation = None


def apply_saone_floodplain(tiles: list[Tile], rng: random.Random) -> None:
    """Marshy/lush terrain along the Saone river corridor."""
    for t in tiles:
        if t.boundary:
            continue
        x, y = t.x, t.y
        if not (11 <= y <= 31):
            continue
        saone_dist = abs(x - 22)
        if saone_dist <= 1:
            if rng.random() < 0.25:
                t.terrain = MARSH
            else:
                t.terrain = LUSH
            t.vegetation = None
        elif saone_dist <= 2:
            t.terrain = LUSH
            if rng.random() < 0.15:
                t.vegetation = TREES


def apply_rivers(tiles: list[Tile]) -> None:
    """Place river edges for major waterways.

    Uses the validated pattern (confirmed via map editor on the Dubis):
    - Every path tile gets W=1 (visible river on west edge)
    - NE step connectivity: SW=1 on the destination tile
    - NW step connectivity: bridge tile at (dest_x-1, dest_y) with SE=0
    """
    tile_map: dict[tuple[int, int], Tile] = {(t.x, t.y): t for t in tiles}

    def set_edge(x: int, y: int, edge: str, value: int) -> None:
        t = tile_map.get((x, y))
        if t and not t.boundary:
            if edge == "W":
                t.river_w = value
            elif edge == "SW":
                t.river_sw = value
            elif edge == "SE":
                t.river_se = value

    def place_river(path: list[tuple[int, int]]) -> None:
        """Place river edges using the validated Dubis pattern.

        Every path tile gets W=1. Connectivity between consecutive tiles:
          NE step (B is NE of A): SW=1 on B
          NW step (B is NW of A): bridge at (B.x-1, B.y) with SE=0

        path: list of (x, y) coordinates from south to north.
        """
        for x, y in path:
            set_edge(x, y, "W", 1)

        for i in range(1, len(path)):
            prev_x, prev_y = path[i - 1]
            curr_x, curr_y = path[i]

            # Compute NE/NW neighbors of previous tile
            if prev_y % 2 == 0:  # even row
                ne = (prev_x, prev_y + 1)
                nw = (prev_x - 1, prev_y + 1)
            else:  # odd row
                ne = (prev_x + 1, prev_y + 1)
                nw = (prev_x, prev_y + 1)

            if (curr_x, curr_y) == ne:
                set_edge(curr_x, curr_y, "SW", 1)
            elif (curr_x, curr_y) == nw:
                set_edge(curr_x - 1, curr_y, "SE", 0)

    # --- Saone (Arar) River ---
    # x=22-23, y=11-30. Meanders between columns.
    place_river([
        (23, 11), (23, 12), (22, 13), (22, 14), (22, 15),
        (22, 16), (22, 17), (23, 18), (23, 19), (23, 20),
        (22, 21), (22, 22), (22, 23), (23, 24), (22, 25),
        (22, 26), (22, 27), (23, 28), (22, 29), (22, 30),
    ])

    # --- Rhone (Rhodanus) River ---
    # x=30-32, y=4-9. Flows NE toward Lake Geneva.
    place_river([
        (30, 4), (30, 5), (31, 6), (31, 7), (32, 8), (32, 9),
    ])

    # --- Doubs (Dubis) River ---
    # x=32, y=26-30. Straight N-S near Vesontio.
    place_river([
        (32, 26), (32, 27), (32, 28), (32, 29), (32, 30),
    ])


def apply_special_tiles(tiles: list[Tile]) -> None:
    """Place cities, nation starting positions, and named features."""
    tile_map: dict[tuple[int, int], Tile] = {(t.x, t.y): t for t in tiles}

    # --- Cities ---

    # Bibracte: Aedui capital, hilltop oppidum
    t = tile_map[(12, 23)]
    t.terrain = URBAN
    t.height = HILL
    t.vegetation = None
    t.element_name = "TEXT_CITYNAME_BIBRACTE"
    t.city_site = "USED"

    # Vesontio (Besancon): Sequani capital, in Doubs river loop
    t = tile_map[(30, 28)]
    t.terrain = URBAN
    t.height = FLAT
    t.vegetation = None
    t.element_name = "TEXT_CITYNAME_VESONTIO"
    t.city_site = "USED"

    # Genava (Geneva): at the western tip of Lake Geneva
    t = tile_map[(31, 10)]
    t.terrain = URBAN
    t.height = FLAT
    t.vegetation = None
    t.element_name = "TEXT_CITYNAME_GENAVA"
    t.city_site = "USED"

    # --- Nation Starting Position ---

    # Rome starts in Provincia (visual south = low Y)
    t = tile_map[(12, 5)]
    t.nation_site = "NATION_ROME"
    t.terrain = URBAN
    t.height = FLAT
    t.vegetation = None

    # --- Named Geographic Features ---

    # Jura Mountains - label a prominent peak
    t = tile_map[(33, 15)]
    if t.height in (MOUNTAIN, HILL):
        t.element_name = "TEXT_JURA_MOUNTAINS"

    # Vosges Mountains - label a prominent peak
    t = tile_map[(38, 27)]
    if t.height in (MOUNTAIN, HILL):
        t.element_name = "TEXT_VOSGES_MOUNTAINS"

    # Alps - label visible alpine peaks
    t = tile_map[(38, 5)]
    if t.height == MOUNTAIN:
        t.element_name = "TEXT_THE_ALPS"

    # Lacus Lemannus
    t = tile_map[(34, 10)]
    if t.height == LAKE:
        t.element_name = "TEXT_LAKE_GENEVA"

    # --- River Labels ---

    # Arar (Saone) - label at midpoint of river
    t = tile_map[(22, 22)]
    t.element_name = "TEXT_RIVER_ARAR"

    # Rhodanus (Rhone) - label at midpoint of river
    t = tile_map[(31, 6)]
    t.element_name = "TEXT_RIVER_RHODANUS"

    # Dubis (Doubs) - label near Vesontio
    t = tile_map[(31, 28)]
    t.element_name = "TEXT_RIVER_DUBIS"

    # --- Battle Sites ---

    # Arar crossing: where Caesar ambushes the Tigurini
    t = tile_map[(22, 15)]
    t.terrain = TEMPERATE
    t.height = FLAT
    t.vegetation = None

    # Bibracte battle site: hillside near the oppidum
    t = tile_map[(13, 21)]
    t.terrain = TEMPERATE
    t.height = HILL
    t.vegetation = None

    # Vosges battle site: open ground on the Alsace plain
    t = tile_map[(43, 27)]
    t.terrain = TEMPERATE
    t.height = FLAT
    t.vegetation = None


def apply_resources(tiles: list[Tile], rng: random.Random) -> None:
    """Scatter resources across the map for gameplay."""
    resources_by_terrain: dict[str, list[tuple[str, float]]] = {
        LUSH: [
            ("RESOURCE_CATTLE", 0.04),
            ("RESOURCE_PIG", 0.03),
            ("RESOURCE_SHEEP", 0.03),
        ],
        TEMPERATE: [
            ("RESOURCE_HORSE", 0.02),
            ("RESOURCE_SHEEP", 0.02),
            ("RESOURCE_GAME", 0.02),
        ],
    }
    resources_by_height: dict[str, list[tuple[str, float]]] = {
        HILL: [
            ("RESOURCE_ORE", 0.04),
            ("RESOURCE_MARBLE", 0.02),
        ],
        MOUNTAIN: [
            ("RESOURCE_ORE", 0.03),
            ("RESOURCE_SILVER", 0.02),
        ],
    }

    for t in tiles:
        if t.boundary or t.terrain in (WATER, URBAN, MARSH) or t.resource:
            continue
        for res, chance in resources_by_terrain.get(t.terrain, []):
            if rng.random() < chance:
                t.resource = res
                break
        if not t.resource:
            for res, chance in resources_by_height.get(t.height, []):
                if rng.random() < chance:
                    t.resource = res
                    break


# ============================================================
# Output
# ============================================================

def write_xml(tiles: list[Tile], output_path: str) -> None:
    """Write the map as Old World XML."""
    lines: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Root',
        f'  MapWidth="{MAP_WIDTH}"',
        '  MapEdgesSafe="True">',
    ]

    for t in tiles:
        lines.append(f'  <Tile')
        lines.append(f'    ID="{t.id}">')

        if t.boundary:
            lines.append('    <Boundary />')

        lines.append(f'    <Terrain>{t.terrain}</Terrain>')
        lines.append(f'    <Height>{t.height}</Height>')

        if t.vegetation:
            lines.append(f'    <Vegetation>{t.vegetation}</Vegetation>')

        if t.river_w is not None:
            lines.append(f'    <RiverW>{t.river_w}</RiverW>')
        if t.river_sw is not None:
            lines.append(f'    <RiverSW>{t.river_sw}</RiverSW>')
        if t.river_se is not None:
            lines.append(f'    <RiverSE>{t.river_se}</RiverSE>')

        if t.nation_site:
            lines.append(f'    <NationSite>{t.nation_site}</NationSite>')

        if t.city_site:
            lines.append(f'    <CitySite>{t.city_site}</CitySite>')

        if t.element_name:
            lines.append(f'    <ElementName>{t.element_name}</ElementName>')

        if t.resource:
            lines.append(f'    <Resource>{t.resource}</Resource>')

        lines.append('  </Tile>')

    lines.append('</Root>')
    lines.append('')

    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    print(f"Wrote {len(tiles)} tiles to {output_path}")


def print_preview(tiles: list[Tile]) -> None:
    """Print an ASCII minimap. Y=0 at top (visual south), Y=39 at bottom (visual north)."""
    tile_map: dict[tuple[int, int], Tile] = {(t.x, t.y): t for t in tiles}

    print(f"\n  Map Preview ({MAP_WIDTH}x{MAP_HEIGHT}, seed={SEED})")
    print(f"  Y=0 (top) = visual SOUTH,  Y=39 (bottom) = visual NORTH")
    print(f"  Legend: ~ water  ^ mountain  n hill  . flat  : lush  , marsh  O city  * Rome  | boundary")
    print()

    header = "    "
    for x in range(0, MAP_WIDTH, 5):
        header += f"{x:<5}"
    print(header)

    for y in range(MAP_HEIGHT):
        row = f"{y:>3} "
        for x in range(MAP_WIDTH):
            t = tile_map[(x, y)]
            if t.nation_site:
                ch = '*'
            elif t.terrain == URBAN:
                ch = 'O'
            elif t.boundary and t.terrain != WATER:
                ch = '|'
            elif t.terrain == WATER:
                ch = '≈' if t.height == LAKE else '~'
            elif t.terrain == MARSH:
                ch = ','
            elif t.height == MOUNTAIN:
                ch = '^'
            elif t.height == HILL:
                ch = 'A' if t.vegetation == TREES else 'n'
            elif t.vegetation == TREES:
                ch = 'T'
            elif t.vegetation == SCRUB:
                ch = ';'
            elif t.terrain == LUSH:
                ch = ':'
            else:
                ch = '.'
            if any(v is not None and v > 0 for v in (t.river_w, t.river_sw, t.river_se)) and ch == '.':
                ch = '~'
            row += ch
        # Add orientation labels
        if y == 0:
            row += "  <- SOUTH (visual)"
        elif y == MAP_HEIGHT - 1:
            row += "  <- NORTH (visual)"
        print(row)

    print()
    print("  Key: * Rome start | O City (Bibracte, Vesontio, Genava)")
    print()


# ============================================================
# Main
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Gallic Wars Chapter 1 map")
    parser.add_argument("--preview", action="store_true", help="Print ASCII preview only")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    tiles = create_tiles()

    # Apply geography layers (order matters: later layers override earlier)
    apply_boundaries(tiles, rng)
    apply_base_terrain(tiles, rng)
    apply_provincia(tiles, rng)
    apply_aedui_heartland(tiles, rng)
    apply_sequani_territory(tiles, rng)
    apply_jura_mountains(tiles, rng)
    apply_vosges_mountains(tiles, rng)
    apply_alps(tiles, rng)
    apply_alsace_plain(tiles, rng)
    apply_rhine(tiles)
    apply_mediterranean(tiles, rng)  # after terrain zones so it carves coast
    apply_lake_geneva(tiles)
    apply_saone_floodplain(tiles, rng)
    apply_rivers(tiles)
    apply_special_tiles(tiles)
    apply_resources(tiles, rng)

    if args.preview:
        print_preview(tiles)
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(project_dir, "GallicWars", "Maps", "GallicWars1Map.xml")

    write_xml(tiles, output_path)
    print_preview(tiles)


if __name__ == "__main__":
    main()

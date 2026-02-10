# River Placement in Old World Hex Maps

Reference for manually placing rivers in the terrain XML (`data/base_terrain.xml`).

## River XML Tags

Only three river tags exist per tile:

| Tag | Edge | Vertices | Visual |
|-----|------|----------|--------|
| `RiverW` | West (left) | V_NW ↔ V_SW | Vertical segment on left side |
| `RiverSW` | Southwest | V_SW ↔ V_S | Angled segment, lower-left |
| `RiverSE` | Southeast | V_S ↔ V_SE | Angled segment, lower-right |

There are no `RiverE`, `RiverNE`, or `RiverNW` tags. The east, northeast, and northwest edges of a tile are represented by the W, SW, and SE edges of their respective neighbors.

The value (e.g., `<RiverW>0</RiverW>`) is a `RotationType` enum that controls **river flow direction**:

| Value | Enum | Meaning |
|-------|------|---------|
| (absent) | `NONE` (-1) | No river on this edge |
| `0` | `CLOCKWISE` | Water flows in one direction along the edge |
| `1` | `COUNTER_CLOCKWISE` | Water flows in the opposite direction |

The rotation determines which end of the river renders as a **source** (spring) vs **mouth** (delta). See [Flow Direction](#flow-direction-rotation-values) below for the full mapping.

## Hex Geometry (Pointy-Top, Odd-Row-Right)

Each hex has 6 vertices and 6 edges:

```
        V_N
       /    \
    V_NW    V_NE
     |        |
    V_SW    V_SE
       \    /
        V_S
```

The three available river edges cover the left and bottom of each hex:

```
        V_N
       /    \
   V_NW      V_NE
     |W        |
   V_SW      V_SE
      \SW  SE/
        V_S
```

The right and top edges (E, NE, NW) are the W, SW, SE edges of neighboring tiles.

## Connectivity Rule

**River edges must share a vertex to render as a connected river.** Edges that don't share a vertex render as disconnected waterfalls/springs.

On a single tile, the shared vertices are:
- **RiverW ↔ RiverSW**: share V_SW
- **RiverSW ↔ RiverSE**: share V_S
- **RiverW ↔ RiverSE**: NO shared vertex (opposite sides of hex)

Between adjacent tiles in the same row:
- **V_SE(x,y) = V_SW(x+1,y)** — the lower boundary between two horizontally adjacent hexes

## Common River Patterns

### East-Flowing River (Along Row Boundary)

Use **RiverSW + RiverSE** on each tile in the row:

```
Tile (x,y):    SW(V_SW→V_S) + SE(V_S→V_SE)    share V_S ✓
Tile (x+1,y):  SW(V_SW→V_S) + SE(V_S→V_SE)    share V_S ✓
Between tiles:  V_SE(x) = V_SW(x+1)             ✓ connected
```

The river zigzags along the boundary between row y and row y+1.

**NEVER use consecutive RiverW across a row.** RiverW on (x,y) and RiverW on (x+1,y) sit on opposite sides of the hex between them — they create disconnected parallel vertical segments (waterfalls).

### South-Flowing River (North to South)

The standard pattern from the Imperium Romanum data uses **RiverSE + RiverW** pairs:

```
Tile (x,y):    RiverSE  — goes to SE neighbor
Tile (x+1,y+1): RiverW  — W edge connects back
```

The SE edge of one tile connects to the W edge of the tile below-right via shared vertex V_SE.

### Bridging North→East (Turning a Corner)

To redirect a southward-flowing river into an east-flowing chain, the bridging tile needs edges that connect the incoming direction to the outgoing direction. Use **RiverW + RiverSW + RiverSE**:

- RiverW (V_NW↔V_SW): catches the incoming river from the north/NW
- RiverSW (V_SW↔V_S): bridges W to SE via V_SW
- RiverSE (V_S↔V_SE): exits east to V_SE = V_SW of next tile

Note: three edges on one tile makes the river wrap around it. Sometimes it's cleaner to split the turn across two tiles — experiment and check visually.

### Junction Considerations

When two river branches meet, be careful with RiverSE — it can create unwanted visual connections to the SE neighbor tile, appearing as a waterfall toward an unintended area. If you see an unwanted edge, check whether RiverSE on the junction tile is pointing somewhere unexpected and remove it.

## Neighbor Lookup (Odd-Row-Right)

River edges connect to specific neighbors depending on row parity:

| Direction | Even row (y%2=0) | Odd row (y%2=1) |
|-----------|-----------------|-----------------|
| W | (x-1, y) | (x-1, y) |
| E | (x+1, y) | (x+1, y) |
| NW | (x-1, y-1) | (x, y-1) |
| NE | (x, y-1) | (x+1, y-1) |
| SW | (x-1, y+1) | (x, y+1) |
| SE | (x, y+1) | (x+1, y+1) |

This means:
- `RiverSW` on even-row tile (x,y) borders **(x-1, y+1)**
- `RiverSW` on odd-row tile (x,y) borders **(x, y+1)**
- `RiverSE` on even-row tile (x,y) borders **(x, y+1)**
- `RiverSE` on odd-row tile (x,y) borders **(x+1, y+1)**

## Row Insertion Parity Rule

When inserting rows (`insert_rows.py`), the count **must be even**. An odd row shift flips even/odd row alignment, which changes which neighbors RiverSW and RiverSE connect to — breaking every river connection in the shifted region.

Column insertion (`insert_columns.py`) has **no parity requirement**.

## Flow Direction (Rotation Values)

River values are `RotationType` enums (from `Enums.cs`). The game uses these to determine water flow direction along each edge, which controls source/mouth rendering. The function `GetFlowInTile()` in `DefaultMapScript.cs` returns the **upstream tile** for each edge+rotation combination.

Each edge connects two hex vertices. The rotation determines which vertex is upstream (where water comes FROM) and which is downstream (where water flows TO).

### RiverW (West edge) — upper-left ↔ lower-left vertices

| Value | Upstream vertex | Downstream vertex | Water flows |
|-------|----------------|-------------------|-------------|
| **0** (CW) | upper-left (NW side) | lower-left (SW side) | ↓ southward |
| **1** (CCW) | lower-left (SW side) | upper-left (NW side) | ↑ northward |

### RiverSW (Southwest edge) — lower-left ↔ bottom vertices

| Value | Upstream vertex | Downstream vertex | Water flows |
|-------|----------------|-------------------|-------------|
| **0** (CW) | lower-left (W side) | bottom (SE side) | ↘ southeastward |
| **1** (CCW) | bottom (SE side) | lower-left (W side) | ↖ northwestward |

### RiverSE (Southeast edge) — bottom ↔ lower-right vertices

| Value | Upstream vertex | Downstream vertex | Water flows |
|-------|----------------|-------------------|-------------|
| **0** (CW) | bottom (SW side) | lower-right (E side) | ↗ northeastward |
| **1** (CCW) | lower-right (E side) | bottom (SW side) | ↙ southwestward |

### Upstream Neighbor Lookup (GetFlowInTile)

The practical way to determine the correct rotation value: **check which neighbor tile should be upstream** using this table, then pick the rotation that makes that neighbor the upstream tile.

| Edge | Value 0 (CW) upstream = | Value 1 (CCW) upstream = |
|------|-------------------------|--------------------------|
| **W** | NW neighbor | SW neighbor |
| **SW** | W neighbor | SE neighbor |
| **SE** | SW neighbor | E neighbor |

Use the [Neighbor Lookup table](#neighbor-lookup-odd-row-right) to resolve NW/SW/SE/E to actual (x,y) coordinates based on row parity.

**Procedure for each edge:**
1. Identify which neighbor should be upstream (closer to river source)
2. Look up the neighbor direction in the table above
3. Set the rotation value that puts that direction as upstream

### Source and Mouth Rendering

The game traces river flow using rotation values to determine direction. At dead ends:
- The **upstream** dead end renders as `RIVERPIECEV2_START_LAND` (rocky spring)
- The **downstream** dead end renders as `RIVERPIECEV2_END_COAST` or `RIVERPIECEV2_END_LAKE` (delta/mouth)

If a river source looks like a mouth (or vice versa), the rotation values are pointing the wrong way.

**Important:** The correct rotation value for each tile depends on row parity (even/odd rows have different neighbors). There is no blanket rule like "always use 0" or "always use 1." Each tile must be evaluated individually. In practice, tune values experimentally with in-game visual verification.

### Source Code Reference

- `RotationType` enum: `Enums.cs:1249` — `NONE=-1, CLOCKWISE=0, COUNTER_CLOCKWISE=1`
- `GetFlowInTile()`: `DefaultMapScript.cs:5150` — maps edge+rotation to upstream tile
- `TileData` fields: `TileData.cs:24-26` — `meRiverW`, `meRiverSW`, `meRiverSE`
- River pieces: `riverPieceV2.xml` — `START_LAND`, `END_COAST`, `END_LAKE`, `CURVE_1`–`CURVE_9`

## Debugging Tips

1. **Waterfalls/springs** = disconnected edges. Check that adjacent edges share a vertex.
2. **River on wrong boundary** = check neighbor lookup table for the row's parity.
3. **Invisible river** = tile might have `RiverW=0` which is valid (river index 0), not "no river". Use absence of the tag for no river.
4. **Visual surprises at junctions** = RiverSE often points to an unexpected neighbor. Remove it and re-check.
5. **Always verify in-game** — vertex math gets you close, but the renderer can surprise you. Iterate with screenshots.

# The Gallic Wars - Old World Scenario Mod

A scenario campaign mod for Old World based on Caesar's *Commentarii de Bello Gallico*. The player controls Rome as Julius Caesar. Chapter 1 (58 BCE) covers the Helvetii migration and Ariovistus campaigns.

## Project Layout

```
GallicWars/              # The mod (deployed to Old World's Mods directory)
  ModInfo.xml            # Mod manifest (scenario=true)
  Infos/                 # XML data: scenario, scenarioClass, tribe, unit, text, genderedText
  Maps/                  # Map XML files (generated)
data/
  base_terrain.xml       # Authored terrain data (frozen from Imperium Romanum, now editable)
scripts/
  generate_scenario.py   # Reads frozen terrain, generates scenario map
  freeze_terrain.py      # One-time: extract + freeze terrain from Imperium Romanum
  deploy.sh              # Copies mod to game's Mods path
  screenshot_map.sh      # Automated in-game screenshot tool
docs/                    # Design docs, milestones, modding reference
Reference/               # Symlink to game's XML (for looking up base game data)
```

## Build & Test Workflow

1. `python3 scripts/generate_scenario.py` - generate scenario map from frozen terrain
2. `./scripts/deploy.sh` - copy mod to game's Mods directory
3. Check logs: `~/Library/Logs/MohawkGames/OldWorld/Player.log`

To re-extract terrain from Imperium Romanum (one-time, rarely needed):
`python3 scripts/freeze_terrain.py` - writes `data/base_terrain.xml`

Requires `.env` with `OLDWORLD_MODS_PATH` set (see `.env.example`).

## Critical Rules

- **preload-text-add.xml MUST have UTF-8 BOM** (EF BB BF). Game silently ignores text without it.
- **NEVER add text keys that already exist in base game** - causes crash. Always check `Reference/XML/Infos/text-*.xml` first.
- **Map XML must have UTF-8 BOM** (`encoding='utf-8-sig'` in Python) and `MapEdgesSafe="True"`.
- Mod files use `-add.xml` suffix (additive modding).
- `<zModName>` in scenario XML must match the mod folder name exactly: `GallicWars`.
- `<zMapFile>` is without file extension: `GallicWars1Map` (not `GallicWars1Map.xml`).
- **scenario-add.xml MUST have `<Difficulty>` or `<DifficultyDisabled>`** - without this, the game skips loading the mod's Maps directory entirely.
- **TribeDiplomacy in save-format maps must list ALL tribes** - empty `<TribeDiplomacy />` causes NullReferenceException at startup.
- **Deploy with clean target** - `rm -rf` the deployed mod directory before `cp -r`, since `cp -r` doesn't remove stale files.
- **Row shifts must be even** - Inserting/deleting an odd number of rows flips hex row parity, breaking all river edges (RiverSW/RiverSE) in the shifted region. This applies to `insert_rows.py --count`, `freeze_terrain.py` Y-offset, and any future row operations.

## Map

Terrain is authored in `data/base_terrain.xml` (originally extracted from the Imperium Romanum map, now independent). The scenario generator reads this file and layers game state on top.

- Dimensions: 23 x 29 = 667 tiles (editable — change MapWidth and add/remove tiles)
- Terrain fields: Terrain, Height, Vegetation, Resource, Road, Rivers, ElementName, CitySite, Improvement
- Boundary tiles computed by the generator (outer 2 rows/columns)
- Output uses scenario/save-file format with Game/Player/Character/City blocks and embedded units

## Current Milestone

See `docs/milestones.md` for full roadmap. Milestones 1-3 complete. Currently working on Milestone 4 (scenario gameplay).

## Key Docs

- `docs/gallic-wars-scenario-design.md` - Full scenario design: narrative events, tribes, characters, goals, victory tiers
- `docs/modding-lessons-learned.md` - XML format rules, event system patterns, debugging tips
- `docs/modding-guide.md` - C# modding reference (GameFactory, Harmony)
- `docs/save-file-format.md` - Scenario/save-file XML format reference
- `docs/milestones.md` - Project milestones and status

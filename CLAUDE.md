# The Gallic Wars - Old World Scenario Mod

A scenario campaign mod for Old World based on Caesar's *Commentarii de Bello Gallico*. The player controls Rome as Julius Caesar. Chapter 1 (58 BC) covers the Helvetii migration and Ariovistus campaigns.

## Project Layout

```
GallicWars/              # The mod (deployed to Old World's Mods directory)
  ModInfo.xml            # Mod manifest (scenario=true)
  Infos/                 # XML data: scenario, scenarioClass, text
  Maps/                  # Map XML files
scripts/
  extract_map.py         # Extracts map region from Imperium Romanum
  deploy.sh              # Copies mod to game's Mods path
  generate_map.py        # DEPRECATED - old procedural map generator
  screenshot_map.sh      # Automated in-game screenshot tool
docs/                    # Design docs, milestones, modding reference
Reference/               # Symlink to game's XML (for looking up base game data)
```

## Build & Test Workflow

1. `python3 scripts/extract_map.py` - extract map from Imperium Romanum
2. `./scripts/deploy.sh` - copy mod to game's Mods directory
3. **Full app restart required** - in-game restart does NOT reload map files
4. Check logs: `~/Library/Logs/MohawkGames/OldWorld/Player.log`

Requires `.env` with `OLDWORLD_MODS_PATH` set (see `.env.example`).

## Critical Rules

- **preload-text-add.xml MUST have UTF-8 BOM** (EF BB BF). Game silently ignores text without it.
- **NEVER add text keys that already exist in base game** - causes crash. Always check `Reference/XML/Infos/text-*.xml` first.
- **Map extraction Y-offset must be EVEN** to preserve hex row parity. Odd-row-right hex grids flip neighbor geometry on odd Y shifts, breaking rivers and terrain adjacency.
- **Map XML must have UTF-8 BOM** (`encoding='utf-8-sig'` in Python) and `MapEdgesSafe="True"`.
- Mod files use `-add.xml` suffix (additive modding).
- `<zModName>` in scenario XML must match the mod folder name exactly: `GallicWars`.
- `<zMapFile>` is without file extension: `GallicWars1Map` (not `GallicWars1Map.xml`).
- **scenario-add.xml MUST have `<Difficulty>` or `<DifficultyDisabled>`** - without this, the game skips loading the mod's Maps directory entirely.
- **TribeDiplomacy in save-format maps must list ALL tribes** - empty `<TribeDiplomacy />` causes NullReferenceException at startup.
- **Deploy with clean target** - `rm -rf` the deployed mod directory before `cp -r`, since `cp -r` doesn't remove stale files.

## Map

Extracted from the Imperium Romanum map (127x105 tiles). Source at:
`~/Library/Application Support/Steam/steamapps/common/Old World/Maps/The Imperium Romanum.xml`

- Extraction region: x=[20,42], y=[58,86] -> 23 x 29 = 667 tiles
- Tiles copied 1:1 with remapped IDs, outer 2 rows/columns marked as boundaries
- Dropped fields: Metadata, TribeSite (Improvement and Road preserved)
- Map uses scenario/save-file format with Game/Player/Character/City blocks and embedded units

## Current Milestone

See `docs/milestones.md` for full roadmap. Milestones 1-2 (MVP scenario + accurate map) are complete. Currently working on Milestone 3 (map customization).

## Key Docs

- `docs/gallic-wars-scenario-design.md` - Full scenario design: narrative events, tribes, characters, goals, victory tiers
- `docs/modding-lessons-learned.md` - XML format rules, event system patterns, debugging tips
- `docs/modding-guide.md` - C# modding reference (GameFactory, Harmony)
- `docs/milestones.md` - Project milestones and status

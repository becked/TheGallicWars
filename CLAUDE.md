# The Gallic Wars - Old World Scenario Mod

A scenario campaign mod for Old World based on Caesar's *Commentarii de Bello Gallico*. The player controls Rome as Julius Caesar. Book I (58 BCE) covers the Helvetii migration and Ariovistus campaigns.

**Current state**: v2 rebuild in progress. v1 is archived under `archive/v1/` for reference. Scaffold smoke test passing — scenario loads, custom 4-day turn scale active, date display shows "Day {N} (58 BCE)".

## Project Layout

```
GallicWars/                  # The mod (deployed to Old World's Mods directory)
  ModInfo.xml                # scenario=true, requires WONDERS_DYNASTIES DLC (for Caesar dynasty)
  Maps/
    GallicWars1Map.xml       # 180x180 map, hand-edited via in-game editor
  Infos/
    scenario-add.xml         # SCENARIO_GALLIC_WARS_1 (Rome locked, DIFFICULTY_GREAT)
    scenarioClass-add.xml    # SCENARIOCLASS_GALLIC_WARS
    turnScale-add.xml        # TURNSCALE_GALLIC_4DAY (iDivisions=91)
    preload-text-add.xml     # Scenario name/sub/desc + turn scale labels (UTF-8 BOM)
    text-ui-change.xml       # Overrides TEXT_UI_TURN_TEXT_YEAR → "Day {0} (58 BCE)" (UTF-8 BOM)
archive/v1/                  # Stowed v1 mod, DLL source, generator scripts, v1 docs
docs/                        # Caesar source texts + general modding reference (event-design-lessons, modding-lessons-learned, modding-guide, river-placement, save-file-format, old-world-designer-notes)
images/                      # Generated event/scenario art (e.g. helvetii burn homeland)
Reference/                   # Symlink to game's XML/source (for looking up base game data)
```

## Build & Test Workflow

The map is authored directly in Old World's in-game map editor (saves to `~/Library/Application Support/OldWorld/Maps/`). To bring map updates into the mod and deploy:

1. Copy the editor's map file → `GallicWars/Maps/GallicWars1Map.xml`, preserving UTF-8 BOM
2. The map needs save-format scenario state (Game/Player/Character blocks) prepended before the `<Tile>` entries. v1's known-good scenario header was used as base; see `GallicWars/Maps/GallicWars1Map.xml` for the current pattern.
3. Clean-deploy to game Mods dir:
   ```
   rm -rf "$OLDWORLD_MODS_PATH/GallicWars"
   cp -R GallicWars "$OLDWORLD_MODS_PATH/"
   ```
4. Launch Old World → Scenarios → "The Helvetii Migration"
5. Check logs on failure: `~/Library/Logs/MohawkGames/OldWorld/Player.log`

Requires `.env` with `OLDWORLD_MODS_PATH` set (see `.env.example`).

No DLL or terrain-generator script in v2 yet — map is hand-edited, scenario state is hand-stitched. We may reintroduce a `generate_scenario.py`-style helper when we start procedurally placing cities/units.

## Critical Rules (still apply from v1)

- **preload-text-add.xml MUST have UTF-8 BOM** (EF BB BF). Game silently ignores text files without it. Same for **text-ui-change.xml** and map XML.
- **NEVER add text keys that already exist in base game** — causes crash. Always check `Reference/XML/Infos/text-*.xml` first.
- Mod files use `-add.xml` suffix (additive modding); `-change.xml` overrides existing entries.
- `<zModName>` in scenario XML must match the mod folder name exactly: `GallicWars`.
- `<zMapFile>` is without file extension: `GallicWars1Map` (not `.xml`).
- **scenario-add.xml MUST have `<Difficulty>` or `<DifficultyDisabled>`** — without it, the game skips loading the mod's Maps directory entirely.
- **TribeDiplomacy in save-format maps must list ALL tribes** — empty `<TribeDiplomacy />` causes NullReferenceException at startup.
- **Deploy with clean target** — `rm -rf` the deployed mod dir before `cp -R`, since `cp -R` doesn't remove stale files.
- **Row shifts must be even** — odd row shifts flip hex parity, breaking all RiverSW/RiverSE edges in the shifted region.

## Turn scale + date display

- Custom turn scales are defined in `turnScale-add.xml` (zType, ScaleSingular/Plural/Short text keys, iDivisions, bEnabled).
- iDivisions = turns per year. `TURNSCALE_GALLIC_4DAY` uses 91 (≈ 365/4 four-day weeks per year).
- The end-turn button uses `ScaleSingular` ("End Turn" if the singular is "Turn").
- Date display: override `TEXT_UI_TURN_TEXT_YEAR` in `text-ui-change.xml`.
- **For base-game default UI (no custom ClientUI class), placeholders are: `{0}` = turn number, `{1}` = iMaxTurns** (per `Reference/Source/Base/Game/ClientCore/ClientUI.cs:22130`).
- Some shipped scenarios (Carthage, Greece6) define custom ClientUI classes with different parameter orders — **do not assume their `text-ui-change.xml` placeholder order applies to a no-code mod**.

## Map

180 × 180 = 32,400 tiles, covering all of Gaul + Britain + Belgica + adjacent Germania. Hand-authored in the in-game map editor.

- Geography is real: Narbo at (90, 18) south coast, Lutetia at (85, 99) north, Massalia (122, 20), Aventicum *not placed* (Helvetii burned all twelve oppida pre-scenario per Caesar Book 1 ch. 5)
- Approximate projection: 12 tiles per degree longitude, 14 per degree latitude
- y=0 is SOUTH (Mediterranean), increasing y = NORTH
- Coordinate of an urban tile: tileID = y * 180 + x

Urban tile placements and what they represent: see git history / conversation context. Cities, tribes, units, characters, and pre-placed ruins are layered on top via scenario XML — not part of the base map terrain.

## Current Milestone

**M0: Scaffold smoke test** — DONE. Scenario loads, custom 4-day turn scale active, date display works.

**M1: Cities + tribes + Caesar's starting forces** — next. Add named cities at existing urban tiles (per the list confirmed with the user), define Book 1 tribes (Helvetii as a moving force with no cities, Aedui, Sequani, Allobroges, Arverni, etc.), place Caesar + 1 legion + 2 workers at Genava (134, 59), set up the Vesontio (128, 76) + Burdigala (45, 42) + Samarobriva (81, 114) additions.

**M2: Opening event chain** — Caesar's arrival narration, 3-option bridge decision (burn bridge / retreat / declare war), fort-building + skirmish chain, auxiliary unit delivery events (Massalia slingers, Allobroges horse, Provincial levies).

**M3+**: Mid-book Helvetii pursuit, Bibracte, Aedui plea, Ariovistus campaign, Vesontio, Vosges. Then Books 2-8 as separate scenarios.

## Key Docs

- `docs/bellum-gallicum.txt`, `docs/1-the-helvetii-campaign.txt` — Caesar source text
- `docs/event-design-lessons.md` — what made/broke past events
- `docs/modding-lessons-learned.md` — XML format rules, event system patterns
- `docs/modding-guide.md` — C# modding reference (GameFactory, Harmony patterns)
- `docs/save-file-format.md` — scenario/save-file XML format reference
- `docs/river-placement.md` — hex river edge connectivity, vertex rules
- `docs/old-world-designer-notes/` — Mohawk Games designer essays (orders, city sites, citizens, events, diplomacy)
- `archive/v1/docs/` — v1-specific design docs (helvetii-event-proposals, gallic-wars-scenario-design, milestones, potential-roman-characters) — useful as reference but not authoritative for v2

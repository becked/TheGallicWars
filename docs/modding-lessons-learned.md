# Old World Modding Lessons Learned

Troubleshooting findings and hard-won knowledge from Old World modding. Originally from the Aristocratic Republic mod, expanded with lessons from The Gallic Wars scenario mod.

## Critical: UTF-8 BOM Required for Text Files

Text files (`text-*-add.xml`) **must** have a UTF-8 BOM (byte order mark: `ef bb bf`) at the start of the file. Without the BOM, the game silently fails to load the text and events won't fire.

**Symptom:** Events never fire, no errors in logs.

**Fix:** Add BOM to text files:
```bash
printf '\xef\xbb\xbf' > temp.xml && cat original.xml >> temp.xml && mv temp.xml original.xml
```

**Verify BOM exists:**
```bash
xxd yourfile.xml | head -1
# Should start with: efbb bf3c 3f78 6d6c
```

Note: `eventStory-add.xml` does NOT need a BOM, only text files.

## File Naming Conventions

| File Type | Correct Name | Notes |
|-----------|--------------|-------|
| Text strings | `text-new-add.xml` | `text-add.xml` does NOT work; needs UTF-8 BOM |
| Event stories | `eventStory-add.xml` | No BOM needed |
| Event bonuses | `bonus-event-add.xml` | No `encoding="utf-8"` in XML declaration |
| Family memories | `memory-family-add.xml` | |
| Event options | `eventOption-add.xml` | Only if using separate file (not recommended) |

## XML Format: Old vs New Syntax

The game supports two XML formats. Use the **new format** for reliability:

### New Format (Recommended)
```xml
<Subjects>
    <Subject alias="leader">
        <Type>SUBJECT_LEADER_US</Type>
    </Subject>
    <Subject alias="candidate">
        <Type>SUBJECT_FAMILY_HEAD_US</Type>
        <Extra>SUBJECT_ADULT</Extra>
        <Extra>SUBJECT_HEALTHY</Extra>
    </Subject>
</Subjects>
<EventOptions>
    <EventOption>
        <Text>TEXT_EVENTOPTION_EXAMPLE</Text>
    </EventOption>
</EventOptions>
```

### Old Format (Avoid)
```xml
<aeSubjects>
    <zValue>SUBJECT_LEADER_US</zValue>
    <zValue>SUBJECT_FAMILY_HEAD_US</zValue>
</aeSubjects>
<aeOptions>
    <zValue>EVENTOPTION_EXAMPLE</zValue>
</aeOptions>
```

## Text String Format

Use `<en-US>` tag for English text, **not** `<English>`:

```xml
<Entry>
    <zType>TEXT_EVENTSTORY_EXAMPLE</zType>
    <en-US>Your text here with {CHARACTER-0} references.</en-US>
</Entry>
```

## Character/Subject References in Text

Use **numeric indices** based on subject order, not alias names:

| Subject Index | Reference | Short Form |
|---------------|-----------|------------|
| 0 | `{CHARACTER-0}` | `{CHARACTER-SHORT-0}` |
| 1 | `{CHARACTER-1}` | `{CHARACTER-SHORT-1}` |
| 2 (if family) | `{FAMILY-2}` | - |

**Wrong:** `{leader:name}`, `{candidate}`
**Correct:** `{CHARACTER-0}`, `{CHARACTER-1}`

## Event Triggers

### The Trigger=NONE Problem

Events without an explicit `<Trigger>` element default to `EVENTTRIGGER_NONE`. These events go through a **random probability gate** based on event level:

| Event Level | Chance Per Turn |
|-------------|-----------------|
| High | 1/4 = 25% |
| Moderate | 1/6 = ~17% |
| Low | 1/8 = 12.5% |

**Symptom:** Event fires sporadically, not every turn as expected.

### Solution: Use Explicit Trigger

Add `<Trigger>EVENTTRIGGER_NEW_TURN</Trigger>` for reliable per-turn firing:

```xml
<Trigger>EVENTTRIGGER_NEW_TURN</Trigger>
<iMinTurns>1</iMinTurns>
<iPriority>10</iPriority>
<iWeight>10</iWeight>
<iProb>100</iProb>
<iRepeatTurns>2</iRepeatTurns>
```

`EVENTTRIGGER_NEW_TURN` has no probability gate - it fires every turn.

## Event Priority and Weight

| Field | Description | Recommended Value |
|-------|-------------|-------------------|
| `iPriority` | Higher beats lower; vanilla max is 9 | 10+ to beat vanilla |
| `iWeight` | Relative weight in lottery | 1-20 |
| `iProb` | % chance to enter pool (0 or 100 = always) | 100 |
| `iRepeatTurns` | Turns between firings; -1 = once ever | As needed |

## Conditional Event Options

Use `<IndexSubject>` to show/hide options based on subject conditions:

```xml
<EventOption>
    <Text>TEXT_EVENTOPTION_KEEP_LEADER</Text>
    <IndexSubject>
        <Pair>
            <First>2</First>  <!-- Subject index -->
            <Second>SUBJECT_FAMILY_MIN_PLEASED</Second>  <!-- Condition -->
        </Pair>
    </IndexSubject>
</EventOption>
```

This option only appears if subject at index 2 meets `SUBJECT_FAMILY_MIN_PLEASED`.

### Useful Family Opinion Subjects

| Subject | Meaning |
|---------|---------|
| `SUBJECT_FAMILY_MIN_PLEASED` | Pleased or better (positive) |
| `SUBJECT_FAMILY_MIN_CAUTIOUS` | Cautious or better (neutral+) |
| `SUBJECT_FAMILY_MAX_CAUTIOUS` | Cautious or worse (neutral-) |

## Debugging Tips

1. **Check logs:** `~/Library/Logs/OldWorld/Player.log`
2. **Verify mod loads:** Look for `[ModPath] Setting ModPath: .../YourMod/`
3. **No errors doesn't mean success:** The game silently ignores malformed XML
4. **Compare to working mods:** Philosophy of Science is a good reference
5. **Test incrementally:** Start with minimal event, add complexity gradually

## iSeizeThroneSubject (Leader Succession)

To make a character become the new leader via event:

1. Add `SUBJECT_PLAYER_US` as a subject (e.g., at index 0)
2. Create a bonus with `<iSeizeThroneSubject>0</iSeizeThroneSubject>` pointing to that player subject
3. Apply the bonus TO the character who should become leader (via `<SubjectBonuses>`)

```xml
<!-- In eventStory-add.xml -->
<Subjects>
    <Subject alias="player">
        <Type>SUBJECT_PLAYER_US</Type>
    </Subject>
    <Subject alias="candidate">
        <Type>SUBJECT_FAMILY_HEAD_US</Type>
    </Subject>
</Subjects>
<EventOptions>
    <EventOption>
        <SubjectBonuses>
            <Pair>
                <First>candidate</First>
                <Second>BONUS_SEIZE_THRONE</Second>
            </Pair>
        </SubjectBonuses>
    </EventOption>
</EventOptions>

<!-- In bonus-event-add.xml -->
<Entry>
    <zType>BONUS_SEIZE_THRONE</zType>
    <iSeizeThroneSubject>0</iSeizeThroneSubject>
</Entry>
```

**Key insight**: The bonus is applied to the Character (who becomes leader), while `iSeizeThroneSubject` points to the Player (whose throne is seized).

## Don't Mix Inline and Separate Event Options

When using inline `<EventOptions>` with `<SubjectBonuses>` in eventStory-add.xml, do NOT also define the same options in a separate eventOption-add.xml file. They can conflict.

- **Inline format** (recommended): Uses aliases like `<First>candidate</First>`
- **Separate file format** (old): Uses positional `<zValue>` elements where position = subject index

## Linking Subjects with Relations

Use `<Relations>` inside a Subject to link it to another subject. Useful for linking families to their candidates:

```xml
<Subjects>
    <Subject alias="candidate1">
        <Type>SUBJECT_FAMILY_HEAD_US</Type>
    </Subject>
    <Subject alias="family1">
        <Type>SUBJECT_FAMILY_US</Type>
        <Relations>
            <Relation>
                <Type>SUBJECTRELATION_FAMILY_SAME</Type>
                <Target>candidate1</Target>
            </Relation>
        </Relations>
    </Subject>
</Subjects>
```

This ensures `family1` is always the same family as `candidate1`.

## Ensuring Different Families (SubjectNotRelations)

To ensure multiple candidates come from different families, use `<SubjectNotRelations>` with `<Triple>`:

```xml
<SubjectNotRelations>
    <Triple><First>2</First><Second>SUBJECTRELATION_FAMILY_SAME</Second><Third>3</Third></Triple>
    <Triple><First>2</First><Second>SUBJECTRELATION_FAMILY_SAME</Second><Third>4</Third></Triple>
    <Triple><First>3</First><Second>SUBJECTRELATION_FAMILY_SAME</Second><Third>4</Third></Triple>
</SubjectNotRelations>
```

This prevents subjects at indices 2, 3, and 4 from being in the same family.

## Family Memory System (Opinion Changes)

To give the winner's family +20 opinion and other families -20:

1. Create two memories with different levels:
```xml
<Entry>
    <zType>MEMORYFAMILY_ELEVATED</zType>
    <MemoryLevel>MEMORYLEVEL_POS_MEDIUM_SHORT</MemoryLevel>
</Entry>
<Entry>
    <zType>MEMORYFAMILY_PASSED_OVER</zType>
    <MemoryLevel>MEMORYLEVEL_NEG_LOW_SHORT</MemoryLevel>
</Entry>
```

2. Apply both in the bonus:
```xml
<Entry>
    <zType>BONUS_ELECT</zType>
    <Memory>MEMORYFAMILY_ELEVATED</Memory>
    <MemoryAllFamilies>MEMORYFAMILY_PASSED_OVER</MemoryAllFamilies>
</Entry>
```

- `<Memory>` applies to the character's family (winner only)
- `<MemoryAllFamilies>` applies to ALL families

Net effect: Winner gets both (+X - Y), others get only (-Y).

## Shared Cooldown Between Events

To make multiple events share a cooldown (e.g., 15 election variants), use `aeEventStoryRepeatTurns` with **bidirectional linking**:

```xml
<!-- In EVENTSTORY_A -->
<aeEventStoryRepeatTurns>
    <zValue>EVENTSTORY_B</zValue>
    <zValue>EVENTSTORY_C</zValue>
</aeEventStoryRepeatTurns>

<!-- In EVENTSTORY_B -->
<aeEventStoryRepeatTurns>
    <zValue>EVENTSTORY_A</zValue>
    <zValue>EVENTSTORY_C</zValue>
</aeEventStoryRepeatTurns>

<!-- In EVENTSTORY_C -->
<aeEventStoryRepeatTurns>
    <zValue>EVENTSTORY_A</zValue>
    <zValue>EVENTSTORY_B</zValue>
</aeEventStoryRepeatTurns>
```

Each event must list all OTHER events. One-way linking does NOT work.

## Scenario Map Format (Save-File Format)

Scenario maps use the **same XML format as save files**. The game loads them via `initFromSaveFile()`. This means you need full Player, Character, City, and Game blocks — not just tiles.

### Required Blocks

A minimal scenario map needs (in order):
1. Root attributes (`MapWidth`, `MapEdgesSafe`, `Scenario`, etc.)
2. `<Team>`, `<Difficulty>`, `<Nation>`, `<Dynasty>` blocks
3. `<Game>` block (NextUnitID, NextCityID, NextCharacterID, TribeDiplomacy, FamilyClass, etc.)
4. `<Player>` blocks (nation, dynasty, resources, starting tiles)
5. `<Character>` blocks (leader, spouse, etc.)
6. `<City>` blocks (pre-founded cities with citizens, build queue)
7. `<Tile>` blocks (with `<Religion />` and `<RevealedTurn />` on every tile)
8. `<Unit>` blocks embedded inside their tile

### scenario-add.xml Must Have Difficulty

**CRITICAL**: `scenario-add.xml` MUST have `<Difficulty>` or `<DifficultyDisabled>` entries. Without these, `ScenarioSetupScreenPanel.OnScenarioChanged()` skips `UpdateScenarioMods()`, so the mod never gets added to active mods and the map file can't be found.

### TribeDiplomacy Must Be Complete

`<TribeDiplomacy>` in the Game block must list **ALL tribes × ALL players**. An empty `<TribeDiplomacy />` causes `NullReferenceException` in `calculateCharacterOpinionEthnicityTribe`.

Use `DIPLOMACY_WAR` for hostile system tribes (REBELS, ANARCHY, RAIDERS, BARBARIANS) and `DIPLOMACY_TRUCE` for others.

### StartingPlayerOptions Values Are Player Indices

`<StartingPlayerOptions>` values are **player indices**, not booleans. The C# code does:
```csharp
int.TryParse(pChildNode.InnerText, out int iPlayer);
lPlayerParameters[iPlayer].sePlayerOptions.Add(eOption);
```

For a single-player scenario, use `0`:
```xml
<StartingPlayerOptions>
  <PLAYEROPTION_NO_TUTORIAL>0</PLAYEROPTION_NO_TUTORIAL>
</StartingPlayerOptions>
```

Using `1` in a single-player map causes `ArgumentOutOfRangeException`.

### Valid Enum Values

- `DIFFICULTY_GREAT` (not `THE_GREAT`)
- `DEVELOPMENT_FLEDGLING` (not `DEVELOPING`)

### gameContentRequired

`gameContentRequired` in ModInfo.xml only enforces for internal (DLC) mods, not external user mods. Setting it has no practical effect.

## Map Extraction

### Y-Offset Must Be Even

When extracting a region from a source map, the Y-offset **must be even** to preserve hex row parity. Odd-row-right hex grids flip neighbor geometry on odd Y shifts, breaking rivers and terrain adjacency.

### Map XML Encoding

Map XML files must have:
- UTF-8 BOM (`encoding='utf-8-sig'` in Python)
- `MapEdgesSafe="True"` on the Root element

### River Tags

Only three river XML tags exist: `RiverW`, `RiverSW`, `RiverSE`. There are no `RiverNW`, `RiverNE`, or `RiverE` tags.

River connectivity: the game groups adjacent tiles with ANY river XML field (even `=0`) into connected rivers.

## City and Tile Knowledge

### City Names

The `<Name>` field in City blocks uses plain strings (`"Narbo"`) or `CITYNAME_*` enum IDs — **NOT** `TEXT_CITYNAME_*` text keys. The `CITYNAME_*` enums are defined in `cityName.xml`.

### Duplicate Text Keys Crash the Game

**NEVER add text keys that already exist in base game** — this causes a crash at load time. Always check `Reference/XML/Infos/text-*.xml` first. For example, `TEXT_CITYNAME_VESONTIO` already exists in the base game.

### Tribe-Owned Cities

Cities owned by tribes (not by a player) use `Player="-1"`, `Family="NONE"`, and `<Tribe>TRIBE_X</Tribe>` inside the City block.

### Removing a City Site

Removing a city site from a tile requires stripping four things:
1. `CitySite` tag
2. `IMPROVEMENT_CITY_SITE` improvement
3. `TERRAIN_URBAN` (change to `TERRAIN_LUSH` or appropriate terrain)
4. `ElementName` label

### Gendered Text for Tribes

Custom tribes need entries in both `preload-text-add.xml` and `genderedText-add.xml`. Each tribe needs 4 text entries (`TEXT_TRIBE_X`, `TEXT_TRIBE_X_F`, `TEXT_TRIBE_X_NICK`, `TEXT_TRIBE_X_NICK_F`) and 2 gendered text entries (`GENDERED_TEXT_TRIBE_X`, `GENDERED_TEXT_TRIBE_X_NICK`).

## Deployment

### Clean Target Before Deploying

`cp -r` doesn't remove stale files from the target. Always `rm -rf` the deployed mod directory before copying:
```bash
rm -rf "$TARGET" && cp -r "$SOURCE" "$TARGET"
```

### Full App Restart Required

In-game restart does **NOT** reload map files. A full quit-and-relaunch of Old World is required after deploying map changes.

### Keep .bak Files Out

`.bak` files in the mod directory get copied by deploy scripts. Keep backup files outside the mod directory.

## CRC Strict Mode Bug with Scenario Mods

External scenario mods that use `StrictModeDeferred` info types (goal, bonus, event, eventOption, eventStory, goalReq) cause a "Version mismatch" error when the scenario has `mzModName` set.

**Root cause**: `UpdateScenarioMods()` sets strict mode on the controller's `ModPath` when `mzModName` is non-empty. In strict mode, `ReadInfoListTypes` XORs deferred file CRCs but `ReadInfoListData` skips them, creating an asymmetric CRC. `AppMain.StartGame()` copies this non-zero CRC to the server **before** `Infos.PreCreateGame()` can fix it. PreCreateGame then updates the controller's CRC (via the reused Infos's internal `mModSettings` reference), but the server's copy is already stale.

**Workaround**: A Harmony postfix on `ModSettings.CreateServerGame` that re-copies the controller's (now-fixed) CRC to the server's `ModPath` after PreCreateGame runs. See `src/GallicWarsMod/` for implementation.

**Bug report**: https://gist.github.com/becked/f6f2c434762d18148e7d3ffe621d9c5d

Internal (DLC) mods are immune because they bypass `OpenModdedXML`/`AddCRC` entirely in `GetModdedXML`.

## Scenario Mods Cannot Be Manually Toggled

Mods with `<scenario>true</scenario>` in ModInfo.xml do not show an ON/OFF toggle in the mod browser. This means scenario mods cannot be manually enabled — they are only activated when a player selects the scenario from the scenario browser. This is relevant because it prevents using manual mod enablement as a workaround for the CRC strict mode bug above.

## DLL Placement

Mod DLLs must be placed in the mod root directory alongside `ModInfo.xml`. The game scans for `*.dll` files via `Directory.GetFiles(moddedPath, "*.dll", SearchOption.TopDirectoryOnly)` in `UserScriptManager.Initialize()`. DLLs in subdirectories are not found.

The DLL is loaded multiple times (controller, server, client). Use a static guard (`if (_harmony != null) return;`) to prevent duplicate Harmony patching.

## Common Pitfalls

1. **Missing BOM on text file** - Events silently fail
2. **Wrong text file name** - `text-add.xml` doesn't work, use `text-new-add.xml`
3. **Using `<English>` instead of `<en-US>`** - Text won't load
4. **Missing explicit trigger** - Event fires randomly instead of reliably
5. **Using alias names in text** - Use numeric indices like `{CHARACTER-0}`
6. **Extra directories in mod** - Can cause loading errors (keep only `Infos/`, `ModInfo.xml`, images)
7. **Mixing inline and separate event options** - Can cause bonuses to apply to wrong subjects
8. **One-way cooldown linking** - Must be bidirectional for shared cooldowns to work
9. **Duplicate text keys** - Adding a key that exists in base game crashes at load
10. **Empty TribeDiplomacy** - NullReferenceException at startup
11. **Missing Difficulty in scenario-add.xml** - Mod's Maps directory silently not loaded
12. **StartingPlayerOptions value = 1 in single-player** - ArgumentOutOfRangeException
13. **Odd Y-offset in map extraction** - Rivers and terrain adjacency break silently

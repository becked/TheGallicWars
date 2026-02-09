# Old World Game State XML Format

How Old World represents cities, units, characters, and tiles in XML. This format is shared between save files and scenario map files — they use the same structure.

## Top-Level Structure

```xml
<Root
  MapWidth="23"
  MapEdgesSafe="True"
  MapPath="GallicWars1Map"
  Scenario="SCENARIO_GALLIC_WARS_1"
  TurnScale="TURNSCALE_YEAR"
  ...>
  <Team> ... </Team>
  <Difficulty> ... </Difficulty>
  <Nation> ... </Nation>
  <Dynasty> ... </Dynasty>
  <Game> ... </Game>
  <Player ID="0"> ... </Player>
  <Character ID="0"> ... </Character>
  ...
  <City ID="0"> ... </City>
  <Tile ID="0"> ... </Tile>
  ...
</Root>
```

Order: Game globals, then Player(s), then Characters, then Cities, then Tiles (with Units embedded inside tiles).

## Player

```xml
<Player
  ID="0"
  Nation="NATION_ROME"
  Dynasty="DYNASTY_ROMULUS"
  AIControlledToTurn="0">
  <OriginalCapitalCityID>0</OriginalCapitalCityID>
  <FounderID>1</FounderID>
  <Legitimacy>16</Legitimacy>
  <StartingTileIDs>
    <Tile>98</Tile>   <!-- Narbo (capital) -->
    <Tile>240</Tile>
    <Tile>178</Tile>
    <Tile>371</Tile>
  </StartingTileIDs>
  <YieldStockpile>
    <YIELD_CIVICS>3000</YIELD_CIVICS>
    <YIELD_TRAINING>3000</YIELD_TRAINING>
    <YIELD_MONEY>300</YIELD_MONEY>
    <YIELD_ORDERS>70</YIELD_ORDERS>
    <YIELD_FOOD>2000</YIELD_FOOD>
    <YIELD_IRON>2000</YIELD_IRON>
    <YIELD_STONE>2000</YIELD_STONE>
    <YIELD_WOOD>2000</YIELD_WOOD>
  </YieldStockpile>
</Player>
```

- `StartingTileIDs` lists the NationSite tiles the game found on the map for this nation.
- `Dynasty` is what the user picked in the setup screen.
- Resources are the standard starting stockpile.

## Character

Characters are the dynasty leader, spouse, heirs, and family members.

```xml
<Character
  ID="0"
  BirthTurn="-21"
  Player="0"
  Character="CHARACTER_ROMULUS"
  Gender="GENDER_MALE"
  FirstName="NAME_ROMULUS"
  Seed="...">
  <Portrait>CHARACTER_PORTRAIT_ROMULUS</Portrait>
  <Level>1</Level>
  <MotherID>1</MotherID>
  <LeaderTurn>1</LeaderTurn>
  <Royal />
  <Nation>NATION_ROME</Nation>
  <Cognomen>COGNOMEN_FOUNDER</Cognomen>
  <Rating>
    <RATING_WISDOM>2</RATING_WISDOM>
    <RATING_CHARISMA>0</RATING_CHARISMA>
    <RATING_COURAGE>2</RATING_COURAGE>
    <RATING_DISCIPLINE>1</RATING_DISCIPLINE>
  </Rating>
  <TraitTurn>
    <TRAIT_HERO_ARCHETYPE>1</TRAIT_HERO_ARCHETYPE>
    <TRAIT_BOLD>1</TRAIT_BOLD>
  </TraitTurn>
</Character>
```

- `BirthTurn` is negative (born before game start). Value is relative to turn 0.
- `Character` field references a base game character type (e.g., CHARACTER_ROMULUS).
- `<Royal />` marks the character as part of the ruling dynasty.
- `<Family>FAMILY_CLAUDIUS</Family>` on non-royal characters assigns them to a family.
- Characters can have Traits, Cognomens, Ratings, Stats, and EventStoryTurn (tracks which events they've participated in).
- In this save, 6 characters were auto-generated: Romulus (leader), Ilia (mother/spouse), Remus (sibling), plus 3 family members (Sulpicia, Aulus, Marcus).

## City

```xml
<City
  ID="0"
  TileID="98"
  Player="0"
  Family="FAMILY_CLAUDIUS"
  Founded="1">
  <Name>Narbo</Name>
  <Citizens>3</Citizens>
  <Capital />
  <FirstPlayer>0</FirstPlayer>
  <LastPlayer>0</LastPlayer>
  <TeamCulture>
    <T.0>CULTURE_WEAK</T.0>
  </TeamCulture>
  <BuildQueue>
    <QueueInfo>
      <Build>BUILD_UNIT</Build>
      <Type>UNIT_SETTLER</Type>
      <Data>-1</Data>
      <Progress>320</Progress>
      <YieldCost>
        <YIELD_FOOD>100</YIELD_FOOD>
      </YieldCost>
    </QueueInfo>
  </BuildQueue>
</City>
```

- `TileID` references the tile where the city sits.
- `Founded` is the turn number the city was founded (1 = turn 1, manually settled by player).
- `<Capital />` marks this as the capital city (self-closing tag = boolean flag).
- `Family` assigns the city to a family (FAMILY_CLAUDIUS is Rome's default first family).
- City name came from the tile's `<ElementName>TEXT_CITYNAME_NARBO</ElementName>` label.
- `Citizens` starts at 3 for a new city.
- `BuildQueue` shows current production.

## Unit

Units are embedded inside their tile's XML block.

```xml
<Tile ID="75">
  ...
  <Unit
    ID="6"
    Type="UNIT_SCOUT"
    Player="0"
    Tribe="NONE"
    Seed="...">
    <CreateTurn>1</CreateTurn>
    <Facing>SW</Facing>
    <Gender>GENDER_FEMALE</Gender>
    <OriginalPlayer>0</OriginalPlayer>
    <RaidTurn />
    <PlayerFamily>
      <P.0>FAMILY_CLAUDIUS</P.0>
    </PlayerFamily>
    <QueueList />
    <AI />
  </Unit>
</Tile>
```

### Player Units (from starting setup)

| ID | Type | Notes |
|----|------|-------|
| 5 | UNIT_WORKER | Standard starting worker |
| 6 | UNIT_SCOUT | Standard starting scout |
| 7 | UNIT_WARRIOR | Standard starting military unit; has PromotionsAvailable |

- All have `Player="0"`, `Tribe="NONE"`, `CreateTurn=1`.
- `PlayerFamily` maps player IDs to family assignment.
- Units with available promotions list them in `<PromotionsAvailable>`.

### Barbarian Units

```xml
<Unit
  ID="2"
  Type="UNIT_SKIRMISHER_1"
  Player="-1"
  Tribe="TRIBE_BARBARIANS"
  Seed="...">
  <CreateTurn>1</CreateTurn>
  <OriginalTribe>TRIBE_BARBARIANS</OriginalTribe>
</Unit>
```

- `Player="-1"` indicates no player owns this unit (it's tribal).
- 4 barbarian UNIT_SKIRMISHER_1 units were auto-generated from TribeSite tiles.

## Tile (in save file context)

Tiles in the save file have more state than the map XML. The map defines static geography; the save adds runtime state.

```xml
<Tile ID="98">
  <Road />
  <Terrain>TERRAIN_URBAN</Terrain>
  <Height>HEIGHT_FLAT</Height>
  <RiverSW>1</RiverSW>
  <RiverSE>1</RiverSE>
  <CitySite>USED</CitySite>
  <TribeSite>TRIBE_BARBARIANS</TribeSite>
  <ElementName>TEXT_CITYNAME_NARBO</ElementName>
  <InitSeed>...</InitSeed>
  <TurnSeed>...</TurnSeed>
  <RevealedCityTerritory>...</RevealedCityTerritory>
  <WasVisibleThisTurn>...</WasVisibleThisTurn>
  <Revealed>...</Revealed>
  <RevealedCity>...</RevealedCity>
  <RevealedRoad>...</RevealedRoad>
  <Religion />
  <RevealedTerrain>...</RevealedTerrain>
  <RevealedHeight>...</RevealedHeight>
</Tile>
```

### CitySite States

| State | Meaning |
|-------|---------|
| `ACTIVE` | Available city site (no one has settled here) |
| `ACTIVE_RESERVED` | Reserved for a specific player/nation (from NationSite on the map) |
| `USED` | City has been built here |

- In our save, tile 98 (Narbo) is `USED` because the player settled it.
- Tiles 178, 371 are `ACTIVE_RESERVED` (other NationSite tiles for Rome that weren't settled yet).
- Other city sites (208, 411, 423, 543, 579) are `ACTIVE` (unclaimed, available to anyone).

### Save-Only Fields (not in scenario maps)

- `<InitSeed>`, `<TurnSeed>` - random seeds (game generates these at load time)

### Fields Present in Both Saves and Scenario Maps

- `<Road />` - boolean, road built on tile
- `<Religion />` - religion state (empty = none)
- `<RevealedTurn />` - usually empty
- `<Revealed>`, `<RevealedTerrain>`, `<RevealedHeight>`, etc. - fog of war per team (only on revealed tiles)
- `<WasVisibleThisTurn>` - visibility tracking (only on visible tiles)
- `<RevealedCityTerritory>` - which team knows about city borders
- `<CityTerritory>0</CityTerritory>` - tile belongs to city ID 0

## Map Labels (ElementName)

Labels from the Imperium Romanum map are preserved and rendered in-game:

| ElementName | Type |
|-------------|------|
| TEXT_CITYNAME_NARBO | City name |
| TEXT_CITYNAME_LUGDUNUM | City name |
| TEXT_CITYNAME_BURDIGALA | City name |
| TEXT_CITYNAME_GENOA | City name |
| TEXT_CITYNAME_CAESARODUNUM | City name |
| TEXT_CITYNAME_COLONIA | City name |
| TEXT_CITYNAME_LONDINIUM | City name |
| TEXT_CITYNAME_AUGUSTA_VINDELICORUM | City name |
| TEXT_CITYNAME_DUROCRTORUM | City name |
| TEXT_RHODANUS_RIVER | River label |
| TEXT_RHENUS_RIVER | River label |
| TEXT_IBERUS_RIVER | River label |
| TEXT_LIGERA_RIVER | River label |
| TEXT_PADUS_RIVER | River label |
| TEXT_SEQUANA_RIVER | River label |
| TEXT_TARNIS_RIVER | River label |
| TEXT_TAMESIS_RIVER | River label |
| TEXT_ALBIS_RIVER | River label |
| TEXT_GALLIA | Region label (appears 3x) |
| TEXT_ALPES | Region label (appears 3x) |
| TEXT_ITALIA | Region label |
| TEXT_PYRENEES | Region label |
| TEXT_BELGICA | Region label |
| TEXT_RAETIA | Region label |
| TEXT_GERMANIA | Region label |

## Bare Map vs Scenario Map

Official scenario maps (Greece1, Egypt1, etc.) use the **same XML format as save files**. They are not simplified — they include full Player, Character, City, and Tile blocks with complete game state. The game loads them as if loading a save.

### Comparison

| Aspect | Bare Tile-Only Map (ours) | Scenario Map (Greece1, Egypt1) |
|--------|--------------------------|-------------------------------|
| Root attributes | `MapWidth`, `MapEdgesSafe` only | Full metadata: `Scenario`, `GameId`, `MapSize`, `Version`, game settings |
| `<Game>` block | None | Present with `NextUnitID`, `NextCityID`, `NextCharacterID`, seeds, yield prices |
| `<Player>` blocks | None | Full player definitions with nation, dynasty, resources, starting tiles |
| `<Character>` blocks | None | Full character definitions with traits, ratings, family lineage, cognomens |
| `<City>` blocks | None | Full city definitions with citizens, culture, build queues, governors, religion |
| `<Unit>` blocks | None | Pre-placed inside Tile blocks (same as save files) |
| Tile fields | Minimal (terrain, height, rivers, resources) | Adds `<Religion />`, `<RevealedTurn />`, plus revelation state on visible tiles |
| Tile seeds | None | None — `InitSeed`/`TurnSeed` are save-only; game generates them at load |
| File size | ~700 lines (667 tiles) | 58K-117K lines |
| How cities start | Game auto-generates from NationSite | Pre-placed as City blocks with full state |

### Example: Egypt1 Pre-Placed City

```xml
<City
  ID="0"
  TileID="4256"
  Player="0"
  Family="FAMILY_THEBES"
  Founded="1">
  <Name>CITYNAME_EG_MENNEFER</Name>
  <Citizens>2</Citizens>
  <Capital />
  <FirstPlayer>0</FirstPlayer>
  <LastPlayer>0</LastPlayer>
  <YieldProgress />
  <YieldOverflow />
  <ProjectCount />
  <LuxuryTurn />
  <AgentTurn />
  <AgentCharacterID />
  <AgentTileID />
  <TeamCultureStep />
  <TeamDiscontentLevel />
  <Religion />
  <PlayerFamily>
    <P.0>FAMILY_THEBES</P.0>
  </PlayerFamily>
  <TeamCulture>
    <T.0>CULTURE_WEAK</T.0>
  </TeamCulture>
  <BuildQueue>
    <QueueInfo>
      <Build>BUILD_PROJECT</Build>
      <Type>PROJECT_COUNCIL_1</Type>
      <Data>-1</Data>
      <Progress>0</Progress>
      <Repeat />
      <YieldCost />
    </QueueInfo>
  </BuildQueue>
</City>
```

### Example: Egypt1 Pre-Placed Character

```xml
<Character
  ID="0"
  BirthTurn="-72"
  Player="0"
  Character="CHARACTER_AHMOSE"
  Gender="GENDER_MALE"
  FirstName="NAME_THEBES_AHMOSE"
  Seed="28853994927302115">
  <Title>TITLE_THEBES</Title>
  <Portrait>CHARACTER_PORTRAIT_AHMOSE</Portrait>
  <Level>1</Level>
  <LeaderTurn>1</LeaderTurn>
  <FatherID>16</FatherID>
  <BirthFatherID>16</BirthFatherID>
  <Royal />
  <Nation>NATION_THEBES</Nation>
  <Cognomen>COGNOMEN_GOOD</Cognomen>
  <Family>FAMILY_THEBES</Family>
  <Rating>
    <RATING_WISDOM>5</RATING_WISDOM>
    <RATING_CHARISMA>0</RATING_CHARISMA>
    <RATING_COURAGE>-1</RATING_COURAGE>
    <RATING_DISCIPLINE>1</RATING_DISCIPLINE>
  </Rating>
  <Stat />
  <Trait>
    <TRAIT_TACTICIAN_ARCHETYPE />
    <TRAIT_HUMBLE />
  </Trait>
</Character>
```

## Scenario Map Tile Structure

Most tiles in scenario maps are lean — just the geographic data plus two empty tags:

```xml
<Tile
  ID="1797">
  <Boundary />
  <Terrain>TERRAIN_LUSH</Terrain>
  <Height>HEIGHT_FLAT</Height>
  <Religion />
  <RevealedTurn />
</Tile>
```

This is nearly identical to our bare map tiles. The `<Religion />` and `<RevealedTurn />` tags are present on every tile but usually empty.

Tiles only get heavier when they have cities, improvements, or are revealed to a team:

```xml
<Tile
  ID="902">
  <Road />
  <Terrain>TERRAIN_URBAN</Terrain>
  <Height>HEIGHT_FLAT</Height>
  <CitySite>USED</CitySite>
  <TribeSite>TRIBE_BARBARIANS</TribeSite>
  <Revealed>
    <Team>1</Team>
  </Revealed>
  <RevealedCity>
    <Team>1</Team>
  </RevealedCity>
  <RevealedRoad>
    <Team>1</Team>
  </RevealedRoad>
  <Religion />
  <RevealedTerrain>
    <Team Terrain="TERRAIN_URBAN">1</Team>
  </RevealedTerrain>
  <Unit
    ID="0"
    Type="UNIT_SHORTBOWMAN"
    Player="2"
    Tribe="NONE"
    Seed="3761063787422445813">
    <CreateTurn>1</CreateTurn>
    <Facing>SW</Facing>
    <Gender>GENDER_FEMALE</Gender>
    <RaidTurn />
    <PlayerFamily>
      <P.2>FAMILY_KUSH</P.2>
    </PlayerFamily>
  </Unit>
</Tile>
```

### Fields Present on Every Tile (scenario maps)

| Field | Notes |
|-------|-------|
| `Terrain` | Always present |
| `Height` | Always present |
| `Religion` | Always present, usually empty (`<Religion />`) |
| `RevealedTurn` | Always present, usually empty (`<RevealedTurn />`) |

### Fields Present Only When Applicable

| Field | When present |
|-------|-------------|
| `Boundary` | Edge tiles only |
| `Road` | Tiles with roads |
| `RiverW`, `RiverSW`, `RiverSE` | River edges |
| `Vegetation` | Tiles with trees/forest |
| `Resource` | Tiles with resources |
| `Improvement` | Tiles with improvements (farms, mines, settlements) |
| `ImprovementDevelopTurns` | If improvement present |
| `ImprovementUnitTurns` | If improvement present |
| `CitySite` | City locations (ACTIVE, ACTIVE_RESERVED, USED) |
| `TribeSite` | Tribal camp locations |
| `NationSite` | Bare maps only — not used in scenario maps |
| `ElementName` | Map labels (city names, river names, region names) |
| `CityTerritory` | Tiles owned by a city |
| `Revealed`, `RevealedTerrain`, etc. | Tiles visible to a team |
| `Unit` | Units on this tile (embedded block, not self-closing) |

### Save-Only Fields (NOT in scenario maps)

| Field | Notes |
|-------|-------|
| `InitSeed` | Generated at load time |
| `TurnSeed` | Generated at load time |

## Key Implications for Our Scenario

1. **To pre-found Narbo**: We need to convert our bare map into a scenario map — add Player, Character, City, and Game blocks, matching the format used by Egypt1/Greece1. The map file effectively becomes a save file that the game loads as the starting state.

2. **NationSite vs City block**: In a bare map, `<NationSite>` tells the game where to auto-generate a starting position. In a scenario map, you skip NationSite entirely and place a `<City>` block directly. The tile gets `<CitySite>USED</CitySite>` instead.

3. **Units ARE pre-placed**: Units are embedded inside Tile blocks in scenario maps, same format as save files. Both player units and tribal units can be pre-placed.

4. **Minimal tile overhead**: Most tiles only need `<Religion />` and `<RevealedTurn />` added to our existing data. The file size increase comes mainly from the Player/Character/City/Game blocks and revelation state on visible tiles — not from per-tile seeds.

5. **Auto-generated TribeSites**: Even though we dropped TribeSite from extraction, the game generated TRIBE_BARBARIANS sites across the map. The game populates empty maps with barbarian sites automatically.

6. **City names from ElementName**: When settling on a tile with `<ElementName>TEXT_CITYNAME_*</ElementName>`, the game uses that label as the default city name. This is how Narbo got its name automatically.

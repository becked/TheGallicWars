#!/usr/bin/env python3
"""
Extract a rectangular region from the Imperium Romanum map and generate
a complete scenario map file for the Gallic Wars scenario.

Reads the source map XML, extracts tiles in the specified x,y range,
remaps tile IDs to the new grid, marks edge tiles as boundary, and wraps
everything in the scenario map format (Game/Player/Character/City blocks
plus units embedded in tiles).

Usage:
    python scripts/extract_map.py
    # Writes to GallicWars/Maps/GallicWars1Map.xml
"""

import re
import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# Extraction Parameters
# ============================================================

SOURCE_MAP = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/Old World"
    "/Maps/The Imperium Romanum.xml"
)
SOURCE_WIDTH = 127

# Extraction region (inclusive). Y-offset MUST be even for hex parity.
SRC_X_MIN = 20
SRC_X_MAX = 42
SRC_Y_MIN = 58
SRC_Y_MAX = 86

NEW_WIDTH = SRC_X_MAX - SRC_X_MIN + 1   # 23
NEW_HEIGHT = SRC_Y_MAX - SRC_Y_MIN + 1  # 29

# ============================================================
# Scenario Constants
# ============================================================

NARBO_X = 6
NARBO_Y = 4
NARBO_TILE_ID = NARBO_Y * NEW_WIDTH + NARBO_X  # 98

GENAVA_X = 11
GENAVA_Y = 12
GENAVA_TILE_ID = GENAVA_Y * NEW_WIDTH + GENAVA_X  # 287

BIBRACTE_X = 9
BIBRACTE_Y = 13
BIBRACTE_TILE_ID = BIBRACTE_Y * NEW_WIDTH + BIBRACTE_X  # 308

VESONTIO_X = 14
VESONTIO_Y = 15
VESONTIO_TILE_ID = VESONTIO_Y * NEW_WIDTH + VESONTIO_X  # 359

# City sites to remove (not relevant to Chapter 1)
REMOVE_CITY_SITES: set[int] = {
    10 * NEW_WIDTH + 10,  # 240 - Lugdunum
    18 * NEW_WIDTH + 9,   # 423 - Durocortorum
    7 * NEW_WIDTH + 17,   # 178 - Genua
    17 * NEW_WIDTH + 20,  # 411 - Augusta Vindelicorum
    23 * NEW_WIDTH + 14,  # 543 - Colonia
    25 * NEW_WIDTH + 4,   # 579 - Londinium
    16 * NEW_WIDTH + 3,   # 371 - Caesarodunum/Tours
}

# City definitions: (city_id, tile_id, name, player, family, tribe, is_capital)
@dataclass
class CityDef:
    city_id: int
    tile_id: int
    name: str
    player: int        # -1 for tribe-owned
    family: str        # "NONE" for tribe-owned
    tribe: str         # "NONE" for player-owned
    is_capital: bool
    citizens: int
    x: int
    y: int
    territory_x_min: Optional[int] = None  # min x for territory tiles
    territory_x_max: Optional[int] = None  # max x for territory tiles
    territory_y_min: Optional[int] = None  # min y for territory tiles
    territory_y_max: Optional[int] = None  # max y for territory tiles

CITIES: list[CityDef] = [
    CityDef(0, NARBO_TILE_ID, "Narbo", 0, "FAMILY_JULIUS", "NONE",
            True, 3, NARBO_X, NARBO_Y),
    CityDef(1, GENAVA_TILE_ID, "Genava", 0, "FAMILY_JULIUS", "NONE",
            False, 1, GENAVA_X, GENAVA_Y, territory_x_min=10, territory_y_max=12),
    CityDef(2, BIBRACTE_TILE_ID, "Bibracte", -1, "NONE", "TRIBE_AEDUI",
            False, 1, BIBRACTE_X, BIBRACTE_Y),
    CityDef(3, VESONTIO_TILE_ID, "Vesontio", -1, "NONE", "TRIBE_SEQUANI",
            False, 1, VESONTIO_X, VESONTIO_Y),
]

# Units to pre-place: (new_x, new_y, unit_type)
STARTING_UNITS: list[tuple[int, int, str]] = [
    (5, 4, "UNIT_HASTATUS"),
    (6, 3, "UNIT_BALEARIC_SLINGER"),
    (6, 5, "UNIT_NOMAD_SKIRMISHER_2"),
    (5, 5, "UNIT_WORKER"),
]

# Pre-placed improvements: (x, y) -> improvement_type
PLACED_IMPROVEMENTS: dict[tuple[int, int], str] = {
    (7, 5): "IMPROVEMENT_GARRISON_1",
    (7, 2): "IMPROVEMENT_NETS",
    (7, 4): "IMPROVEMENT_NETS",
    (5, 5): "IMPROVEMENT_MINE",
    (6, 6): "IMPROVEMENT_MINE",
    (7, 6): "IMPROVEMENT_MINE",
    (4, 5): "IMPROVEMENT_QUARRY",
    (6, 3): "IMPROVEMENT_QUARRY",
    (5, 2): "IMPROVEMENT_QUARRY",
    # Farms near Genava
    (10, 12): "IMPROVEMENT_FARM",
    (11, 11): "IMPROVEMENT_FARM",
    (12, 11): "IMPROVEMENT_FARM",
    (10, 10): "IMPROVEMENT_FARM",
    (11, 10): "IMPROVEMENT_FARM",
    (12, 10): "IMPROVEMENT_FARM",
}

NUM_UNITS = len(STARTING_UNITS)
NUM_CHARACTERS = 2  # Caesar + Calpurnia
NUM_CITIES = len(CITIES)

# Fields to drop from extracted tiles
DROP_FIELDS = {"Metadata", "TribeSite"}

# ============================================================
# Parsing
# ============================================================

@dataclass
class TileData:
    """Raw tile data parsed from XML. Preserves all fields as-is."""
    src_id: int
    src_x: int
    src_y: int
    fields: list[tuple[str, Optional[str]]] = field(default_factory=list)


def parse_tiles(path: str) -> dict[int, TileData]:
    """Parse all tiles from the source map XML."""
    tiles: dict[int, TileData] = {}

    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    tile_blocks = re.split(r'<Tile\s*\n?\s*ID="(\d+)">', content)

    for i in range(1, len(tile_blocks), 2):
        tile_id = int(tile_blocks[i])
        block = tile_blocks[i + 1].split('</Tile>')[0]

        src_x = tile_id % SOURCE_WIDTH
        src_y = tile_id // SOURCE_WIDTH

        tile = TileData(src_id=tile_id, src_x=src_x, src_y=src_y)

        for m in re.finditer(r'<(\w+)\s*/>', block):
            tile.fields.append((m.group(1), None))

        for m in re.finditer(r'<(\w+)>([^<]*)</(\w+)>', block):
            if m.group(1) == m.group(3):
                tile.fields.append((m.group(1), m.group(2)))

        tiles[tile_id] = tile

    return tiles


# ============================================================
# Extraction
# ============================================================

def extract_region(
    tiles: dict[int, TileData],
) -> list[tuple[int, TileData, bool]]:
    """Extract tiles in the region and compute new IDs.

    Returns list of (new_id, tile_data, is_boundary) sorted by new_id.
    """
    result: list[tuple[int, TileData, bool]] = []

    for new_y in range(NEW_HEIGHT):
        for new_x in range(NEW_WIDTH):
            src_x = SRC_X_MIN + new_x
            src_y = SRC_Y_MIN + new_y
            src_id = src_y * SOURCE_WIDTH + src_x

            new_id = new_y * NEW_WIDTH + new_x

            tile = tiles.get(src_id)
            if tile is None:
                tile = TileData(src_id=src_id, src_x=src_x, src_y=src_y)
                tile.fields = [
                    ("Terrain", "TERRAIN_WATER"),
                    ("Height", "HEIGHT_OCEAN"),
                ]

            is_boundary = (
                new_x <= 1 or new_x >= NEW_WIDTH - 2 or
                new_y <= 1 or new_y >= NEW_HEIGHT - 2
            )

            result.append((new_id, tile, is_boundary))

    return result


# ============================================================
# Hex Geometry
# ============================================================

def offset_to_cube(x: int, y: int) -> tuple[int, int, int]:
    """Convert odd-row-right offset coords to cube coords."""
    q = x - (y - (y & 1)) // 2
    r = y
    s = -q - r
    return q, r, s


def hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Hex distance between two offset coordinate positions."""
    q1, r1, s1 = offset_to_cube(x1, y1)
    q2, r2, s2 = offset_to_cube(x2, y2)
    return max(abs(q1 - q2), abs(r1 - r2), abs(s1 - s2))


# ============================================================
# Scenario Preamble Generation
# ============================================================

def generate_preamble(game_id: str) -> list[str]:
    """Generate the full scenario map preamble (Root attrs through City)."""
    lines: list[str] = []

    # Root element with scenario attributes
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Root')
    lines.append(f'  MapWidth="{NEW_WIDTH}"')
    lines.append('  MapEdgesSafe="True"')
    lines.append('  MapPath=""')
    lines.append(f'  GameId="{game_id}"')
    lines.append('  MapSize="MAPSIZE_SMALL"')
    lines.append('  Scenario="SCENARIO_GALLIC_WARS_1"')
    lines.append('  GameName=""')
    lines.append('  FirstSeed="58000001"')
    lines.append('  MapSeed="58000001"')
    lines.append('  GameMode="SINGLE_PLAYER"')
    lines.append('  TurnStyle="TURNSTYLE_STRICT"')
    lines.append('  TurnTimer="TURNTIMER_NONE"')
    lines.append('  OpponentLevel="OPPONENTLEVEL_AGGRESSIVE"')
    lines.append('  TribeLevel="TRIBELEVEL_STRONG"')
    lines.append('  Development="DEVELOPMENT_FLEDGLING"')
    lines.append('  HumanDevelopment="DEVELOPMENT_FLEDGLING"')
    lines.append('  Advantage="ADVANTAGE_NONE"')
    lines.append('  SuccessionGender="SUCCESSIONGENDER_ABSOLUTE_COGNATIC"')
    lines.append('  SuccessionOrder="SUCCESSIONORDER_PRIMOGENITURE"')
    lines.append('  Mortality="MORTALITY_STANDARD"')
    lines.append('  TurnScale="TURNSCALE_YEAR"')
    lines.append('  TeamNation="TEAMNATION_GAME_UNIQUE"')
    lines.append('  ForceMarch="FORCEMARCH_UNLIMITED"')
    lines.append('  EventLevel="EVENTLEVEL_MODERATE"')
    lines.append('  NumAutosaves="10">')

    # Team / Difficulty / Nation / Dynasty / Humans
    lines.append('  <Team>')
    lines.append('    <PlayerTeam>0</PlayerTeam>')
    lines.append('  </Team>')
    lines.append('  <Difficulty>')
    lines.append('    <PlayerDifficulty>DIFFICULTY_GREAT</PlayerDifficulty>')
    lines.append('  </Difficulty>')
    lines.append('  <Development>')
    lines.append('    <PlayerDevelopment>DEVELOPMENT_FLEDGLING</PlayerDevelopment>')
    lines.append('  </Development>')
    lines.append('  <Nation>')
    lines.append('    <PlayerNation>NATION_ROME</PlayerNation>')
    lines.append('  </Nation>')
    lines.append('  <Dynasty>')
    lines.append('    <PlayerDynasty>DYNASTY_JULIUS_CAESAR</PlayerDynasty>')
    lines.append('  </Dynasty>')
    lines.append('  <Archetype>')
    lines.append('    <LeaderArchetype>TRAIT_PRESET_ARCHETYPE</LeaderArchetype>')
    lines.append('  </Archetype>')
    lines.append('  <Humans>')
    lines.append('    <PlayerHuman>0</PlayerHuman>')
    lines.append('  </Humans>')
    lines.append('  <StartingPlayerOptions>')
    lines.append('    <PLAYEROPTION_NO_TUTORIAL>0</PLAYEROPTION_NO_TUTORIAL>')
    lines.append('  </StartingPlayerOptions>')
    lines.append('  <GameOptions />')
    lines.append('  <OccurrenceLevels />')
    lines.append('  <VictoryEnabled />')
    lines.append('  <GameContent />')
    lines.append('  <MapMultiOptions />')
    lines.append('  <MapSingleOptions />')

    # Game block
    lines.append('  <Game>')
    lines.append('    <Seed>666877878369320307</Seed>')
    lines.append(f'    <NextUnitID>{NUM_UNITS}</NextUnitID>')
    lines.append(f'    <NextCityID>{NUM_CITIES}</NextCityID>')
    lines.append(f'    <NextCharacterID>{NUM_CHARACTERS}</NextCharacterID>')
    lines.append('    <NextOccurrenceID>0</NextOccurrenceID>')
    lines.append('    <MapSize>MAPSIZE_SMALL</MapSize>')
    lines.append('    <NoFogOfWar />')
    lines.append('    <Turn>1</Turn>')
    lines.append('    <TurnTime>0</TurnTime>')
    lines.append('    <TeamTurn>0</TeamTurn>')
    lines.append('    <PlayerTurn>0</PlayerTurn>')
    lines.append('    <YieldPrice>')
    lines.append('      <YIELD_ORDERS>200000</YIELD_ORDERS>')
    lines.append('      <YIELD_FOOD>40000</YIELD_FOOD>')
    lines.append('      <YIELD_IRON>40000</YIELD_IRON>')
    lines.append('      <YIELD_STONE>40000</YIELD_STONE>')
    lines.append('      <YIELD_WOOD>40000</YIELD_WOOD>')
    lines.append('    </YieldPrice>')
    lines.append('    <YieldPriceTurn>')
    lines.append('      <YIELD_ORDERS>200000</YIELD_ORDERS>')
    lines.append('      <YIELD_FOOD>40000</YIELD_FOOD>')
    lines.append('      <YIELD_IRON>40000</YIELD_IRON>')
    lines.append('      <YIELD_STONE>40000</YIELD_STONE>')
    lines.append('      <YIELD_WOOD>40000</YIELD_WOOD>')
    lines.append('    </YieldPriceTurn>')
    lines.append('    <YieldPriceHistory />')
    lines.append('    <ReligionFounded />')
    lines.append('    <ReligionHeadID />')
    lines.append('    <ReligionHolyCity />')
    lines.append('    <ImprovementDisabled />')
    lines.append('    <EventStoryMaxPriority />')
    lines.append('    <ReligionFounder />')
    lines.append('    <TeamAlliance />')
    lines.append('    <FamilyClass>')
    lines.append('      <FAMILY_FABIUS>FAMILYCLASS_CHAMPIONS</FAMILY_FABIUS>')
    lines.append('      <FAMILY_CLAUDIUS>FAMILYCLASS_LANDOWNERS</FAMILY_CLAUDIUS>')
    lines.append('      <FAMILY_VALERIUS>FAMILYCLASS_PATRONS</FAMILY_VALERIUS>')
    lines.append('      <FAMILY_JULIUS>FAMILYCLASS_STATESMEN</FAMILY_JULIUS>')
    lines.append('    </FamilyClass>')
    lines.append('    <TribeConflictTurn />')
    lines.append('    <TribeDiplomacyTurn />')
    lines.append('    <TribeDiplomacyBlock />')
    lines.append('    <TribeWarScore />')
    lines.append('    <TeamConflictTurn />')
    lines.append('    <TeamDiplomacyTurn />')
    lines.append('    <TeamDiplomacyBlock />')
    lines.append('    <TeamWarScore />')
    lines.append('    <ReligionTheology />')
    lines.append('    <TribeContact />')
    lines.append('    <TeamContact>')
    lines.append('      <T.0.0 />')
    lines.append('    </TeamContact>')
    lines.append('    <TribeDiplomacy>')
    # Hostile tribes: always at war
    for tribe in ["TRIBE_REBELS", "TRIBE_ANARCHY", "TRIBE_RAIDERS",
                   "TRIBE_BARBARIANS", "TRIBE_BOII"]:
        lines.append(f'      <{tribe}.0>DIPLOMACY_WAR</{tribe}.0>')
    # Neutral/diplomatic tribes: truce
    for tribe in ["TRIBE_GAULS", "TRIBE_VANDALS", "TRIBE_DANES",
                   "TRIBE_THRACIANS", "TRIBE_SCYTHIANS",
                   "TRIBE_NUMIDIANS",
                   "TRIBE_HELVETII", "TRIBE_SUEBI", "TRIBE_AEDUI",
                   "TRIBE_SEQUANI"]:
        lines.append(f'      <{tribe}.0>DIPLOMACY_TRUCE</{tribe}.0>')
    lines.append('    </TribeDiplomacy>')
    lines.append('    <TeamDiplomacy>')
    lines.append('      <T.0.0>DIPLOMACY_TEAM</T.0.0>')
    lines.append('    </TeamDiplomacy>')
    lines.append('  </Game>')

    # Player block
    lines.append('  <Player')
    lines.append('    ID="0"')
    lines.append('    Name=""')
    lines.append('    Email=""')
    lines.append('    OnlineID=""')
    lines.append('    CustomReminder=""')
    lines.append('    Language="LANGUAGE_ENGLISH"')
    lines.append('    Nation="NATION_ROME"')
    lines.append('    Dynasty="DYNASTY_JULIUS_CAESAR"')
    lines.append('    AIControlledToTurn="0">')
    lines.append('    <OriginalCapitalCityID>0</OriginalCapitalCityID>')
    lines.append('    <FounderID>0</FounderID>')
    lines.append('    <ChosenHeirID>-1</ChosenHeirID>')
    lines.append('    <LastDoTurn>0</LastDoTurn>')
    lines.append('    <TimeStockpile>0</TimeStockpile>')
    lines.append('    <Legitimacy>16</Legitimacy>')
    lines.append('    <RecruitLegitimacy>0</RecruitLegitimacy>')
    lines.append('    <AmbitionDelay>1</AmbitionDelay>')
    lines.append('    <BuyTileCount>0</BuyTileCount>')
    lines.append('    <StateReligionChangeCount>0</StateReligionChangeCount>')
    lines.append('    <TribeMercenaryCount>0</TribeMercenaryCount>')
    lines.append('    <StartTurnCities>0</StartTurnCities>')
    lines.append('    <Founded />')
    lines.append('    <SuccessionGender>SUCCESSIONGENDER_ABSOLUTE_COGNATIC</SuccessionGender>')
    lines.append(f'    <StartingTileIDs>')
    lines.append(f'      <Tile>{NARBO_TILE_ID}</Tile>')
    lines.append(f'    </StartingTileIDs>')
    lines.append('    <YieldStockpile>')
    lines.append('      <YIELD_CIVICS>3000</YIELD_CIVICS>')
    lines.append('      <YIELD_TRAINING>3000</YIELD_TRAINING>')
    lines.append('      <YIELD_MONEY>500</YIELD_MONEY>')
    lines.append('      <YIELD_ORDERS>80</YIELD_ORDERS>')
    lines.append('      <YIELD_FOOD>2000</YIELD_FOOD>')
    lines.append('      <YIELD_IRON>2000</YIELD_IRON>')
    lines.append('      <YIELD_STONE>2000</YIELD_STONE>')
    lines.append('      <YIELD_WOOD>2000</YIELD_WOOD>')
    lines.append('    </YieldStockpile>')
    lines.append('    <TechProgress />')
    lines.append('    <TechCount>')
    lines.append('      <TECH_IRONWORKING>1</TECH_IRONWORKING>')
    lines.append('      <TECH_STONECUTTING>1</TECH_STONECUTTING>')
    lines.append('      <TECH_LABOR_FORCE>1</TECH_LABOR_FORCE>')
    lines.append('      <TECH_TRAPPING>1</TECH_TRAPPING>')
    lines.append('    </TechCount>')
    lines.append('    <LawClassChangeCount />')
    lines.append('    <TheologyEstablishedCount />')
    lines.append('    <ResourceRevealed />')
    lines.append('    <GoalStartedCount />')
    lines.append('    <BonusCount />')
    lines.append('    <AmbitionDecisions />')
    lines.append('    <GoalsFailed />')
    lines.append('    <AllEventStoryTurn />')
    lines.append('    <EventClassTurn />')
    lines.append('    <UnitsProduced />')
    lines.append('    <UnitsProducedTurn />')
    lines.append('    <CouncilCharacter />')
    lines.append('    <FamilySeatCityID>')
    lines.append('      <FAMILY_JULIUS>0</FAMILY_JULIUS>')
    lines.append('    </FamilySeatCityID>')
    lines.append('    <FamilyHeadID />')
    lines.append('    <TechAvailable />')
    lines.append('    <TechPassed />')
    lines.append('    <TechTrashed />')
    lines.append('    <TechTarget />')
    lines.append('    <ActiveLaw>')
    lines.append('      <LAWCLASS_ORDER>LAW_PRIMOGENITURE</LAWCLASS_ORDER>')
    lines.append('    </ActiveLaw>')
    lines.append('    <FamilyReligion />')
    lines.append('    <FamilyLawOpinion />')
    lines.append('    <FamilyLuxuryTurn />')
    lines.append('    <FamilyEventStoryTurn />')
    lines.append('    <ReligionEventStoryTurn />')
    lines.append('    <TribeLuxuryTurn />')
    lines.append('    <TribeEventStoryTurn />')
    lines.append('    <PlayerLuxuryTurn />')
    lines.append('    <PlayerEventStoryTurn />')
    lines.append('    <FamilyEventStoryOption />')
    lines.append('    <ReligionEventStoryOption />')
    lines.append('    <TribeEventStoryOption />')
    lines.append('    <PlayerEventStoryOption />')
    lines.append('    <Leaders>')
    lines.append('      <ID>0</ID>')
    lines.append('    </Leaders>')
    lines.append('    <Families>')
    lines.append('      <FAMILY_JULIUS />')
    lines.append('    </Families>')
    lines.append('    <IgnoreCouncilReminder />')
    lines.append('    <PlayerOptions>')
    lines.append('      <PLAYEROPTION_NO_TUTORIAL />')
    lines.append('    </PlayerOptions>')
    lines.append('    <MemoryPlayerList />')
    lines.append('    <MemoryFamilyList />')
    lines.append('    <MilitaryPowerHistory />')
    lines.append('    <PointsHistory />')
    lines.append('    <YieldRateHistory />')
    lines.append('    <FamilyOpinionHistory />')
    lines.append('    <AI />')
    lines.append('  </Player>')

    # Character blocks
    # Caesar
    lines.append('  <Character')
    lines.append('    ID="0"')
    lines.append('    BirthTurn="-34"')
    lines.append('    Player="0"')
    lines.append('    Character="CHARACTER_JULIUS_CAESAR_LEADER"')
    lines.append('    Gender="GENDER_MALE"')
    lines.append('    FirstName="NAME_JULIUS_CAESAR"')
    lines.append('    Seed="58100000000000001">')
    lines.append('    <Portrait>CHARACTER_PORTRAIT_JULIUS_CAESAR</Portrait>')
    lines.append('    <NameType>NAME_JULIUS_CAESAR</NameType>')
    lines.append('    <Level>1</Level>')
    lines.append('    <LeaderTurn>1</LeaderTurn>')
    lines.append('    <Royal />')
    lines.append('    <Nation>NATION_ROME</Nation>')
    lines.append('    <Family>FAMILY_JULIUS</Family>')
    lines.append('    <Cognomen>COGNOMEN_GOOD</Cognomen>')
    lines.append('    <Rating>')
    lines.append('      <RATING_WISDOM>2</RATING_WISDOM>')
    lines.append('      <RATING_CHARISMA>3</RATING_CHARISMA>')
    lines.append('      <RATING_COURAGE>4</RATING_COURAGE>')
    lines.append('      <RATING_DISCIPLINE>2</RATING_DISCIPLINE>')
    lines.append('    </Rating>')
    lines.append('    <Stat />')
    lines.append('    <Trait>')
    lines.append('      <TRAIT_COMMANDER_ARCHETYPE />')
    lines.append('      <TRAIT_EXPANSIONIST />')
    lines.append('    </Trait>')
    lines.append('    <CognomenHistory>')
    lines.append('      <T1>1</T1>')
    lines.append('    </CognomenHistory>')
    lines.append('  </Character>')

    # Calpurnia
    lines.append('  <Character')
    lines.append('    ID="1"')
    lines.append('    BirthTurn="-20"')
    lines.append('    Player="0"')
    lines.append('    Character="CHARACTER_CALPURNIA"')
    lines.append('    Gender="GENDER_FEMALE"')
    lines.append('    FirstName="NAME_CALPURNIA"')
    lines.append('    Seed="58100000000000002">')
    lines.append('    <Portrait>CHARACTER_PORTRAIT_ROME_LEADER_FEMALE_11</Portrait>')
    lines.append('    <NameType>NAME_CALPURNIA</NameType>')
    lines.append('    <Level>1</Level>')
    lines.append('    <SpouseID>0</SpouseID>')
    lines.append('    <Royal />')
    lines.append('    <Nation>NATION_ROME</Nation>')
    lines.append('    <Family>FAMILY_JULIUS</Family>')
    lines.append('    <Rating>')
    lines.append('      <RATING_WISDOM>1</RATING_WISDOM>')
    lines.append('      <RATING_CHARISMA>0</RATING_CHARISMA>')
    lines.append('      <RATING_COURAGE>0</RATING_COURAGE>')
    lines.append('      <RATING_DISCIPLINE>1</RATING_DISCIPLINE>')
    lines.append('    </Rating>')
    lines.append('    <Stat />')
    lines.append('    <Trait>')
    lines.append('      <TRAIT_JUDGE_ARCHETYPE />')
    lines.append('      <TRAIT_HUMBLE />')
    lines.append('      <TRAIT_SUPERSTITIOUS />')
    lines.append('    </Trait>')
    lines.append('  </Character>')

    # City blocks
    for city in CITIES:
        lines.append('  <City')
        lines.append(f'    ID="{city.city_id}"')
        lines.append(f'    TileID="{city.tile_id}"')
        lines.append(f'    Player="{city.player}"')
        lines.append(f'    Family="{city.family}"')
        lines.append('    Founded="1">')
        lines.append(f'    <Name>{city.name}</Name>')
        lines.append(f'    <Citizens>{city.citizens}</Citizens>')
        if city.is_capital:
            lines.append('    <Capital />')
        lines.append(f'    <FirstPlayer>{max(city.player, 0)}</FirstPlayer>')
        lines.append(f'    <LastPlayer>{max(city.player, 0)}</LastPlayer>')
        if city.player == -1:
            lines.append(f'    <Tribe>{city.tribe}</Tribe>')
        lines.append('    <YieldProgress />')
        lines.append('    <YieldOverflow />')
        lines.append('    <ProjectCount />')
        lines.append('    <LuxuryTurn />')
        lines.append('    <AgentCharacterID />')
        lines.append('    <TeamCultureStep />')
        if city.player >= 0:
            lines.append('    <TeamDiscontentLevel />')
            lines.append('    <TeamDiscontentLevelHighest />')
        lines.append('    <Religion />')
        lines.append('    <PlayerFamily>')
        if city.player >= 0:
            lines.append(f'      <P.{city.player}>{city.family}</P.{city.player}>')
        lines.append('    </PlayerFamily>')
        lines.append('    <TeamCulture>')
        lines.append('      <T.0>CULTURE_WEAK</T.0>')
        lines.append('    </TeamCulture>')
        if city.is_capital:
            lines.append('    <BuildQueue>')
            lines.append('      <QueueInfo>')
            lines.append('        <Build>BUILD_PROJECT</Build>')
            lines.append('        <Type>PROJECT_COUNCIL_1</Type>')
            lines.append('        <Data>-1</Data>')
            lines.append('        <Progress>0</Progress>')
            lines.append('        <Repeat />')
            lines.append('        <YieldCost />')
            lines.append('      </QueueInfo>')
            lines.append('    </BuildQueue>')
        lines.append('  </City>')

    return lines


# ============================================================
# Tile Output
# ============================================================

def build_unit_map() -> dict[int, list[tuple[int, str]]]:
    """Build a mapping of tile_id -> [(unit_id, unit_type), ...]."""
    unit_map: dict[int, list[tuple[int, str]]] = {}
    for unit_id, (ux, uy, unit_type) in enumerate(STARTING_UNITS):
        tile_id = uy * NEW_WIDTH + ux
        unit_map.setdefault(tile_id, []).append((unit_id, unit_type))
    return unit_map


def write_unit(unit_id: int, unit_type: str) -> list[str]:
    """Generate XML lines for a unit embedded in a tile."""
    seed = 58100000000000100 + unit_id
    lines: list[str] = []
    lines.append(f'    <Unit')
    lines.append(f'      ID="{unit_id}"')
    lines.append(f'      Type="{unit_type}"')
    lines.append(f'      Player="0"')
    lines.append(f'      Tribe="NONE"')
    lines.append(f'      Seed="{seed}">')
    lines.append(f'      <CreateTurn>1</CreateTurn>')
    lines.append(f'      <Facing>NE</Facing>')
    lines.append(f'      <OriginalPlayer>0</OriginalPlayer>')
    lines.append(f'      <RaidTurn />')
    lines.append(f'      <PlayerFamily>')
    lines.append(f'        <P.0>FAMILY_JULIUS</P.0>')
    lines.append(f'      </PlayerFamily>')
    lines.append(f'      <QueueList />')
    lines.append(f'      <AI />')
    lines.append(f'    </Unit>')
    return lines


def build_city_tile_map() -> dict[int, CityDef]:
    """Build a mapping of tile_id -> CityDef for all cities."""
    return {city.tile_id: city for city in CITIES}


def build_improvement_map() -> dict[int, str]:
    """Build a mapping of tile_id -> improvement_type for pre-placed improvements."""
    return {y * NEW_WIDTH + x: imp for (x, y), imp in PLACED_IMPROVEMENTS.items()}


def write_tile(
    new_id: int,
    tile: TileData,
    is_boundary: bool,
    unit_map: dict[int, list[tuple[int, str]]],
    city_map: dict[int, CityDef],
    improvement_map: dict[int, str],
) -> list[str]:
    """Generate XML lines for a single tile."""
    lines: list[str] = []
    new_x = new_id % NEW_WIDTH
    new_y = new_id // NEW_WIDTH

    city = city_map.get(new_id)
    has_units = new_id in unit_map
    placed_improvement = improvement_map.get(new_id)
    # Reveal tiles that have units or are a player city
    is_revealed = has_units or (city is not None and city.player >= 0)

    # Check if this tile is in any player-owned city's territory
    city_territory_id: Optional[int] = None
    for c in CITIES:
        if c.player >= 0 and not is_boundary:
            dist = hex_distance(new_x, new_y, c.x, c.y)
            if dist <= 2:
                # Apply optional territory bounds
                if c.territory_x_min is not None and new_x < c.territory_x_min:
                    continue
                if c.territory_x_max is not None and new_x > c.territory_x_max:
                    continue
                if c.territory_y_min is not None and new_y < c.territory_y_min:
                    continue
                if c.territory_y_max is not None and new_y > c.territory_y_max:
                    continue
                city_territory_id = c.city_id
                break

    lines.append(f'  <Tile')
    lines.append(f'    ID="{new_id}">')

    if is_boundary:
        lines.append('    <Boundary />')

    # Track whether source tile already has CitySite
    terrain_value: Optional[str] = None
    source_has_citysite = any(tag == "CitySite" for tag, _ in tile.fields)
    source_has_improvement = any(tag == "Improvement" for tag, _ in tile.fields)

    # Write tile fields from source, preserving order
    for tag, value in tile.fields:
        if tag in DROP_FIELDS:
            continue
        if tag == "Boundary":
            continue
        # On city tiles, change CitySite from ACTIVE to USED
        if city is not None and tag == "CitySite":
            lines.append('    <CitySite>USED</CitySite>')
            continue
        # On city tiles, override terrain to URBAN
        if city is not None and tag == "Terrain":
            terrain_value = "TERRAIN_URBAN"
            lines.append(f'    <Terrain>TERRAIN_URBAN</Terrain>')
            continue
        # Remove city sites that aren't needed for Chapter 1
        if new_id in REMOVE_CITY_SITES:
            if tag == "CitySite":
                continue
            if tag == "Improvement" and value == "IMPROVEMENT_CITY_SITE":
                if placed_improvement is not None:
                    lines.append(f'    <Improvement>{placed_improvement}</Improvement>')
                continue
            if tag == "ElementName":
                continue
            if tag == "Terrain" and value == "TERRAIN_URBAN":
                terrain_value = "TERRAIN_LUSH"
                lines.append('    <Terrain>TERRAIN_LUSH</Terrain>')
                continue
        # Override Improvement if this tile has a pre-placed one
        if tag == "Improvement" and placed_improvement is not None:
            lines.append(f'    <Improvement>{placed_improvement}</Improvement>')
            continue
        # Skip NationSite from source (we don't add it anymore)
        if tag == "NationSite":
            continue
        if tag == "Terrain":
            terrain_value = value
        if value is None:
            lines.append(f'    <{tag} />')
        else:
            lines.append(f'    <{tag}>{value}</{tag}>')

    # For new city tiles that didn't have CitySite in source, add it
    if city is not None and not source_has_citysite:
        lines.append('    <CitySite>USED</CitySite>')

    # Add pre-placed improvement if source tile had none
    if placed_improvement is not None and not source_has_improvement:
        lines.append(f'    <Improvement>{placed_improvement}</Improvement>')

    # Add revealed state for tiles near player cities
    if is_revealed and not is_boundary:
        if city_territory_id is not None:
            lines.append('    <RevealedCityTerritory>')
            lines.append('      <Team')
            lines.append(f'        CityTerritory="{city_territory_id}">0</Team>')
            lines.append('    </RevealedCityTerritory>')
        lines.append('    <Revealed>')
        lines.append('      <Team>0</Team>')
        lines.append('    </Revealed>')
        if city is not None and city.player >= 0:
            lines.append('    <RevealedCity>')
            lines.append('      <Team>0</Team>')
            lines.append('    </RevealedCity>')

    # City territory for tiles near player-owned cities
    if city_territory_id is not None:
        lines.append(f'    <CityTerritory>{city_territory_id}</CityTerritory>')
    if city is not None and city.player >= 0:
        lines.append(f'    <OrigUrbanOwner>{city.player}</OrigUrbanOwner>')

    # Embed units
    if has_units:
        for unit_id, unit_type in unit_map[new_id]:
            lines.extend(write_unit(unit_id, unit_type))

    # Standard scenario map tags on every tile
    lines.append('    <Religion />')
    if is_revealed and not is_boundary and terrain_value:
        lines.append('    <RevealedTerrain>')
        lines.append(f'      <Team')
        lines.append(f'        Terrain="{terrain_value}">0</Team>')
        lines.append('    </RevealedTerrain>')
    lines.append('    <RevealedTurn />')

    lines.append('  </Tile>')
    return lines


# ============================================================
# Output
# ============================================================

def write_bare_xml(
    extracted: list[tuple[int, TileData, bool]],
    output_path: str,
) -> None:
    """Write a bare tile-only map XML (old format, for debugging)."""
    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append(f'<Root MapWidth="{NEW_WIDTH}" MapEdgesSafe="True">')

    for new_id, tile, is_boundary in extracted:
        lines.append(f'  <Tile')
        lines.append(f'    ID="{new_id}">')
        if is_boundary:
            lines.append('    <Boundary />')
        for tag, value in tile.fields:
            if tag in DROP_FIELDS or tag == "Boundary" or tag == "NationSite":
                continue
            if value is None:
                lines.append(f'    <{tag} />')
            else:
                lines.append(f'    <{tag}>{value}</{tag}>')
        lines.append('  </Tile>')

    lines.append('</Root>')
    lines.append('')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    print(f"Generated BARE map: {output_path}")
    print(f"  Tiles: {len(extracted)}")


def write_xml(
    extracted: list[tuple[int, TileData, bool]],
    output_path: str,
) -> None:
    """Write the complete scenario map XML."""
    game_id = str(uuid.uuid4())
    unit_map = build_unit_map()
    city_map = build_city_tile_map()
    imp_map = build_improvement_map()

    lines: list[str] = []

    # Preamble: Root attributes, Game, Player, Characters, City
    lines.extend(generate_preamble(game_id))

    # Tiles
    for new_id, tile, is_boundary in extracted:
        lines.extend(write_tile(new_id, tile, is_boundary, unit_map, city_map, imp_map))

    lines.append('</Root>')
    lines.append('')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    print(f"Generated scenario map: {output_path}")
    print(f"  Source region: x=[{SRC_X_MIN},{SRC_X_MAX}], y=[{SRC_Y_MIN},{SRC_Y_MAX}]")
    print(f"  Dimensions: {NEW_WIDTH} x {NEW_HEIGHT} = {NEW_WIDTH * NEW_HEIGHT} tiles")
    print(f"  Cities: {NUM_CITIES}")
    for c in CITIES:
        owner = f"Player {c.player}" if c.player >= 0 else c.tribe
        print(f"    {c.name} at tile {c.tile_id} ({c.x},{c.y}) [{owner}]")
    print(f"  Units: {NUM_UNITS} pre-placed")
    print(f"  Improvements: {len(PLACED_IMPROVEMENTS)} pre-placed")
    print(f"  Characters: {NUM_CHARACTERS} (Caesar + Calpurnia)")
    print(f"  GameId: {game_id}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    bare_mode = "--bare" in sys.argv

    print(f"Reading source map: {SOURCE_MAP}")
    tiles = parse_tiles(SOURCE_MAP)
    print(f"  Parsed {len(tiles)} tiles (source map: {SOURCE_WIDTH} wide)")

    extracted = extract_region(tiles)
    print(f"  Extracted {len(extracted)} tiles")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(
        project_dir, "GallicWars", "Maps", "GallicWars1Map.xml"
    )

    if bare_mode:
        write_bare_xml(extracted, output_path)
    else:
        write_xml(extracted, output_path)


if __name__ == "__main__":
    main()

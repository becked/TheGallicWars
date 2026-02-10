#!/usr/bin/env python3
"""
Generate a complete scenario map for the Gallic Wars scenario.

Reads terrain data from data/base_terrain.xml (the frozen terrain file)
and layers scenario state on top: game settings, player, characters,
cities, units, territory, and revelation state.

Usage:
    python scripts/generate_scenario.py
    # Writes to GallicWars/Maps/GallicWars1Map.xml
"""

import re
import os
import uuid
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# Scenario Constants
# ============================================================

BOUNDARY_WIDTH = 2  # tiles from each edge marked as boundary

NARBO_X = 6
NARBO_Y = 4

GENAVA_X = 11
GENAVA_Y = 12

BIBRACTE_X = 9
BIBRACTE_Y = 13

VESONTIO_X = 14
VESONTIO_Y = 15

# City definitions
@dataclass
class CityDef:
    city_id: int
    tile_id: int  # computed from width at load time
    name: str
    player: int        # -1 for tribe-owned
    family: str        # "NONE" for tribe-owned
    tribe: str         # "NONE" for player-owned
    is_capital: bool
    citizens: int
    x: int
    y: int
    culture: str = "CULTURE_WEAK"
    build_queue: Optional[list[tuple[str, str]]] = None  # [(build_type, unit/project), ...]
    extra_territory: Optional[list[tuple[int, int]]] = None  # extra (x,y) tiles
    territory_radius: int = 2
    territory_x_min: Optional[int] = None
    territory_x_max: Optional[int] = None
    territory_y_min: Optional[int] = None
    territory_y_max: Optional[int] = None


def make_cities(width: int) -> list[CityDef]:
    """Build the CITIES list with tile IDs computed from map width."""
    return [
        CityDef(0, NARBO_Y * width + NARBO_X, "Narbo", 0, "FAMILY_JULIUS",
                "NONE", True, 3, NARBO_X, NARBO_Y,
                culture="CULTURE_DEVELOPING",
                build_queue=[("BUILD_UNIT", "UNIT_HASTATUS")],
                extra_territory=[(8, 5), (9, 5), (10, 5), (11, 5), (9, 6), (10, 6)]),
        CityDef(1, GENAVA_Y * width + GENAVA_X, "Genava", 0, "FAMILY_JULIUS",
                "NONE", False, 1, GENAVA_X, GENAVA_Y,
                build_queue=[("BUILD_UNIT", "UNIT_WARRIOR")],
                territory_x_min=10, territory_y_max=12),
        CityDef(2, BIBRACTE_Y * width + BIBRACTE_X, "Bibracte", -1, "NONE",
                "TRIBE_AEDUI", False, 1, BIBRACTE_X, BIBRACTE_Y),
        CityDef(3, VESONTIO_Y * width + VESONTIO_X, "Vesontio", -1, "NONE",
                "TRIBE_SEQUANI", False, 1, VESONTIO_X, VESONTIO_Y),
    ]


# Units to pre-place: (x, y, unit_type)
STARTING_UNITS: list[tuple[int, int, str]] = [
    (5, 4, "UNIT_HASTATUS"),
    (6, 3, "UNIT_BALEARIC_SLINGER"),
    (6, 5, "UNIT_NOMAD_SKIRMISHER_2"),
    (5, 5, "UNIT_WORKER"),
]

NUM_UNITS = len(STARTING_UNITS)
NUM_CHARACTERS = 2  # Caesar + Calpurnia


# ============================================================
# Terrain Parsing
# ============================================================

@dataclass
class TileData:
    """Tile data parsed from the frozen terrain file."""
    tile_id: int
    fields: list[tuple[str, Optional[str]]] = field(default_factory=list)


def parse_frozen_terrain(
    path: str,
) -> tuple[int, int, list[tuple[int, TileData]]]:
    """Parse the frozen terrain file.

    Returns (width, height, tiles) where tiles is
    [(tile_id, tile_data), ...] sorted by tile_id.
    """
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Extract MapWidth from Root element
    m = re.search(r'MapWidth="(\d+)"', content)
    if m is None:
        raise ValueError(f"No MapWidth found in {path}")
    width = int(m.group(1))

    # Parse tiles
    tiles: list[tuple[int, TileData]] = []
    tile_blocks = re.split(r'<Tile\s*\n?\s*ID="(\d+)">', content)

    for i in range(1, len(tile_blocks), 2):
        tile_id = int(tile_blocks[i])
        block = tile_blocks[i + 1].split('</Tile>')[0]

        tile = TileData(tile_id=tile_id)

        for fm in re.finditer(r'<(\w+)\s*/>', block):
            tile.fields.append((fm.group(1), None))

        for fm in re.finditer(r'<(\w+)>([^<]*)</(\w+)>', block):
            if fm.group(1) == fm.group(3):
                tile.fields.append((fm.group(1), fm.group(2)))

        tiles.append((tile_id, tile))

    height = len(tiles) // width
    return width, height, tiles


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

def generate_preamble(
    width: int,
    cities: list[CityDef],
    game_id: str,
) -> list[str]:
    """Generate the full scenario map preamble (Root attrs through City)."""
    num_cities = len(cities)
    narbo_tile_id = NARBO_Y * width + NARBO_X

    lines: list[str] = []

    # Root element with scenario attributes
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Root')
    lines.append(f'  MapWidth="{width}"')
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
    lines.append(f'    <NextCityID>{num_cities}</NextCityID>')
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
    lines.append(f'      <Tile>{narbo_tile_id}</Tile>')
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
    lines.append('      <TECH_POLIS>1</TECH_POLIS>')
    lines.append('      <TECH_STONECUTTING>1</TECH_STONECUTTING>')
    lines.append('      <TECH_IRONWORKING>1</TECH_IRONWORKING>')
    lines.append('      <TECH_LABOR_FORCE>1</TECH_LABOR_FORCE>')
    lines.append('      <TECH_ADMINISTRATION>1</TECH_ADMINISTRATION>')
    lines.append('      <TECH_TRAPPING>1</TECH_TRAPPING>')
    lines.append('      <TECH_MILITARY_DRILL>1</TECH_MILITARY_DRILL>')
    lines.append('      <TECH_ARISTOCRACY>1</TECH_ARISTOCRACY>')
    lines.append('      <TECH_RHETORIC>1</TECH_RHETORIC>')
    lines.append('      <TECH_SOVEREIGNTY>1</TECH_SOVEREIGNTY>')
    lines.append('      <TECH_HUSBANDRY>1</TECH_HUSBANDRY>')
    lines.append('      <TECH_DRAMA>1</TECH_DRAMA>')
    lines.append('      <TECH_FORESTRY>1</TECH_FORESTRY>')
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
    lines.append('      <LAWCLASS_EPICS_EXPLORATION>LAW_EXPLORATION</LAWCLASS_EPICS_EXPLORATION>')
    lines.append('      <LAWCLASS_SLAVERY_FREEDOM>LAW_SLAVERY</LAWCLASS_SLAVERY_FREEDOM>')
    lines.append('      <LAWCLASS_CENTRALIZATION_VASSALAGE>LAW_CENTRALIZATION</LAWCLASS_CENTRALIZATION_VASSALAGE>')
    lines.append('      <LAWCLASS_TYRANNY_CONSTITUTION>LAW_TYRANNY</LAWCLASS_TYRANNY_CONSTITUTION>')
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
    lines.append('    BirthTurn="-42"')
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
    for city in cities:
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
        lines.append(f'      <T.0>{city.culture}</T.0>')
        lines.append('    </TeamCulture>')
        if city.build_queue:
            lines.append('    <BuildQueue>')
            for build_type, item_type in city.build_queue:
                lines.append('      <QueueInfo>')
                lines.append(f'        <Build>{build_type}</Build>')
                lines.append(f'        <Type>{item_type}</Type>')
                lines.append('        <Data>-1</Data>')
                lines.append('        <Progress>0</Progress>')
                lines.append('        <YieldCost />')
                lines.append('      </QueueInfo>')
            lines.append('    </BuildQueue>')
        lines.append('  </City>')

    return lines


# ============================================================
# Tile Output
# ============================================================

def build_unit_map(width: int) -> dict[int, list[tuple[int, str]]]:
    """Build a mapping of tile_id -> [(unit_id, unit_type), ...]."""
    unit_map: dict[int, list[tuple[int, str]]] = {}
    for unit_id, (ux, uy, unit_type) in enumerate(STARTING_UNITS):
        tile_id = uy * width + ux
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


def build_city_tile_map(cities: list[CityDef]) -> dict[int, CityDef]:
    """Build a mapping of tile_id -> CityDef for all cities."""
    return {city.tile_id: city for city in cities}


def write_tile(
    tile_id: int,
    tile: TileData,
    is_boundary: bool,
    width: int,
    cities: list[CityDef],
    unit_map: dict[int, list[tuple[int, str]]],
    city_map: dict[int, CityDef],
) -> list[str]:
    """Generate XML lines for a single tile with scenario state."""
    lines: list[str] = []
    new_x = tile_id % width
    new_y = tile_id // width

    city = city_map.get(tile_id)
    has_units = tile_id in unit_map
    is_revealed = has_units or (city is not None and city.player >= 0)

    # Check if this tile is in any player-owned city's territory
    city_territory_id: Optional[int] = None
    for c in cities:
        if c.player >= 0 and not is_boundary:
            in_extra = (c.extra_territory is not None
                        and (new_x, new_y) in c.extra_territory)
            dist = hex_distance(new_x, new_y, c.x, c.y)
            if in_extra or dist <= c.territory_radius:
                if not in_extra:
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
    lines.append(f'    ID="{tile_id}">')

    if is_boundary:
        lines.append('    <Boundary />')

    # Track terrain for RevealedTerrain
    terrain_value: Optional[str] = None
    source_has_citysite = any(tag == "CitySite" for tag, _ in tile.fields)

    # Write tile fields from frozen terrain, with city overrides
    for tag, value in tile.fields:
        # On city tiles, change CitySite from ACTIVE to USED
        if city is not None and tag == "CitySite":
            lines.append('    <CitySite>USED</CitySite>')
            continue
        # On city tiles, override terrain to URBAN
        if city is not None and tag == "Terrain":
            terrain_value = "TERRAIN_URBAN"
            lines.append('    <Terrain>TERRAIN_URBAN</Terrain>')
            continue
        # Pass through everything else as-is
        if tag == "Terrain":
            terrain_value = value
        if value is None:
            lines.append(f'    <{tag} />')
        else:
            lines.append(f'    <{tag}>{value}</{tag}>')

    # For city tiles that didn't have CitySite in terrain, add it
    if city is not None and not source_has_citysite:
        lines.append('    <CitySite>USED</CitySite>')

    # Revealed state for tiles with units or player cities
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

    # City territory
    if city_territory_id is not None:
        lines.append(f'    <CityTerritory>{city_territory_id}</CityTerritory>')
    if city is not None and city.player >= 0:
        lines.append(f'    <OrigUrbanOwner>{city.player}</OrigUrbanOwner>')

    # Embed units
    if has_units:
        for unit_id, unit_type in unit_map[tile_id]:
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

def write_xml(
    width: int,
    height: int,
    tiles: list[tuple[int, TileData]],
    output_path: str,
) -> None:
    """Write the complete scenario map XML."""
    game_id = str(uuid.uuid4())
    cities = make_cities(width)
    unit_map = build_unit_map(width)
    city_map = build_city_tile_map(cities)

    lines: list[str] = []

    # Preamble: Root attributes, Game, Player, Characters, City
    lines.extend(generate_preamble(width, cities, game_id))

    # Tiles
    for tile_id, tile in tiles:
        new_x = tile_id % width
        new_y = tile_id // width
        is_boundary = (
            new_x < BOUNDARY_WIDTH or new_x >= width - BOUNDARY_WIDTH or
            new_y < BOUNDARY_WIDTH or new_y >= height - BOUNDARY_WIDTH
        )
        lines.extend(write_tile(
            tile_id, tile, is_boundary, width, cities, unit_map, city_map,
        ))

    lines.append('</Root>')
    lines.append('')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))

    print(f"Generated scenario map: {output_path}")
    print(f"  Terrain source: data/base_terrain.xml")
    print(f"  Dimensions: {width} x {height} = {width * height} tiles")
    print(f"  Cities: {len(cities)}")
    for c in cities:
        owner = f"Player {c.player}" if c.player >= 0 else c.tribe
        print(f"    {c.name} at tile {c.tile_id} ({c.x},{c.y}) [{owner}]")
    print(f"  Units: {NUM_UNITS} pre-placed")
    print(f"  Characters: {NUM_CHARACTERS} (Caesar + Calpurnia)")
    print(f"  GameId: {game_id}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    terrain_path = os.path.join(project_dir, "data", "base_terrain.xml")
    output_path = os.path.join(
        project_dir, "GallicWars", "Maps", "GallicWars1Map.xml"
    )

    print(f"Reading terrain: {terrain_path}")
    width, height, tiles = parse_frozen_terrain(terrain_path)
    print(f"  {width} x {height} = {len(tiles)} tiles")

    write_xml(width, height, tiles, output_path)


if __name__ == "__main__":
    main()

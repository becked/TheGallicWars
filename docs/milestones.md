# The Gallic Wars Mod - Milestones

## Milestone 1: MVP Scenario Mod (COMPLETE)
- Scenario appears in Old World's scenario browser and launches a game
- ModInfo.xml, scenario-add.xml, scenarioClass-add.xml, preload-text-add.xml
- Basic map loads, player can start as Rome

## Milestone 2: Accurate Map (COMPLETE)
- 31x35 region extracted from Imperium Romanum map, expanded for gameplay
- Correct terrain, rivers, and geography preserved via 1:1 tile copy
- Rome starts at Narbo (6,4)
- Outer 2 tiles marked as boundaries

## Milestone 3: Map Customization (COMPLETE)
- Pre-founded historical cities: Narbo and Genava (Rome), Bibracte (Aedui), Vesontio (Sequani)
- Removed irrelevant city sites (Genua, Lugdunum, Durocortorum, Tours, Colonia, Londinium, Augusta Vindelicorum)
- Genava territory bounded (x_min=10, y_max=13) to avoid overlap with Bibracte
- Improvements preserved from source map; Roads not present in source region
- TribeSites dropped (tribes represented as city owners instead)

## Milestone 4: Scenario Gameplay (IN PROGRESS)
### Done
- Dynasty locked to Julius Caesar (Wonders & Dynasties DLC)
- Caesar and Calpurnia as starting characters
- 5 custom tribes defined: Helvetii, Suebi, Aedui, Sequani, Boii
- TribeDiplomacy configured (Boii at war, others at truce)
- Starting units: Hastatus, Balearic Slinger, Nomad Skirmisher, Worker near Narbo
- Victory conditions: 3 scenario goals (Fortify the Rhone, Battle of Bibracte, Battle of Vosges)
- CrcFix Harmony DLL to work around game bug with StrictModeDeferred info types in scenario mods

### Remaining
- Tribe starting units / army placement (Helvetii migration force, Ariovistus warband)
- Gameplay balance tuning (resource stockpiles, tech state, difficulty settings)

## Milestone 5: Book 1 Narrative Content (PENDING)
- Helvetii migration events
- Ariovistus campaign events
- Historical event stories
- Gameplay balance and testing

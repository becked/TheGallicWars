# The Gallic Wars Mod - Milestones

## Milestone 1: MVP Scenario Mod (COMPLETE)
- Scenario appears in Old World's scenario browser and launches a game
- ModInfo.xml, scenario-add.xml, scenarioClass-add.xml, preload-text-add.xml
- Basic map loads, player can start as Rome

## Milestone 2: Accurate Map (COMPLETE)
- 37x41 region extracted from Imperium Romanum map, expanded for gameplay
- Correct terrain, rivers, and geography preserved via 1:1 tile copy
- Rome starts at Narbo (6,4)
- Outer 2 tiles marked as boundaries

## Milestone 3: Map Customization (COMPLETE)
- Pre-founded historical cities: Narbo and Genava (Rome), Bibracte (Aedui), Vesontio (Sequani)
- Removed irrelevant city sites (Genua, Lugdunum, Durocortorum, Tours, Colonia, Londinium, Augusta Vindelicorum)
- Genava territory bounded (x_min=10, x_max=19, y_max=19) to avoid overlap
- Improvements preserved from source map; roads added on key tiles east of Narbo
- Alps terrain refined: mountain-to-hill transitions, tundra/temperate gradients
- ALPES label repositioned to (23,13); ancient ruins removed at (33,17)
- TribeSites dropped (tribes represented as city owners instead)

## Milestone 4: Scenario Gameplay (COMPLETE)
- Dynasty locked to Julius Caesar (Wonders & Dynasties DLC)
- Caesar and Calpurnia as starting characters
- 5 custom tribes defined: Helvetii, Suebi, Aedui, Sequani, Boii
- TribeDiplomacy configured (Boii at war, others at truce)
- 14 starting units near Narbo: 4 Hastatus, 2 Balearic Slingers, 4 Elite Nomad Warlords, 4 Workers
- City families: Narbo→Fabius (Champions), Genava→Claudius (Landowners)
- Rome bonuses via effectPlayer-change: +50 legitimacy, +20 orders/turn
- Starting orders stockpile set to 37 for turn 1
- Camera start positioned east of Narbo for wider initial view
- Victory conditions: 3 scenario goals (Fortify the Rhone, Battle of Bibracte, Battle of Vosges)
- CrcFix Harmony DLL to work around game bug with StrictModeDeferred info types in scenario mods

## Milestone 5: Book 1 Narrative Content (PENDING)
- Narrative event chains (Helvetii migration, Dumnorix subplot, Ariovistus campaign)
- Tribal army spawning via events (Helvetii migration force, Boii flankers, Suebi warband)
- Aedui auxiliary cavalry granted via events
- Historical characters (Labienus, Publius Crassus, Diviciacus, Ariovistus, Divico, Dumnorix)
- Gameplay balance and testing

# The Gallic Wars - Scenario Mod Design Document

## Overview

A scenario campaign mod for Old World based on Julius Caesar's *Commentarii de Bello Gallico*. The player controls Rome as Julius Caesar, playing through scenario chapters that mirror the real-life events and battles described in the book.

This document covers **Chapter 1: The Helvetii and Ariovistus** (Book I, 58 BCE) - the initial release.

### Campaign Vision (Future Chapters)

| Chapter | Title | Book | Year | Focus |
|---------|-------|------|------|-------|
| 1 | The Helvetii and Ariovistus | I | 58 BCE | Helvetii migration, Ariovistus invasion |
| 2 | Terror of the Belgae | II | 57 BCE | Belgian confederation, Battle of the Sabis |
| 3 | Beyond the Known World | III-IV | 56-55 BCE | Veneti naval campaign, Rhine bridge, Britain |
| 4 | Revolt of Ambiorix | V-VI | 54-53 BCE | Legion destroyed, siege of Cicero's camp |
| 5 | Vercingetorix and Alesia | VII | 52 BCE | Great revolt, Gergovia, siege of Alesia |

---

## Mod Architecture

### Single Mod, All Chapters

The entire campaign is distributed as **one mod** (`GallicWars`). Each chapter is a separate scenario registered within that mod. Users subscribe once on Steam Workshop / mod.io and get all chapters as they're released via updates.

This follows from how Old World handles mod dependencies: there is no automatic dependency resolution. If we split into a parent mod + per-chapter child mods, users would have to manually find and install each piece. A single mod avoids that friction entirely.

**Note**: The Egypt campaign uses a parent + child pattern (`EgyptCampaign` + `Egypt1`-`Egypt6`), but that works because it's bundled DLC — the parent is guaranteed to be on disk via `gameContentRequired: PHARAOHS`. User-distributed mods don't have that luxury.

### How User Mods Hook Into the Game

Old World loads mods from two directories through the **same pipeline** — there is no difference in capability between bundled and user mods:

| Location | Contents |
|----------|----------|
| `Reference/XML/Mods/` (game install) | Bundled scenario mods (Carthage, Greece, Egypt, etc.) |
| `~/Library/Application Support/OldWorld/Mods/` (macOS) | User-installed mods |
| `%USERPROFILE%\Documents\My Games\OldWorld\Mods\` (Windows) | User-installed mods |

A `ModRecord.IsInternal` flag exists in the engine, but it's only used for demo mode restrictions and UI filtering — not for XML loading, scenario registration, or gameplay behavior. A user mod with `<scenario>true</scenario>` and a `scenario-add.xml` is treated identically to Greece or Egypt by the game engine.

**Scenario registration** uses the same pattern as Greece (Pattern B): the mod's `scenario-add.xml` injects scenario entries at load time. The game reads `scenario.xml` (base) plus all `scenario-add.xml` files from loaded mods, building the full scenario list dynamically.

### Mod Folder Structure

```
GallicWars/
├── ModInfo.xml
├── Maps/
│   ├── GallicWars1Map.xml          (Chapter 1 map)
│   ├── GallicWars2Map.xml          (Chapter 2 map - added later)
│   └── ...
└── Infos/
    ├── scenario-add.xml            (registers ALL chapter scenarios)
    ├── scenarioClass-add.xml       (SCENARIOCLASS_GALLIC_WARS)
    ├── tribe-add.xml               (shared tribes across chapters)
    ├── turnScale-add.xml           (weekly turn scale)
    ├── character-add.xml           (all characters across chapters)
    ├── eventStory-add.xml          (all events across chapters)
    ├── eventOption-add.xml
    ├── eventTrigger-add.xml
    ├── eventClass-add.xml
    ├── eventLink-add.xml
    ├── bonus-event-add.xml
    ├── goal-add.xml
    ├── victory-add.xml
    ├── difficulty-add.xml
    ├── text-eventStory-add.xml
    ├── text-eventStoryTitle-add.xml
    ├── text-eventOption-add.xml
    ├── text-bonus-add.xml
    └── preload-text-add.xml
```

All chapters share one `zModName: GallicWars`. The game loads all XML when any chapter is played — events and goals for other chapters are simply never triggered because they're gated by scenario-specific event triggers and links. This is the same pattern Egypt uses (EgyptCampaign loads text for all 6 chapters).

### ModInfo.xml

```xml
<?xml version="1.0"?>
<ModInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <displayName>The Gallic Wars</displayName>
  <description>Play through Caesar's Commentarii de Bello Gallico.
Chapter 1: The Helvetii and Ariovistus (58 BCE).</description>
  <author>Jeff</author>
  <modversion>0.1.0</modversion>
  <tags>Scenario</tags>
  <singlePlayer>true</singlePlayer>
  <multiplayer>false</multiplayer>
  <scenario>true</scenario>
  <scenarioToggle>false</scenarioToggle>
  <blocksMods>false</blocksMods>
  <modDependencies />
  <modIncompatibilities />
  <modWhitelist />
  <gameContentRequired>NONE</gameContentRequired>
</ModInfo>
```

### scenario-add.xml (Chapter 1)

```xml
<?xml version="1.0" encoding="utf-8"?>
<Root>
  <Entry>
    <zType>SCENARIO_GALLIC_WARS_1</zType>
    <Name>TEXT_SCENARIO_GALLIC_WARS_1</Name>
    <SubTitle>TEXT_SCENARIO_GALLIC_WARS_1_SUB</SubTitle>
    <ScenarioClass>SCENARIOCLASS_GALLIC_WARS</ScenarioClass>
    <zMapFile>GallicWars1Map</zMapFile>
    <zModName>GallicWars</zModName>
    <Nation>NATION_ROME</Nation>
    <Difficulty>DIFFICULTY_GOOD</Difficulty>
    <TurnScale>TURNSCALE_WEEK</TurnScale>
    <ParametersInvalid>
      <zValue>NumPlayers</zValue>
      <zValue>NumTeams</zValue>
      <zValue>Nation</zValue>
      <zValue>Archetype</zValue>
      <zValue>Dynasty</zValue>
      <zValue>TurnScale</zValue>
      <zValue>MapSize</zValue>
      <zValue>MapOptions</zValue>
      <zValue>MapClass</zValue>
      <zValue>MapPath</zValue>
    </ParametersInvalid>
  </Entry>
  <!-- Future chapters added here as new <Entry> blocks with Prereq chaining:
  <Entry>
    <zType>SCENARIO_GALLIC_WARS_2</zType>
    <Prereq>SCENARIO_GALLIC_WARS_1</Prereq>
    ...
  </Entry>
  -->
</Root>
```

### scenarioClass-add.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<Root>
  <Entry>
    <zType>SCENARIOCLASS_GALLIC_WARS</zType>
    <Name>TEXT_SCENARIOCLASS_GALLIC_WARS</Name>
  </Entry>
</Root>
```

---

## Chapter 1: The Helvetii and Ariovistus

### Scenario Settings

- **Nation**: NATION_ROME (player controls Caesar)
- **Turn Scale**: Weekly (custom TURNSCALE_WEEK, `iDivisions=52`), 35 turns total
- **Time Frame**: March-October 58 BCE (the campaign season)
- **No AI nations**: All non-player factions are tribes

---

## Turn Scale

Weekly turns at 35 turns for the campaign season (March through October 58 BCE). Each turn represents roughly one week.

Custom turn scale definition:
- `zType`: TURNSCALE_WEEK
- `iDivisions`: 52 (weeks per year)
- Turn names can use Roman calendar dates for flavor

### Pacing

| Phase | Approximate Turns | Events |
|-------|-------------------|--------|
| Rhone fortification | Turns 1-5 | Helvetii request passage, Caesar stalls, build forts |
| Pursuit & Arar | Turns 5-10 | Helvetii divert north, Caesar pursues, Saone ambush |
| Bibracte | Turns 10-14 | Supply crisis, march to Bibracte, the battle |
| Diplomatic interlude | Turns 14-18 | Gallic council, Ariovistus demands, seize Vesontio |
| Legion panic & approach | Turns 18-25 | Panic event, rally, march east |
| Vosges | Turns 25-30 | Parley, camps, battle |
| Resolution | Turns 30-35 | Aftermath, resettlement, victory |

---

## Tribes

All non-player factions are tribes (no AI nations). 5 new tribes + 1 existing base game tribe.

### Tribe Roster

| Tribe ID | Display Name | Diplomacy | Mercenary | Role | Team Color |
|----------|-------------|-----------|-----------|------|------------|
| TRIBE_HELVETII (new) | Helvetii | Yes | No | Primary antagonist Act 1. Large migrating army + civilians. | Orange/amber |
| TRIBE_SUEBI (new) | Suebi | Yes | No | Primary antagonist Act 2. Ariovistus's Germanic warriors. Aggressive, powerful. | Dark red |
| TRIBE_AEDUI (new) | Aedui | Yes | Yes | Roman allies. Political subplot (Dumnorix/Diviciacus). Provide grain & auxiliary cavalry. | Green |
| TRIBE_SEQUANI (new) | Sequani | Yes | No | Invited Ariovistus, now regret it. Appeal to Caesar for help. | Blue |
| TRIBE_BOII (new) | Boii | No | No | Minor hostile. Joined the Helvetii migration. Flank attack at Bibracte. | Brown |
| TRIBE_GAULS (existing) | Other Gauls | No | No | Generic minor Gallic groups: Allobroges, Ambarri, Tigurini, etc. | Default |

### Tribe Behavior Notes

- **Helvetii**: Should have a large army that moves across the map (migrating). Starts with diplomacy (requests passage), then becomes hostile. High unit count to represent 368,000 migrants.
- **Suebi**: Appears mid-scenario in the east. Extremely aggressive. High combat strength. Ariovistus as named leader.
- **Aedui**: Allied to Rome throughout. Never directly fights the player. Source of political events (Dumnorix subplot, grain supply issues). Provides auxiliary cavalry units via events.
- **Sequani**: Neutral/friendly. Their territory is where Ariovistus has settled. They appeal to Caesar for help, providing narrative motivation for Act 2.
- **Boii**: Part of the Helvetii migration. Appears as a flanking force during the Battle of Bibracte. Small but disruptive.

---

## Characters

### Roman Side (Player's Generals & Leaders)

| Character ID | Name | Role | Age (58 BCE) | Traits/Notes |
|-------------|------|------|-------------|--------------|
| CHARACTER_CAESAR | Julius Caesar | Player leader | 42 | Protagonist. Ambitious, brilliant. High stats across the board. |
| CHARACTER_LABIENUS | Titus Labienus | Senior legate | ~40 | Caesar's best general. Commands independently at the Arar ambush and Bibracte's left wing. High military rating. |
| CHARACTER_PUBLIUS_CRASSUS | Publius Crassus | Cavalry commander | ~26 | Son of triumvir Crassus. Young, aggressive. Commands the cavalry reserve that wins Bibracte. |
| CHARACTER_COTTA | Lucius Aurunculeius Cotta | Legate | ~45 | Reliable subordinate. Commands a legion. Important in later chapters. |
| CHARACTER_PEDIUS | Quintus Pedius | Legate | ~40 | Commands a legion. Caesar's nephew. |
| CHARACTER_DIVICIACUS | Diviciacus | Aeduan druid/diplomat | ~50 | Pro-Roman Aeduan leader. Pleads for his brother Dumnorix's life. Could serve as allied general unit representing Gallic auxiliaries. |

### Gallic & Germanic Side (Event Characters & Enemy Leaders)

| Character ID | Name | Faction | Role |
|-------------|------|---------|------|
| CHARACTER_ORGETORIX | Orgetorix | Helvetii | Nobleman who planned the migration. Conspired with Casticus and Dumnorix for pan-Gallic power grab. Dies (suicide or murder) before the migration starts. Intro events only. |
| CHARACTER_DIVICO | Divico | Helvetii | Elderly war chief. Led the Helvetii when they defeated Rome in 107 BCE. Meets Caesar for negotiations after the Arar - arrogant, reminds Caesar of the old defeat. |
| CHARACTER_DUMNORIX | Dumnorix | Aedui | Brother of Diviciacus. Secretly anti-Roman. Married to a Helvetian noblewoman. Sabotages Caesar's cavalry and Aedui grain supplies. Eventually exposed and placed under surveillance. |
| CHARACTER_ARIOVISTUS | Ariovistus | Suebi | Germanic king. Previously named "Friend of Rome" by the Senate. Demands half of Gaul. Refuses to meet Caesar on Caesar's terms. Huge, intimidating warriors. |
| CHARACTER_CASTICUS | Casticus | Sequani | Son of a former Sequani king. Co-conspirator with Orgetorix. Minor event role. |
| CHARACTER_LISCUS | Liscus | Aedui | Aeduan magistrate (vergobret). Reluctantly reveals Dumnorix's treachery to Caesar in a private meeting. |

---

## Narrative Event Chains

### Design Philosophy

- Events present what historically happened as narrative beats
- Player choices stay within the historical envelope (no alt-history branches)
- Choices offer tactical/resource trade-offs, not divergent storylines
- Caesar wrote the *Commentarii* in third person ("Caesar decided...") - event text can mirror this style for authenticity
- Battles are fought by the player on the map, with events providing narrative framing and light scripting for key story moments

### Act 1: The Helvetii (Turns 1-14)

#### Intro Event: The Migration Begins
- **Trigger**: EVENTTRIGGER_START_GAME
- **Narrative**: Caesar receives word that the Helvetii, a powerful Gallic people hemmed in by mountains, the Rhine, and the Rhone, have burned their twelve towns and four hundred villages. Under the influence of the nobleman Orgetorix (now dead - executed or suicide after his conspiracy was discovered), 368,000 men, women, and children march west seeking new lands. Caesar recalls that the Helvetii defeated consul Lucius Cassius Longinus in 107 BCE. Rome has a score to settle.
- **Subjects**: Caesar, Helvetii
- **Options**: "Continue" (single option - sets the stage)
- **Bonuses**: Activates Act 1 goals

#### Helvetii Embassy: Request for Passage
- **Trigger**: EventLink from intro (turn 2-3)
- **Narrative**: Helvetii ambassadors Nammeius and Verucloetius arrive requesting safe passage through Provincia. Caesar tells them he will consider the matter and to return on the Ides of April - buying precious time.
- **Options**: "Use the time wisely" (single option - activates Rhone fortification goal timer)
- **Bonuses**: Goal activated: "Fortify the Rhone" (build X forts/improvements along the river within Y turns)

#### Fortification Complete / Passage Denied
- **Trigger**: Rhone fortification goal completed OR timer expires
- **Narrative**: Caesar has built a 19-mile wall with watchtowers and redoubts along the south bank of the Rhone. When the Helvetii return for his answer, he formally denies passage. They attempt to cross anyway - by raft, by ford - but the fortifications hold. Frustrated, the Helvetii turn north to seek passage through Sequani territory instead.
- **Options**: "Pursue them" (single option)
- **Bonuses**: Helvetii army begins moving north across the map. Pursuit phase begins.

#### Dumnorix Subplot: The Grain Crisis
- **Trigger**: EventLink, fires during pursuit phase (turn 6-8)
- **Narrative**: Caesar has demanded grain from the Aedui as Rome's allies, but supplies are not arriving. Investigations reveal delays and excuses. Something is wrong.
- **Options**: "Investigate further" (leads to next event in chain)

#### Dumnorix Subplot: Liscus Reveals the Truth
- **Trigger**: EventLink from grain crisis
- **Narrative**: In a private meeting, Aeduan magistrate Liscus reluctantly reveals that Dumnorix - brother of the pro-Roman druid Diviciacus - has been sabotaging the grain supply. Dumnorix commands the Aedui cavalry, has married a Helvetian noblewoman, and is secretly working against Rome. He has been telling the Gauls that Caesar intends to conquer all of Gaul.
- **Options**: "Confront the situation" (leads to next event)

#### Dumnorix Subplot: Diviciacus Pleads
- **Trigger**: EventLink from Liscus event
- **Narrative**: Diviciacus comes to Caesar in tears, embracing him, begging him not to punish his brother harshly. He fears it will look like he, Diviciacus, used his Roman friendship to destroy his own brother. Caesar is moved by the display. He takes Dumnorix's hand and dismisses the others. He tells Dumnorix he forgives the past but expects loyalty going forward. He places Dumnorix under surveillance.
- **Options**:
  - "Place Dumnorix under watch" - Caesar spares him and assigns men to monitor his movements. (Grants intelligence/surveillance bonus, positive Aedui opinion)
  - "Publicly censure Dumnorix" - Caesar formally rebukes Dumnorix before the Aedui council but spares his life at Diviciacus's request. (Minor Aedui opinion hit, but Dumnorix is more thoroughly cowed)
- Both options lead to the same historical outcome: Dumnorix lives, is watched, and causes no more trouble this campaign.

#### Ambush at the Arar (Saone River)
- **Trigger**: EventLink or player's army reaches the Arar zone
- **Narrative**: Roman scouts report that three-quarters of the Helvetii have crossed the Saone, but one quarter - the Tigurini clan - remain on the near bank. The Tigurini are the very clan that killed consul Cassius and sent a Roman army under the yoke in 107 BCE. Caesar sees his chance for revenge.
- **Goal**: "Blitz at the Arar" - defeat the Tigurini/Helvetii units at the river crossing
- **Options**: "Attack at the third watch of the night" (single option - launches the battle)
- **Bonuses**: Combat bonus for the initial attack (surprise)
- **Post-battle event**: Caesar builds a bridge over the Saone in a single day, crossing to pursue the main Helvetii force. The Helvetii are stunned - it took them twenty days to cross.

#### Divico's Embassy
- **Trigger**: EventLink after Arar battle
- **Narrative**: The elderly war chief Divico, the same man who defeated Rome in 107 BCE, rides to Caesar's camp to negotiate. He is arrogant despite his defeat: "If Rome makes peace, the Helvetii will go wherever Caesar directs them. But if Caesar insists on war, he should remember what happened before. Let him not be so confident that this place becomes famous for Roman disaster." Caesar replies that he remembers the old defeat well - which is precisely why he will not let it happen again.
- **Options**: "Rome remembers its defeats" (single option - negotiations fail, the campaign continues)

#### Supply Crisis and March to Bibracte
- **Trigger**: EventLink, several turns after Arar
- **Narrative**: Roman grain supplies are running low. The Aedui have promised grain but it has not arrived (echoing the Dumnorix sabotage - even with him neutralized, logistics are difficult). Caesar makes the decision to break off pursuit and march toward Bibracte, the Aedui capital, to resupply. The Helvetii, seeing Caesar turn away, interpret it as retreat. They turn and pursue.
- **Options**: "March to Bibracte" (single option)
- **Bonuses**: Helvetii army turns aggressive, begins moving toward the player

#### Battle of Bibracte
- **Trigger**: Armies meet near Bibracte
- **Narrative intro event**: The Helvetii attack. Caesar sends his horse away - he will fight on foot with his men. He draws up his four veteran legions on a hillside, with the two newly raised legions and auxiliaries on the hilltop behind to guard the baggage.
- **This is a player-fought battle on the map.**
- **Mid-battle event (Boii/Tulingi flank)**: The Boii and Tulingi, who had been guarding the Helvetii baggage train, attack the Roman right flank. Caesar must fight on two fronts. The third line turns to face the new threat while the first two lines hold the main Helvetii attack.
- **Goal**: "Win the Battle of Bibracte" - defeat the main Helvetii army units
- **Post-battle event**: The Helvetii flee to a mountain and then to the territory of the Lingones. Caesar does not pursue for three days (his men are burying the dead and tending the wounded). He sends word to the Lingones: do not aid the Helvetii, or face the same treatment.

#### Helvetii Surrender
- **Trigger**: EventLink after Bibracte victory
- **Narrative**: The surviving Helvetii, starving and exhausted, send envoys to surrender. They throw themselves at Caesar's feet, weeping. Caesar demands hostages, weapons, and their runaway slaves. In the night, 6,000 from the Verbigeni canton try to slip away toward the Rhine - Caesar sends cavalry to bring them back and treats them as enemies. The rest he orders to return to their homeland and rebuild their burned towns - he does not want the fertile Helvetian lands left empty for Germanic tribes to fill. The Aedui are ordered to supply them with grain for the journey. Of the 368,000 who set out, only 110,000 return home.
- **Options**: "Send them home" (historical outcome)
- **Goal completed**: "Force Helvetii Resettlement"

### Act 2: Ariovistus (Turns 14-35)

#### The Council of Gaul
- **Trigger**: EventLink after Helvetii resolution
- **Narrative**: Gallic chiefs from across the land request a private meeting with Caesar. Led by Diviciacus, they beg for help. Ariovistus, king of the Germanic Suebi, crossed the Rhine years ago at the Sequani's invitation to help them fight the Aedui. But now Ariovistus has seized a third of Sequani territory - the finest land in all Gaul - and demands another third. His warriors are arrogant and cruel. More Germans cross the Rhine every year. If Caesar does not act, all Gaul will become Germania.
- **Options**: "Rome will address this" (single option - activates Act 2 goals)

#### Diplomatic Exchange with Ariovistus
- **Trigger**: EventLink from council
- **Narrative**: Caesar sends envoys to Ariovistus requesting a meeting. Ariovistus replies contemptuously: "If I needed something from Caesar, I would go to him. If Caesar needs something from me, he should come to me. I don't dare enter the part of Gaul that Caesar holds, and he shouldn't enter mine. I conquered these people by right of war. I don't tell Caesar how to govern his province. He shouldn't tell me how to govern mine."
- **Options**: "Prepare for war" (single option)

#### The Race to Vesontio
- **Trigger**: EventLink from diplomatic exchange
- **Narrative**: Caesar learns that Ariovistus is marching on Vesontio (Besançon), capital of the Sequani - the best-fortified town in the region, rich in military supplies. Caesar force-marches day and night and seizes the town first.
- **Goal**: "Seize Vesontio" - capture/reach Vesontio before Suebi units
- **Options**: "March day and night" (single option)

#### The Panic
- **Trigger**: EventLink after Vesontio is secured
- **Narrative**: At Vesontio, Roman officers and soldiers hear terrifying stories from Gallic traders about the Germanic warriors: their enormous size, their incredible ferocity, the terrifying expressions on their faces. They say no one can even meet their gaze. Panic spreads through the camp. Centurions who have no military experience - men who followed Caesar from Rome for political reasons - begin requesting leave, inventing excuses. Their fear infects the common soldiers. Men openly weep and write their wills.
- **Event**: Caesar calls a council. He delivers a speech: Why do they fear these Germans? Marius defeated them. The Helvetii defeated them regularly. Are Rome's legions less than the Helvetii? Ariovistus has been beaten before. And if the whole army is too afraid to follow, Caesar will march with just the Tenth Legion alone - he has no doubt of their loyalty, and they will serve as his praetorian guard.
- **Options**:
  - "March with the Tenth alone" - (historically accurate) The Tenth Legion is honored and shamed the others follow. Massive morale recovery. All legions declare readiness. (Legitimacy bonus, morale bonus to all units)
  - "Appeal to Roman honor" - Caesar reminds them of their ancestors' victories and their oath to Rome. A more measured approach. (Moderate morale bonus)
- **Goal completed**: "Rally the Legions"

#### Ariovistus's Parley
- **Trigger**: EventLink, armies approach each other
- **Narrative**: Ariovistus agrees to a meeting, but only if both parties come on horseback, attended by cavalry. Caesar doesn't trust his Gallic cavalry for this, so he mounts men of the Tenth Legion on Gallic horses (they joke they're being promoted from infantry to knights). During the meeting, Ariovistus's tone is threatening. He reminds Caesar that many powerful Romans would thank Ariovistus for killing Caesar. Suddenly, Germanic horsemen begin throwing javelins and stones at Caesar's escort. Caesar breaks off the meeting rather than escalate.
- **Options**: "Break off the parley" (single option)
- **Post-event**: Ariovistus positions his camp to cut Caesar's supply lines. Caesar builds a second, smaller camp 600 paces from the first.

#### Ariovistus Refuses Battle
- **Trigger**: EventLink from parley
- **Narrative**: For several days, Ariovistus avoids pitched battle, relying on cavalry skirmishes. Caesar learns from prisoners that Germanic women, casting lots and reading omens, have declared the Germans will not win if they fight before the new moon. Caesar decides to force the issue immediately.
- **Options**: "Attack now, while superstition holds them" (single option)

#### Battle of Vosges
- **Trigger**: Player attacks Suebi army
- **Narrative intro event**: Caesar assigns each of his five legates and his quaestor to command a legion, so every soldier knows they are being watched. Caesar himself takes the right wing, where the enemy line appears weakest. The Romans charge at the signal.
- **This is a player-fought battle on the map.**
- **Mid-battle event**: The fighting is so immediate and violent that the Romans cannot throw their javelins - they draw swords and fight hand-to-hand. Germanic warriors form a shield-wall (phalanx). Roman soldiers are seen leaping on top of the wall to pull shields aside and stab downward.
- **Mid-battle event (Crassus's charge)**: The Roman left wing is being pushed back. Young Publius Crassus, commanding the cavalry reserve, sees the danger before Caesar does and sends in the third line to reinforce. The tide turns.
- **Goal**: "Win the Battle of Vosges" - defeat the main Suebi army units
- **Post-battle event**: The Germanic army breaks and flees toward the Rhine, about five miles away. Ariovistus finds a small boat and escapes across the river. His two wives are killed in the rout. Roman cavalry pursues, cutting down the fleeing Germans. Gaul is free of Germanic domination.
- **Goal**: "Rout Ariovistus to the Rhine" (bonus - complete the rout within a turn limit)

#### Victory Resolution
- **Trigger**: All required goals completed
- **Narrative**: Caesar quarters his legions among the Sequani for the winter and departs for Cisalpine Gaul to hold his judicial assizes. In a single campaign season, he has crushed two enormous threats to Roman Gaul. His dispatches to the Senate result in an unprecedented fifteen days of public thanksgiving. The name of Caesar is on every Roman's lips.
- **Options**: "View Victory Screen" (opens victory tab)

---

## Player Goals

### Core Goals (Required for any victory)

| Goal ID | Name | Type | Description |
|---------|------|------|-------------|
| GOAL_GW1_BIBRACTE | Win the Battle of Bibracte | Military (bBlockComplete) | Defeat the main Helvetii army. Completed via event trigger when Helvetii units are destroyed near Bibracte. |
| GOAL_GW1_VOSGES | Win the Battle of Vosges | Military (bBlockComplete) | Defeat Ariovistus's Suebi army. Completed via event trigger when Suebi units are destroyed. |

### Secondary Goals

| Goal ID | Name | Type | Description |
|---------|------|------|-------------|
| GOAL_GW1_FORTIFY_RHONE | Fortify the Rhone | Timed build | Build X fort improvements along the Rhone river within Y turns. Activated by the Helvetii embassy event. |
| GOAL_GW1_ARAR_BLITZ | Blitz at the Arar | Military (bBlockComplete) | Defeat the Helvetii rearguard (Tigurini) at the Saone river crossing. Timed - must strike before they finish crossing. |
| GOAL_GW1_RALLY_LEGIONS | Rally the Legions | Event chain (bBlockComplete) | Successfully resolve the legion panic event before the Ariovistus campaign. Completed via event. |
| GOAL_GW1_DUMNORIX | Resolve the Dumnorix Affair | Event chain (bBlockComplete) | Complete the Dumnorix political subplot. Completed via event. |

### Bonus Goals

| Goal ID | Name | Type | Description |
|---------|------|------|-------------|
| GOAL_GW1_VESONTIO | Seize Vesontio | Military/race | Reach or capture Vesontio before Ariovistus's forces. |
| GOAL_GW1_RESETTLEMENT | Force Helvetii Resettlement | Event (bBlockComplete) | Complete the post-Bibracte resettlement event - send the surviving Helvetii home. |
| GOAL_GW1_ROUT_ARIOVISTUS | Rout Ariovistus to the Rhine | Timed military | After winning Vosges, complete the pursuit/rout within X turns. |
| GOAL_GW1_AEDUI_ALLIANCE | Secure Aedui Grain Supply | Diplomatic/event | Maintain positive relations with Aedui and resolve the grain supply issue. |

---

## Victory Tiers

| Tier | Requirements | Narrative Flavor |
|------|-------------|------------------|
| **Bronze** | Win Battle of Bibracte + Win Battle of Vosges | "You have secured Gaul, but at great cost and with little political gain. The Senate grants a polite thanksgiving." |
| **Silver** | Bronze + Fortify the Rhone + Blitz at the Arar | "Caesar's swift action at the Rhone and the Saone proved Rome's reach. The Senate takes notice - ten days of public thanksgiving are decreed." |
| **Gold** | Silver + Rally the Legions + Resolve Dumnorix Affair + Secure Aedui Grain Supply | "Through military brilliance and political cunning, Caesar has made himself master of Gaul and darling of Rome. Fifteen days of thanksgiving are decreed - unprecedented in Roman history." |
| **Epic** | Gold + Seize Vesontio + Force Helvetii Resettlement + Rout Ariovistus to the Rhine + complete both battles within specific turn windows | "Caesar's Commentarii will record this year as the beginning of legend. All Gaul trembles at Rome's power, and in the Forum, men whisper that a new Marius has arisen." |

---

## Map Design

### Geographic Scope

The map covers a roughly 350-mile west-to-east corridor from Bibracte to the Rhine, and about 200 miles north-to-south from Sequani territory down to Provincia (Roman Provence).

### Reference Maps

- **Overall Gaul with tribal territories**: [Map of Gaul in the Time of Caesar](https://www.emersonkent.com/map_archive/gaul_1st_cent_bc.htm) - Shows all tribal territories, major oppida, and rivers.
- **Campaign route & Ariovistus battle**: [Caesar's Campaign in Gaul, 58 BCE](https://www.emersonkent.com/map_archive/caesar_gaul.htm) - US Military Academy map showing the Helvetii route and the battle at Mulhouse.
- **Detailed maps from T.A. Dodge**: [Dickinson College - Gallic War Maps](https://dcc.dickinson.edu/subjects/gallic-war-maps?page=16) - The Rhone wall, both Helvetii migration routes, and Ariovistus battle.
- **Digital Maps of the Ancient World**: [Book I Maps](https://digitalmapsoftheancientworld.com/ancient-literature/the-gallic-war/the-gallic-war-book-i/) - Gaul overview, Bibracte battle, and Vosges battle maps.

#### Direct Image Links

- Gaul 1st Century BCE overview: `https://digitalmapsoftheancientworld.com/wp-content/uploads/2021/05/gaul_1st_century_bc.gif`
- Battle of Bibracte: `https://digitalmapsoftheancientworld.com/wp-content/uploads/2021/05/bataille_bibracte_-58.png`
- Battle of Vosges / Ariovistus: `https://digitalmapsoftheancientworld.com/wp-content/uploads/2021/05/1280px-battaglia_ariovisto_mulhouse_png.png`

### Terrain Zones

#### Western Zone: Aedui Heartland (Bibracte)

- **Bibracte** (Mont Beuvray): Hilltop oppidum, Aedui capital. Sits on a forested mountain ~800m elevation. Rolling agricultural hills surround it.
- **Terrain**: Green, fertile rolling hills. Mixed oak forest and farmland. Gentle river valleys. Breadbasket of Gaul - grain fields, pastures, cattle.
- **Rivers**: Upper Loire tributaries. The Arroux river runs nearby.
- **Old World tiles**: Grassland, light forest, farms. A few hills. Temperate, lush.

#### Central Zone: The Saone (Arar) River Corridor

- **The Saone/Arar River**: Runs roughly north-south. Wide, slow-moving river - Caesar says it flows "with incredible slowness, so you cannot tell by looking which way it flows."
- **Key crossing point**: Where 3/4 of the Helvetii crossed but the Tigurini clan was still on the near bank. Flat open ground on the east bank - good for Caesar's night attack.
- **Terrain**: Broad river valley with flat floodplains. Scattered forest on higher ground. The Jura Mountains rise to the east.
- **Old World tiles**: River, floodplain/grassland, some marsh near the river. Forest on flanks.

#### Eastern Zone: Sequani Territory & the Jura

- **Vesontio (Besancon)**: Sequani capital. Sits in a dramatic loop of the Doubs River - a natural fortress with the river wrapping almost entirely around the town, and a high hill closing the gap. Caesar seizes this as his base.
- **Jura Mountains**: Forested mountain chain running northeast-southwest. The Helvetii homeland (Switzerland) is on the other side. Dense forest, steep passes. One pass so narrow that carts can barely pass single-file.
- **Terrain**: Mountainous, forested, rugged. River valleys between ridges.
- **Old World tiles**: Hills, mountains, dense forest. Rivers cutting through valleys.

#### Far Eastern Zone: The Rhine Frontier & Alsace Plain

- **The Alsace Plain**: Between the Vosges Mountains (west) and the Rhine (east). Flat, open agricultural land. This is where the Battle of Vosges is fought.
- **Vosges Mountains**: Forested mountain range running north-south. Western wall of the Alsace plain.
- **The Rhine**: Major river forming the boundary between Gaul and Germania. Wide, powerful current. Ariovistus's escape route.
- **Battle of Vosges terrain**: Open plain. Caesar's two camps 600 paces apart. Ariovistus's wagon laager (wagons in a circle with women and children inside). Battle site ~5 miles from the Rhine.
- **Old World tiles**: Plains/grassland with Vosges hills/forest to the west, Rhine river to the east. Flat and open - cavalry country.

#### Southern Zone: Provincia (Roman Territory)

- **Genava (Geneva)**: Where the Rhone exits Lake Geneva. Caesar destroys the bridge here.
- **The Rhone**: Major river flowing from Lake Geneva southwest toward the Mediterranean. Caesar builds a 19-mile wall with watchtowers and redoubts along the south bank to block the Helvetii.
- **Lake Geneva (Lacus Lemannus)**: Large lake at the junction of Helvetii territory and Provincia.
- **Terrain**: Rhone valley is relatively narrow with hills on both sides. South of the Rhone is Roman territory - more developed, with roads and towns.
- **Old World tiles**: River, hills, some forest. Fort/improvement zone along south bank.

### Schematic Map Layout

```
NORTH
 |
 |    [Sequani territory]     [Vosges Mtns]  [Alsace Plain]  [RHINE]
 |         Vesontio o              ^^^         x Vosges       |||
 |              \                                             |||
 |   [Aedui territory]        [Jura Mountains]               |||
 |    Bibracte o  <-- x         ^^^^^^                        |||
 |         \        Bibracte      \                           |||
 |          \                      \   [Helvetii homeland]    |||
 |    ~~~Saone River~~~    x Arar crossing                    |||
 |              \                    \                        |||
 |               \              Lake Geneva                   |||
 |                \           Genava o === Rhone ===>         |||
 |            [PROVINCIA ROMANA]     ### Roman wall ###       |||
 |
SOUTH                                                     EAST

o = city/oppidum    x = battle site    ^^^ = mountains
~~~ = river         ### = fortification zone
```

### Battle Site Terrain Details

#### Rhone Fortification Zone
River with hills on both sides. Player builds forts along a ~19 tile stretch of the south bank. Helvetii appear on the north bank attempting to cross. Terrain should make crossing difficult without the fortifications destroyed.

#### Arar/Saone Crossing
Wide flat river with open ground on the east bank. The Tigurini are caught mid-crossing on flat terrain with nowhere to hide. Open, punishing terrain for the ambush.

#### Bibracte
Rolling hills. Caesar positions on a hillside:
- 4 veteran legions in front (downslope)
- 2 new legions + baggage on the hilltop behind
- Helvetii charge uphill from the southwest
- A mountain ~1 mile behind the Helvetii serves as their rally point
- The Boii and Tulingi attack from a different direction (the flank) - the terrain must allow for this multi-directional threat

#### Vosges
Open plain between the Vosges mountain foothills (west) and the Rhine (east). Flat, ideal for infantry formations.
- Caesar's main camp + smaller auxiliary camp 600 paces apart
- Ariovistus's wagon laager (defensive wagon circle)
- Rhine ~5 miles behind the German position (their escape route)
- Open terrain favoring Roman discipline over Germanic aggression

---

## Technical Reference

### Old World Scenario Mod Structure

Each scenario mod follows this convention:
- `ModInfo.xml` - Declares the mod as single-player scenario (`<scenario>true</scenario>`)
- `Maps/` - Contains scenario map files
- `Infos/` - Contains all XML definition files

File naming conventions:
- `*-add.xml` - Adds new entries to a base system
- `*-change.xml` - Modifies existing base game entries
- `text-*-add.xml` - Localization/text strings

### Mod Loading System

The game discovers mods by scanning both the bundled and user mod directories. For each mod:
1. `ModInfo.xml` is parsed to extract metadata, dependencies, and scenario flag
2. If `<scenario>true</scenario>`, the mod's `scenario-add.xml` entries are merged into the scenario registry
3. When a player selects a scenario, the engine looks up `zModName` and loads that mod's entire `Infos/` directory
4. All XML from the mod is merged — events/goals for other chapters are harmless since they're gated by scenario-specific triggers
5. The map file referenced by `zMapFile` is loaded from the mod's `Maps/` directory

There is no C# / DLL requirement. All scenario functionality (events, goals, tribes, characters, victory conditions, custom turn scale, custom map) is XML-driven. A DLL would only be needed for custom game logic (e.g., overriding year display format), which can be added later if desired.

### Key XML Systems

| System | File | Purpose |
|--------|------|---------|
| Scenario definition | `scenario-add.xml` | Registers the scenario with prereqs, nation, difficulty, locked params |
| Scenario class | `scenarioClass-add.xml` | Groups chapters into a campaign |
| Turn scale | `turnScale-add.xml` | Custom time divisions |
| Tribes | `tribe-add.xml` | Define new tribal factions |
| Characters | `character-add.xml` | Historical figures with traits, age, portraits |
| Events | `eventStory-add.xml` | Event definitions with triggers, subjects, options |
| Event options | `eventOption-add.xml` | Player choices with bonuses |
| Event triggers | `eventTrigger-add.xml` | What causes events to fire |
| Event links | `eventLink-add.xml` | Chain events together with turn delays |
| Event classes | `eventClass-add.xml` | Category grouping for events |
| Bonuses | `bonus-event-add.xml` | Concrete rewards/effects from events |
| Goals | `goal-add.xml` | Objectives with tracking conditions |
| Victory | `victory-add.xml` | Victory tier definitions |
| Difficulty | `difficulty-add.xml` | Custom difficulty levels |

### Goal Mechanics

- `GoalForce` in bonus-event: Forces a goal onto the player regardless of conditions
- `FinishGoal` in bonus-event: Immediately completes a `bBlockComplete` goal
- `bBlockComplete`: Goal can only be completed via event (not automatic tracking)
- `bScenario`: Marks as scenario goal (not a standard ambition)
- `iMaxTurns`: Turn limit for timed goals
- Goals can track: unit counts, improvement counts, tribes killed, cities captured, resources, stats, and more

### Victory Tiers

Victory types (VICTORY_CAMPAIGN_EPIC/GOLD/SILVER/BRONZE) are labels. Goals with `bVictoryEligible` determine what players must accomplish for each tier. Victory events fire via `EVENTTRIGGER_WIN_GAME` with `TriggerData` specifying the tier.

### Event Chain Pattern

1. Intro event fires on game start (`EVENTTRIGGER_START_GAME`)
2. Event option adds an `EventLinkAdd` to queue follow-up events
3. Follow-up events use `EventLinkPrereq` to fire after the link
4. `iTurnLimit` on links controls delay between events
5. `bImmediate` on links fires without delay
6. Events can grant goals (`GoalForce`), complete goals (`FinishGoal`), grant units/resources, or trigger further event chains

### Available Unit Types (Roman era)

- **Infantry**: UNIT_HASTATUS, UNIT_LEGIONARY, UNIT_CONSCRIPT, UNIT_SPEARMAN, UNIT_SWORDSMAN
- **Ranged**: UNIT_SLINGER, UNIT_ARCHER
- **Cavalry**: UNIT_HORSEMAN, UNIT_HORSE_ARCHER
- **Siege**: UNIT_BATTERING_RAM, UNIT_BALLISTA, UNIT_ONAGER
- **Support**: UNIT_WORKER, UNIT_SCOUT, UNIT_GENERAL, UNIT_SETTLER
- **Naval**: UNIT_BIREME, UNIT_TRIREME

### Existing Game Tribes (can rename or use as-is)

TRIBE_GAULS, TRIBE_VANDALS, TRIBE_DANES, TRIBE_THRACIANS, TRIBE_SCYTHIANS, TRIBE_NUMIDIANS, TRIBE_BARBARIANS, TRIBE_RAIDERS, TRIBE_REBELS, TRIBE_ANARCHY

# Roadmap

Forward-looking plan for the Gallic Wars v2 mod, organized from imminent to long-term. Each milestone passes the three-pillar check before becoming code (see `docs/design-pillars.md`).

---

## M0: Scaffold smoke test — DONE

- Scenario registers and launches as "The Helvetii Migration"
- Custom `TURNSCALE_GALLIC_4DAY` (iDivisions=91) active
- Date display shows "Day {0} (58 BCE)" — end-turn advances correctly
- 180×180 map renders; Caesar character placeholder; minimal scenario state (Game + Player + Caesar + base TribeDiplomacy)

---

## M1: Cities, tribes, starting forces (next)

### Cities to place at existing urban tiles

Per the user-confirmed mapping:

| Tile | City |
|---|---|
| (90, 18), (91, 18), (91, 19) | Narbo (3-tile city) |
| (122, 20) | Massalia |
| (124, 23) | Arelate |
| (71, 25) | Tolosa |
| (115, 52) | Vienna |
| (93, 55) | Gergovia |
| (134, 59) | Genava |
| (108, 71) | Decetia or Cabillonum (Aeduan) |
| (94, 72) | Bibracte |
| (85, 74) | Avaricum (Bourges) |
| (84, 77) | ??? (TBD — possibly second Avaricum tile?) |
| (80, 86) | Cenabum |
| (96, 90) | Agedincum (Sens) |
| (89, 95) | Noviodunum (Suessionum likely) |
| (85, 99) | Parisii capital (Lutetia) |

### New cities to add (not on user's source map)

| City | Coords | Why |
|---|---|---|
| Vesontio | (128, 76) | Sequani capital, Book 1 act 2 vs Ariovistus |
| Lugdunum | (113, 55) | Roman ally throughout |
| Burdigala | (45, 42) | Aquitania, Book 3 |
| Samarobriva | (81, 114) | Caesar's winter HQ, Books 2–6 |

### Helvetii burned ruins

Scatter `IMPROVEMENT_RUINS_1–4` across the NE plateau where the Helvetii's twelve oppida were:

- (141, 70) — RUINS_4 (Aventicum site, biggest oppidum)
- (138, 62) — RUINS_2 (northern canton)
- (144, 67) — RUINS_4 (central canton)
- (148, 73) — RUINS_2 (eastern canton)
- (153, 70) — RUINS_1 (far eastern village cluster)

### Tribes to define

| Tribe | Role | Cities |
|---|---|---|
| Helvetii | Antagonist (moving force) | **None** — burned everything |
| Aedui | Caesar's eventual ally | Bibracte, Decetia |
| Sequani | Wavering, hosts Ariovistus | Vesontio |
| Allobroges | Roman-allied (provides cavalry) | Vienna |
| Arverni | Future Book 7 enemy | Gergovia |
| Boii | Joins Helvetii migration | None |
| Suebi | Future Ariovistus, across Rhine | None |

Plus base tribes (REBELS, ANARCHY, BARBARIANS, RAIDERS, GAULS) in the diplomacy table — empty `<TribeDiplomacy />` crashes the game.

### Starting forces

At Genava (134, 59):

- Caesar (character unit, leadership aura concept)
- 1 Legion (only legion Caesar had in Transalpine Gaul on arrival)
- 2 Workers (for fort-building during the stall)

Order budget retuned from v1's inflated 200 → **~30–50 orders/turn** to enforce real decision pressure.

---

## M2: Opening event chain

### Intro event (turn 1)

Caesar's voice setting the scene — Gallia divided in three (mirroring the book's opening), Helvetii migration news, forced march from Rome to Genava narrated rather than played.

### Bridge decision (turn 1, three options)

| Option | Path |
|---|---|
| Burn the bridge + ask Helvetii to wait a fortnight | **Historical** — leads to wall + stall phase |
| Retreat to Narbo | Option A — Helvetii cross peacefully, ravage Provincia for ~8–10 turns, then chase from worse position |
| Declare war immediately | Battle on bad defensive ground in Provincia |

### Wall-building phase (turns 2–4ish, ~14 in-fiction days)

- Goal: 3 forts on Rhône tiles, 2 turns each to build, 2 workers available
- **Probe attack events** fire each turn — player chooses: detach legion / hold with workers / cede ground
- **Concurrent diplomatic events**:
  - Diviciacus arrives (Aedui plea: promise aid / sympathize-only / refuse)
  - Dumnorix scout report (subplot prelude)
  - Allobroges cavalry deal (accept / demand more / refuse)
- **Auxiliary unit deliveries via events**:
  - Massalia slingers (turn 2–3)
  - Allobroges horse (after deal accepted)
  - Provincial militia levies (turn 1–2)

### Wall outcome branch

- Goal met by deadline → Helvetii assaults repulsed → forced detour north
- Goal missed → line breaches → Roman positions damaged → harder pursuit phase

---

## M3+: Mid- to late-Book 1

- **Helvetii bypass** event when they go north via Sequani territory
- **Battle of the Arar (Saône)** — Tigurini canton destroyed before crossing
- **Pursuit to Bibracte** — possible re-up of Aedui alliance
- **Battle of Bibracte** — major Book 1 climax (act 1)
- **Diviciacus → Ariovistus plea** — transition to act 2
- **Ariovistus negotiation events** — diplomatic options before fighting
- **Vesontio winter occupation** — fortified base before Vosges
- **Battle of the Vosges** — Ariovistus defeated, Book 1 victory
- **Book 1 victory conditions** — tiered (decisive vs minor), based on which battles won, which alliances secured

---

## Cross-cutting deferred items

- **`azTurnNames` real dates** — currently "Day N (58 BCE)"; swap to "March 28–31, 58 BCE" via 52 explicit strings. Iteration 2 of M0 polish.
- **Generator script** — may reintroduce a `generate_scenario.py`-style tool when procedurally placing many cities/units. Currently hand-stitching is fine.
- **Harmony DLL** — may need one for behaviors XML can't express (v1's fort tracker is a precedent). Stay XML-only until something forces it.
- **Improvement build time overrides** — at 4-day turns, fort/improvement build counts need tuning via `improvement-change.xml`. Forts: 2 turns. Camps: 1. Roads: 4–5.
- **Unit movement tuning** — at 4-day turns, legions realistically march 60–80 miles = 6–8 tiles. Base game movement values likely need bumps for legions, less so for tribal levies.
- **Tile (84, 77)** — currently unidentified. Either a second Avaricum tile or a different town; needs clarification.
- **Tile (108, 71)** — likely Decetia or Cabillonum (Aeduan); confirm with user.

---

## Books 2–8 (long horizon)

Each book becomes its own scenario file (`SCENARIO_GALLIC_WARS_2`, etc.), potentially with its own `TurnScale`. The Greek and Egyptian campaigns ship per-book scenarios sharing a `scenarioClass` — same pattern we'll use.

| Book | Year | Key locations | Notes |
|---|---|---|---|
| 2 | 57 BCE | Samarobriva, Durocortorum, Bratuspantium | Caesar's first big northern campaign (Belgae) |
| 3 | 56 BCE | Brittany coast, Burdigala, Tolosa | Veneti naval, Crassus in Aquitania |
| 4 | 55 BCE | Argentoratum, Cantium | First Germans + first Britain |
| 5 | 54 BCE | Londinium, Aduatuca | Britain expedition + winter rebellion disaster |
| 6 | 53 BCE | Colonia area | Punitive Eburones + second Rhine bridge |
| 7 | 52 BCE | Cenabum, Avaricum, Gergovia, Alesia | Vercingetorix climax — the masterpiece |
| 8 | 51 BCE | Uxellodunum | Hirtius mop-up |

Each book runs through the three-pillar check before any XML is written:

1. Does it match the book?
2. Does it offer meaningful divergent options?
3. Does it give the player something to do each turn — events AND units?

---

## What's actually next this session if we keep going

The natural M1 unit of work:

1. Pick a city
2. Generate its `<City>` XML block (with name, family or tribe ownership, citizens, etc.)
3. Insert into the map XML at the right TileID
4. Deploy
5. Verify in-game

Then repeat for the next city. After ~5–6 cities we'd add a tribe, expand TribeDiplomacy, place a starting unit, etc. The whole M1 is a couple of sessions' work.

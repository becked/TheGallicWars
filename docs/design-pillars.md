# The Gallic Wars — Design Pillars

Three pillars guide every gameplay decision in this scenario mod. Each section below explains the principle and gives concrete examples of how it applies in Book 1.

---

## 1. Accuracy to the book

*Commentarii de Bello Gallico* is the source-of-truth narrative spine. Every major beat should be recognizable to someone who's read Caesar.

### What this means concretely

- **Opening matches the book**: scene-set with Gaul divided in three (Belgae, Aquitani, Celtae) per the famous opening; Caesar races north to Genava in 8 days; arrives at the Rhône bridge with one legion.
- **Helvetii are pre-scorched**: per Book 1 ch. 5, they burned their twelve oppida and four hundred villages *before* leaving home. So Aventicum and the rest do not exist as cities on our map — instead we scatter `IMPROVEMENT_RUINS_1–4` across the Swiss plateau (proposed coordinates: (141, 70), (138, 62), (144, 67), (148, 73), (153, 70)). When scouts head east, the destruction is visible. The Helvetii themselves are modeled as a **moving column**, not a settled tribe.
- **Sequence respects chronology**: Burn the bridge → envoys arrive → stall for a fortnight → build the 19-mile wall → repel probes → Helvetii go north via Sequani → chase to Bibracte → battle. Then Diviciacus appears, Aedui plea, Ariovistus phase, Vesontio occupation, Vosges battle.
- **Named figures and tribes match**: Diviciacus (Aedui), Dumnorix (subplot), Labienus (wall-watcher), Massalia (auxiliaries), Allobroges (cavalry via deal). Sequani capital **Vesontio** (128, 76) is still placed as a real city — the Sequani didn't migrate.
- **Real dates on every turn**: 4-day turns, ~52 turns covering March–October 58 BCE. `azTurnNames` (when implemented) gives literal date strings ("March 28–31, 58 BCE") so the player feels Caesar's diary, not abstract Turn N.

---

## 2. Events as decisions that diverge from history

The story is what *did* happen. The game is what *could* happen if the player makes different choices.

Our recurring pattern: each beat has 2–3 options, one historical and one or two counterfactuals that branch the narrative without breaking it.

### Worked examples

**Bridge decision (turn 1)** — three options:
- *Burn the bridge* + tell Helvetii to wait a fortnight (historical → leads to wall + stall + probe-battles)
- *Retreat to Narbo* (legitimacy penalty; Helvetii cross peacefully under their original request, ravage southern Provincia for ~8–10 turns; then the player chases them through ruined territory toward Bibracte — same destination as the historical path, but from a worse opening)
- *Declare war immediately* (battle on bad defensive ground in Roman Provincia — risk for reward)

**Wall outcome** — the fortify-the-Rhône goal has a deadline:
- 2 turns to build a fort, 2 workers, 3 forts needed
- If goal met by the deadline → Helvetii wall assaults repulsed → forced detour north
- If not met → line breaches → Roman positions take damage → campaign continues with a debuff

**Aedui plea (Diviciacus)** — three options:
- *Promise full aid* (locks in alliance that drives Ariovistus phase)
- *Sympathize without committing* (keeps options open; neutral consequence)
- *Refuse* (easier deal with Ariovistus later, but Aeduan hostility down the line)

**Allobroges cavalry deal**:
- *Accept terms*, *demand more* (risk negotiation collapse), *refuse* (no cavalry but no debt)

**Dumnorix subplot**:
- *Investigate*, *ignore*, or *seize him* (foreshadows Book 5 betrayal arc)

### The pattern

History is always one of the options. **Never the only one.** The player isn't railroaded into Caesar's exact choices — they're given Caesar's information and asked to make the call themselves. Bad calls have *consequences*, not game-over screens. Caesar himself worried publicly that the "peaceful Helvetii crossing" might happen if he did nothing; that becomes our Option A on the bridge decision.

---

## 3. Every turn has decisions — events AND units

Stall periods (like the historical 14-day wait while the wall is built) must not become dead zones. The solution is two layers running in parallel.

### Event layer (passive content the game gives the player)

- Each stall turn fires a scripted **Helvetii probe attack** at one of the three fort tiles — player must respond:
  - *Detach legion to repel* (drains forces from elsewhere)
  - *Hold the half-built fort with workers + auxiliaries* (risk damage, lose worker turn)
  - *Cede ground, retreat to redoubt* (free defenders to maintain other forts)
- Concurrent **diplomatic events** during the wait: Diviciacus arrives (turn 2–3), Allobroges chief offers cavalry (mid-stall), Dumnorix-conspiracy scout report
- **Auxiliary unit deliveries via events**: Massalia slingers (turn 2 or 3), Allobroges cavalry (after deal accepted), Provincial militia (early)

### Unit layer (things the player initiates with their own forces)

- **Workers** (2 of them): placed on the 3 fort tiles — forces prioritization. Which fort gets built first matters because a probe could hit the unfinished one. Spare worker can do road/improvement work elsewhere.
- **Legion**: positioning along the wall, ready to redeploy when a probe lands.
- **Caesar (character unit)**: leadership aura — adjacent units get bonuses. "Where is Caesar this turn" matters.
- **Cavalry** (when event-delivered): scout to figure out where Helvetii will probe next; correctly-scouted probes give defensive bonuses.
- **Order budget**: kept tight (~30–50 orders/turn, not v1's inflated 200) so unit moves are deliberate, not free.

### What a stall turn actually feels like

Turn 3 of the 14-day stall:

> **Event 1 — Probe at the Northern Ford**
> Helvetii skirmishers test the line near where Worker A is still building the rampart (fort 60% complete). A small skirmish force crosses.
> - *A:* Detach Legion from south (costs orders, fort south becomes vulnerable)
> - *B:* Hold the half-built fort with workers + auxiliaries (risk damage, lose worker turn)
> - *C:* Allow the crossing, retreat to redoubt (cede ground, free defenders)
>
> **Event 2 — Diviciacus Arrives**
> Aedui envoy kneels before Caesar's command tent. Asks for Roman protection against Ariovistus.
> - *A:* Promise aid (foreshadowing alliance, +Aedui opinion)
> - *B:* Sympathize without commit (neutral)
> - *C:* Refuse (–Aedui opinion, easier Ariovistus deal later)
>
> **Player's turn proper:**
> - Place workers for next fort tile
> - Move legion in response to probe outcome
> - Send scouting cavalry north (if delivered)
> - Position Caesar where leadership aura helps most

That's a full turn worth of decisions, not a "press end turn and wait" moment.

---

## The thread that ties all three together

Caesar's strategic situation in 58 BCE was *intense*. Short on troops, racing time, juggling tribal diplomacy, trying to build a wall while being probed daily. We want to replicate that **feeling**, not just the bullet points.

- The **book** gives us the scaffold (what happened, when, where, who).
- The **events** give the player meaningful narrative agency (could it have gone differently?).
- The **per-turn micro-decisions** (worker placement, unit position, event response) keep the pressure constant rather than appearing only at climactic moments.

When designing any new content — Book 2 (Belgae), Book 3 (Veneti), Book 7 (Vercingetorix) — check it against these three pillars before writing XML.

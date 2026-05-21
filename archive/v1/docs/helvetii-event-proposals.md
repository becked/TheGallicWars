# Helvetii Campaign — Revised Event Proposals

Revised event chain for Act 1 (the Helvetii, turns 1–14), informed by three sources:

- `1-the-helvetii-campaign.txt` — detailed walkthrough of Book I
- `gallic-wars-scenario-design.md` — our original event design
- `event-design-lessons.md` — takeaways from Soren Johnson's Designer Notes

## Guiding Principles

1. **Every event should touch the game state.** No pure "Continue" events. Even single-option narrative beats should grant or cost something — Orders, resources, combat bonuses, units, opinion shifts. The player should feel the story in their economy and army, not just in text boxes.

2. **Characters drive events, events change characters.** Dumnorix, Labienus, Diviciacus, and Divico should feel like actors with agency, not narration props. Where possible, events should be *about* a character doing something that creates a gameplay consequence.

3. **Choices within the historical envelope.** We're not doing alt-history, but Caesar's account often presents moments where he weighed options or made judgment calls. Those are real choice points. Even where the outcome is fixed, the *method* can vary and carry different costs.

4. **Missing episodes matter.** The original design omits several episodes that are mechanically interesting: Caesar's army buildup, Dumnorix brokering the Sequani detour, the cavalry skirmish, the aborted ambush / Considius panic, and the Aemilius desertion. These are opportunities, not filler.

---

## Event-by-Event Proposals

### 1. INTRO: The Migration Begins

**Trigger**: EVENTTRIGGER_START_GAME
**Source**: Walkthrough items 1–4

The original intro is good but should do more than "Continue." Caesar has just one legion (Legio X) and is racing to Geneva. The opening should establish urgency and scarcity.

**Narrative**: Word reaches Caesar in Rome: the Helvetii have burned their towns and are marching west — 368,000 souls, including fighting men who once humiliated Rome. Caesar rides hard for Geneva with what forces he has. He arrives to find a single legion and raw provincial levies standing between Gaul and catastrophe. The bridge at Geneva must be destroyed immediately.

**Options**:
- **"Destroy the bridge and prepare"** — Bridge at Geneva is destroyed (narrative). Player receives a small bonus to Civics (Caesar's administrative speed). Activates the Rhone fortification goal.

**Mechanical effects**:
- Goal activated: GOAL_GW1_FORTIFY_RHONE
- Small Civics bonus (representing Caesar's famed organizational ability)
- Sets the stage: the player starts with limited forces and must build

**Design note**: The player's starting army should reflect the historical reality — one veteran legion plus levies. The full army arrives later (see event #4).

---

### 2. HELVETII EMBASSY: Request for Passage

**Trigger**: EventLink from intro, ~turn 2
**Source**: Walkthrough item 5

**Narrative**: Helvetii ambassadors Numeius and Verudoctius arrive at Geneva requesting safe passage through the Province. It is a reasonable request, politely made. Caesar faces a calculation: he needs time. He tells the ambassadors he will consider the matter and they should return on the Ides of April.

**Options**:
- **"Tell them to return on April 12th"** — Buys time. +2 bonus turns on the Rhone fortification goal timer. (Caesar's actual stalling tactic.)
- **"Demand hostages as a condition"** — More aggressive. No extra time, but if the Helvetii later attack the wall, player gets a diplomatic bonus (they broke terms). Small Civics cost (the demand requires formal negotiation).

**Mechanical effects**: Adjusts the fortification goal timer or provides a future combat/opinion bonus. Either way, the player is making a real resource decision about how to use the diplomatic moment.

---

### 3. PASSAGE DENIED: The Wall Holds

**Trigger**: Rhone fortification goal completed, OR timer expires
**Source**: Walkthrough items 6–8

Same as original design, but with consequences for success vs. failure:

**If fortification goal completed**:
- **Narrative**: Caesar's wall — 19 miles of trenches, ramparts, and redoubts — stands complete. The Helvetii return for his answer. Caesar denies passage. They attempt to force the crossing by raft and ford, but the fortifications hold. Frustrated, the Helvetii turn north.
- **Bonus**: Training bonus (the legionaries are hardened by the construction work). Legitimacy.

**If timer expired (wall incomplete)**:
- **Narrative**: The fortifications are incomplete when the Helvetii return. Caesar denies passage anyway. The Helvetii probe the weaker sections — there are anxious hours — but the natural terrain of the Rhone and what defenses exist are enough to deter a full crossing. The Helvetii turn north, seeking the Sequani route. It was close.
- **Bonus**: None. The player missed the window. No penalty beyond lost opportunity.

---

### 4. NEW — DUMNORIX BROKERS THE DETOUR

**Trigger**: EventLink from Passage Denied, ~1 turn later
**Source**: Walkthrough item 9

This episode is absent from our original design but is important: it's our first hint that Dumnorix is working against Rome, and it explains *how* the Helvetii get around Caesar's wall.

**Narrative**: Reports reach Caesar that the Helvetii have found a route — not through the Province, but through the narrow Jura pass into Sequani territory. Someone brokered this passage and arranged mutual hostages. Caesar's intelligence suggests Dumnorix of the Aedui, a man with troubling connections, was the intermediary. But there is no proof yet, and the Aedui are Rome's allies.

**Options**:
- **"Note it. We will deal with Dumnorix later."** — Sets a flag/trait on Dumnorix that makes the later exposure event more impactful. No immediate action. (Historically accurate — Caesar bided his time.)
- **"Send agents to watch Dumnorix now"** — Costs Civics (intelligence operation). Provides earlier warning in the Dumnorix chain — the grain crisis event fires sooner or with better information.

**Design note**: This is the "emergent layering" principle from the designer notes. Dumnorix's treachery isn't a self-contained subplot; it starts here and ripples forward through the cavalry skirmish and grain crisis.

---

### 5. NEW — CAESAR GATHERS HIS ARMY

**Trigger**: EventLink from Passage Denied, simultaneous with or just after event #4
**Source**: Walkthrough items 10–13

The original design skips this entirely, but it's Caesar's most dramatic logistical feat in Book I: leaving Labienus at the wall, sprinting to Italy, raising two new legions, collecting three more from winter quarters, and fighting through hostile Alpine passes to return.

**Narrative**: Caesar leaves Labienus in command of the Rhone fortifications and rides for Cisalpine Gaul at maximum speed. He levies two new legions, collects three veteran legions from their winter quarters at Aquileia, and marches back over the Alps — fighting off the Centrones, Graioceli, and Caturiges who try to block the passes. Seven days later, he crosses into Transalpine Gaul with six legions at his back.

**Options**:
- **"Force-march over the Alps"** — The army arrives at full strength but fatigued. All new units spawn, but with some damage or a temporary movement penalty (representing the exhausting march). +Orders this turn (Caesar's energy is infectious).
- **"March carefully through the passes"** — No fatigue penalty on the new units, but no Orders bonus either. Safer but slower (event fires one turn later, or one fewer bonus turn before the pursuit phase).

**Mechanical effects**: This is the moment the player's army jumps from one legion to six. It should feel like a major power spike — but with a cost attached, per the designer notes principle. The Alpine crossing isn't free.

**Design note**: Labienus being "left at the wall" could be reflected mechanically — his general unit is unavailable for the first few turns, then rejoins after this event. This makes him feel like a character with a role, not just a unit.

---

### 6. GAULS BEG FOR HELP

**Trigger**: EventLink, ~1 turn after army arrives
**Source**: Walkthrough item 14

Another missing episode. Before the Saone battle, the Helvetii are ravaging Aedui lands, and multiple Gallic peoples send desperate embassies to Caesar.

**Narrative**: The Aedui, the Ambarri, and the Allobroges all send embassies to Caesar. The Helvetii are ravaging their lands — burning fields, carrying off cattle, seizing people. The Aedui, Rome's oldest allies in Gaul, beg Caesar to intervene before they are utterly destroyed. The Ambarri, kinsmen of the Aedui, report that their territory has been stripped bare. Even the Allobroges, whose lands across the Rhone should have been safe, have been raided. There is no more time for caution.

**Options**:
- **"We march to relieve the Aedui"** — Grants a movement bonus (forced march) for this turn. Positive Aedui opinion. Sets up the pursuit phase.
- **"Demand the Aedui provide cavalry and grain first"** — No movement bonus, but guarantees a small resource delivery (Food/Training). Caesar leverages the alliance for material support before committing. Slight Aedui opinion cost (they're being made to bargain while their lands burn).

**Mechanical effects**: Establishes the Aedui relationship as transactional — the player is making choices about how to manage the alliance, not just reading about it. This feeds forward into the grain crisis.

---

### 7. AMBUSH AT THE ARAR

**Trigger**: EventLink or army reaches the Arar zone
**Source**: Walkthrough items 15–16

Largely unchanged from original design, but with sharper mechanical teeth.

**Narrative**: Roman scouts report that three-quarters of the Helvetii have crossed the Saone, but the Tigurine canton — the very people who killed consul Cassius and sent a Roman army under the yoke fifty years ago — remain on the near bank, still crossing. Caesar sees his chance.

**Options**:
- **"Attack at the third watch"** — Night attack. Grants a significant combat bonus (surprise + darkness) to all units this turn. +Orders (Caesar roused the army at midnight). Goal activated: GOAL_GW1_ARAR_BLITZ — destroy the Tigurini units within 1–2 turns.

**Post-battle event** (fires when goal completed):
- **Narrative**: The Tigurini are shattered. The survivors flee into the woods. Caesar builds a bridge across the Saone in a single day and crosses with his entire army. The Helvetii are stunned — it took them twenty days to make the same crossing. Rome's speed is its own weapon.
- **Bonus**: Free road improvement on the Saone crossing tile (representing the bridge). Training bonus from the victory.

---

### 8. DIVICO'S EMBASSY

**Trigger**: EventLink after Arar victory
**Source**: Walkthrough item 17

The original design has this as a single-option narrative. It deserves more.

**Narrative**: The elderly war chief Divico rides to Caesar's camp. He is the same man who defeated Rome in 107 BCE — old now, but unbowed. His words are carefully chosen: "If Rome makes peace, the Helvetii will go wherever Caesar directs. But if Caesar insists on war, he should remember what happened to Rome before. Let him not be so confident that this place becomes famous for Roman disaster." Caesar's reply is cold: Rome remembers its defeats very well, which is precisely why there will be no mercy.

**Options**:
- **"Demand hostages and reparations to the Aedui"** — Historically accurate. Caesar makes maximum demands he knows the Helvetii won't accept. Negotiations fail, but Caesar has the moral high ground — he offered terms. Small Legitimacy bonus. The pursuit continues.
- **"Tell Divico that Rome has already answered at the Arar"** — Caesar dismisses the embassy curtly. More aggressive. No Legitimacy, but +Orders this turn (the army's blood is up, no time wasted on diplomacy). Helvetii morale does not recover (they get no reprieve from the relentless pursuit).

**Design note**: Divico should feel like a real antagonist here — not just flavor text. His embassy is the last moment of Helvetii agency before they're ground down. The choice is about what kind of commander the player's Caesar is: politically shrewd or relentlessly aggressive.

---

### 9. NEW — THE CAVALRY SKIRMISH

**Trigger**: EventLink, 1–2 turns after Divico's embassy
**Source**: Walkthrough item 18

Missing from the original design. This is a Dumnorix episode — his Aedui cavalry causes a rout — and a mechanical setback that makes the campaign feel less like a triumphant march.

**Narrative**: Caesar sends his 4,000-strong cavalry — legionary horse, provincial riders, and the Aedui contingent under Dumnorix — to harass the Helvetii rearguard. The pursuit goes too far. A mere 500 Helvetii horsemen turn and countercharge. The Aedui cavalry breaks first, panicking the whole force. The Roman horse flee back to the column in disorder. It is a humiliation. And whispers in the camp blame Dumnorix for deliberately leading the rout.

**Options**:
- **"Discipline the cavalry commanders"** — Costs Civics. Cavalry units recover faster (reduced damage/fatigue penalty). But Dumnorix is publicly embarrassed, which will make the later confrontation more charged.
- **"Press the pursuit on foot — we don't need cavalry"** — No Civics cost, but cavalry units remain weakened for longer. Infantry gets a small movement bonus (double-time march). Caesar adapts rather than punishes.

**Mechanical effects**: The player takes an actual setback — cavalry units are damaged or debuffed. This makes the Helvetii feel dangerous and creates a mid-campaign valley before the climb to Bibracte. It also deepens the Dumnorix thread: his name keeps coming up in bad contexts.

---

### 10. THE GRAIN CRISIS

**Trigger**: EventLink, fires during pursuit phase
**Source**: Walkthrough items 19–20

Restructured from the original three-event Dumnorix chain. The walkthrough shows the grain crisis, the Dumnorix exposure, and the Diviciacus plea as three rapid beats in a single episode. We should keep that pacing but make the earlier Dumnorix hints (events #4 and #9) pay off here.

**Narrative**: Caesar has demanded grain from the Aedui — Rome's allies owe this much. But the grain does not come. Day after day, excuses: the harvest is not ready, the carts are delayed, the roads are bad. Caesar summons Diviciacus and the Aeduan magistrate Liscus. In a tense private meeting, Liscus finally breaks: it is Dumnorix. He arranged the Helvetii's passage through Sequani territory. He commanded the cavalry that routed at the skirmish. He married Orgetorix's daughter. He has been telling the Gauls that Caesar means to conquer all of Gaul and make himself king. He controls the Aedui grain supply, and he has been withholding it.

**Options**:
- **"Summon Dumnorix"** — Leads immediately to the next event (Diviciacus pleads). The historical path.

**Mechanical effects**: Food/resource penalty representing the supply shortage. The player should feel the grain crisis in their economy — units might take attrition damage, or the player loses stored Food. This is not just a story; it's a logistics problem.

---

### 11. DIVICIACUS PLEADS FOR HIS BROTHER

**Trigger**: EventLink from grain crisis (immediate, same turn if possible)
**Source**: Walkthrough item 21

This is the emotional heart of the Dumnorix arc and the one moment with a genuine player choice. Keep it from the original design, but enrich the options.

**Narrative**: Before Caesar can act, Diviciacus comes to him — in tears, embracing him, begging. "Do not punish my brother harshly. I fear people will say I used my friendship with Rome to destroy my own family. If that happens, every Gaul will turn against me, and against you." Caesar is moved. He takes Dumnorix by the hand, dismisses the others, and speaks to him alone.

**Options**:
- **"Pardon him and set a watch"** — (Historical.) Caesar forgives the past but assigns men to monitor Dumnorix. Positive Aedui opinion (Diviciacus is grateful, the alliance holds). Grain supply partially restored (+Food). But Dumnorix remains a latent threat — flag for Chapter 5 where he becomes a major problem again. Costs nothing.
- **"Pardon him, but strip his cavalry command"** — Caesar is merciful but firm. Dumnorix keeps his life but loses military authority. Aedui opinion is neutral (Diviciacus is relieved, but the family is diminished). Grain supply fully restored (Dumnorix can no longer interfere). Player gains a small Training bonus (the cavalry is reorganized under Roman officers). Dumnorix's flag is set differently for future chapters.
- **"Publicly censure him before the Aedui council"** — Caesar makes an example. Negative Aedui opinion (Diviciacus is humiliated along with his brother). But the grain crisis is fully resolved AND the player gains a Civics bonus (Caesar's authority over the Gauls is established). The most politically aggressive option.

**Design note**: All three options lead to the same immediate outcome (Dumnorix lives, the campaign continues), but they produce different resource effects *now* and set different flags for *later*. This is the designer notes principle of choices within the historical envelope — the story doesn't branch, but the gameplay does.

---

### 12. NEW — THE ABORTED AMBUSH (CONSIDIUS)

**Trigger**: EventLink, 1–2 turns after Dumnorix resolution, as armies near Bibracte
**Source**: Walkthrough items 22–23

Completely absent from the original design. This is a fascinating episode: Caesar attempts a brilliant night flanking maneuver, but a panicking scout (Considius) ruins it with a false report. It's a *failure* — and failures make campaigns feel real.

**Narrative**: Caesar devises a plan. A mountain overlooks the Helvetii camp, eight miles away. He sends Labienus with two legions to seize the summit by night, then attack at dawn while Caesar advances from the front. The scout Publius Considius, reputed an experienced soldier, is sent ahead to confirm Labienus has taken the position. At dawn, Considius gallops back in a panic: the enemy holds the summit! Their arms and insignia are Gallic! Caesar pulls back and deploys for defense. Hours pass. Finally, scouts confirm the truth: Labienus holds the mountain. Considius imagined the whole thing. The opportunity is gone — the Helvetii have moved on.

**Options**:
- **"We have lost a day, but not the campaign"** — Caesar accepts the setback stoically. No bonus, no penalty. The pursuit continues. (The restraint itself is the point — Caesar doesn't punish Considius, he just moves on.)
- **"Considius will answer for this"** — Caesar makes an example of the scout. Small Training bonus (discipline is reinforced), but small Legitimacy cost (punishing a man for honest fear sits poorly with some officers).

**Mechanical effects**: This event costs the player a turn of momentum — the Helvetii gain distance. It also gives Labienus a moment in the spotlight as an independent commander, which is what the designer notes mean by characters having agency. Labienus did his job; the failure was elsewhere.

**Design note**: Consider making this event conditional — it only fires if the player's army is within a certain distance of the Helvetii, representing the opportunity that existed. If the player is too far behind (poorly managed pursuit), the ambush opportunity never arises and the event is skipped. This is a reward for good play that then gets taken away by bad luck — dramatically effective.

---

### 13. NEW — THE DESERTER (AEMILIUS)

**Trigger**: EventLink, fires as Caesar turns toward Bibracte
**Source**: Walkthrough item 24

Another missing episode with real mechanical consequences.

**Narrative**: Caesar, short on supplies, turns his column toward Bibracte to resupply from the Aedui capital. But a Gallic cavalry officer, Lucius Aemilius, deserts in the night and rides to the Helvetii camp. He tells them Caesar has turned away. The Helvetii interpret this as retreat. Emboldened, they reverse course and pursue. The hunter becomes the hunted.

**Options**:
- **"Let them come"** — (Historical.) Caesar accepts the reversal. The Helvetii army becomes aggressive and moves toward the player. Narrative-only option — the mechanical consequence is the Helvetii behavior change, which is significant on its own.

**Mechanical effects**: Helvetii units switch from retreating/passive to aggressive/pursuing. This is a major map-state change triggered by a character's betrayal. The player was chasing; now they're being chased. It should feel like a sudden shift.

**Design note**: Aemilius is a minor character, but his desertion has outsized consequences. This is exactly what the designer notes mean by characters justifying change — a single act of betrayal transforms the tactical situation.

---

### 14. BATTLE OF BIBRACTE — DEPLOYMENT

**Trigger**: EventLink or proximity trigger as armies converge near Bibracte
**Source**: Walkthrough items 25–26

**Narrative**: The Helvetii attack from the rear as Caesar's column approaches Bibracte. Caesar sends away his horse — and those of every officer — so that all face equal danger and no one can flee. He draws up his four veteran legions on a hillside, with the two raw legions and the auxiliaries on the summit to guard the baggage. The Helvetii form their phalanx and charge uphill.

**Options**:
- **"We fight on foot, with the men"** — All units near Bibracte receive a combat bonus (morale from Caesar's presence). +Orders this turn (the army fights with desperate energy).

**Mechanical effects**: This is the pre-battle buff. It should be meaningful — the player is about to fight the biggest battle of the campaign. The horse-sending-away detail is great flavor, but the real mechanical hook is the Orders burst: the player has more actions this turn to position their forces.

---

### 15. BATTLE OF BIBRACTE — BOII FLANK

**Trigger**: Mid-battle (turn after deployment, or when main Helvetii units are engaged)
**Source**: Walkthrough item 27

Kept from the original design, but with sharper mechanical impact.

**Narrative**: As the Roman line pushes the Helvetii phalanx back, 15,000 Boii and Tulingi — who had been guarding the Helvetii baggage train — slam into the Roman right flank. The Helvetii rally. Caesar must fight on two fronts. The third line wheels to face the new threat.

**Mechanical effects**: Boii/Tulingi units spawn or activate on the player's flank. This should be a genuine tactical crisis — new hostile units appearing from an unexpected direction mid-battle. The player's existing formation must adapt. No choice here; it's a pure complication.

**Design note**: The timing should be keyed to the player engaging the main Helvetii force, not a fixed turn. If the player hasn't attacked yet, the flank attack doesn't trigger — it only fires when they're committed and can't easily reposition.

---

### 16. BIBRACTE — AFTERMATH

**Trigger**: GOAL_GW1_BIBRACTE completed (Helvetii army defeated)
**Source**: Walkthrough items 28–29

**Narrative**: The battle rages from noon to nightfall, then into the night as the Romans storm the Helvetii wagon laager. By morning, the Helvetii are broken. The survivors — perhaps 130,000 of the 368,000 who set out — flee toward Lingones territory. Caesar does not pursue for three days: his men are burying the dead and tending the wounded. He sends word to the Lingones: give no aid to the fugitives, or face the same consequences.

**Options**:
- **"Rest the army and tend the wounded"** — All units heal. +Food from captured Helvetii supplies. 2–3 turn pause before the surrender event (historically accurate).
- **"Pursue immediately"** — No healing, but the Helvetii surrender event fires sooner. Training bonus (relentless aggression). This is ahistorical but offers a tempo choice.

---

### 17. HELVETII SURRENDER & RESETTLEMENT

**Trigger**: EventLink from Bibracte aftermath
**Source**: Walkthrough items 29–31

**Narrative**: The surviving Helvetii send envoys. They throw themselves at Caesar's feet, weeping. Caesar demands hostages, arms, and the return of all deserters. That night, 6,000 from the Verbigeni canton slip away toward the Rhine. Caesar's cavalry hunts them down and treats them as enemies. The rest he orders to return to their burned homeland and rebuild. He will not leave those fertile lands empty for Germanic tribes to fill. The Aedui are ordered to supply grain for the journey home. Tablets found in the Helvetii camp, written in Greek characters, record the census: 368,000 departed. 110,000 return.

**Options**:
- **"Send them home"** — (Historical.) Positive Aedui opinion (the threat to their lands is over). Legitimacy bonus. Goal completed: GOAL_GW1_RESETTLEMENT.
- **"Settle the Boii among the Aedui"** — (Also historical — the Aedui requested this.) Additional Aedui opinion bonus. Sets up a minor future callback for later chapters (the Boii become part of the Aedui political landscape).

**Mechanical effects**: Large Legitimacy reward. Aedui opinion boost. The census detail (368,000 → 110,000) should appear in the event text — it's one of the most haunting details in the Commentarii and drives home the scale of what just happened.

---

## Summary of Changes from Original Design

### New events added (4):
- **Dumnorix brokers the detour** (#4) — first hint of treachery, seeds the subplot
- **Caesar gathers his army** (#5) — the Alpine march and army power-spike
- **The cavalry skirmish** (#9) — Dumnorix-linked setback, mid-campaign valley
- **Gauls beg for help** (#6) — Aedui/Ambarri/Allobroges embassies, alliance management
- **The aborted ambush / Considius** (#12) — a failure, Labienus spotlight
- **The deserter Aemilius** (#13) — triggers the Helvetii reversal at Bibracte

### Events restructured:
- **Grain crisis + Dumnorix** — collapsed from three events to two (the setup is now spread across events #4, #9, and #10 instead of being a self-contained chain)
- **Divico's embassy** — upgraded from single-option to a real choice
- **Helvetii embassy** — upgraded from single-option to a real choice
- **Bibracte aftermath** — split from surrender, given its own choice

### "Continue" events eliminated or enriched:
Every event now either (a) offers a meaningful choice or (b) delivers a significant mechanical effect even as a single option. No event is purely narrative text with a "Continue" button that changes nothing.

### Character usage:
| Character | Events where they have agency |
|-----------|-------------------------------|
| Caesar | All (as player proxy) |
| Labienus | #5 (left at wall), #12 (aborted ambush — he succeeds, Considius fails) |
| Dumnorix | #4 (brokers detour), #9 (cavalry rout), #10 (exposed), #11 (confronted) |
| Diviciacus | #6 (begs for help), #10 (grain crisis), #11 (pleads for brother) |
| Divico | #8 (embassy — antagonist with real presence) |
| Liscus | #10 (reveals the truth) |
| Considius | #12 (his panic ruins the ambush) |
| Aemilius | #13 (desertion flips the tactical situation) |

### Dumnorix thread:
Instead of a self-contained three-event subplot, Dumnorix now appears across five events (#4, #9, #10, #11, and implicitly #6). Each appearance deepens suspicion until the reveal. This is the "emergent layering" principle — his treachery isn't a detour from the campaign, it's woven through it.

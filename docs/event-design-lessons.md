# Event & Story Design Lessons from Old World Designer Notes

Takeaways from Soren Johnson's [Designer Notes](old-world-designer-notes/) applied to our Gallic Wars scenario.

## 1. Emergent stories > scripted storylines (DN #9)

Johnson's key insight is the "virtual deck" model — events are standalone pieces that combine emergently. One writer creates "leader becomes a Drunk," another writes an event requiring a Drunk leader, and "these two writers have now created a little story without discussing anything."

**For us**: Our event chains are heavily scripted and linear (eventLink after eventLink). That's fine for a scenario — we *want* to tell Caesar's story. But where we can, we should look for opportunities to let events layer on each other rather than just march in a fixed queue. For example, the Dumnorix subplot could set a character trait/state that unlocks *optional* later events, rather than being a self-contained chain that ends and is forgotten.

## 2. Events should affect the game state you're already managing (DN #9, #5)

Johnson's example: "perhaps an event provides a sudden burst of Orders that allows the player to move enough units to defend a city." Events are most powerful when they interact with systems the player is already thinking about (Orders, yields, unit positions).

**For us**: Many of our events currently resolve as "Continue" (single option, narrative-only). The design doc shows this pattern a lot — only the Dumnorix and Panic events have real choices. We should look for more places where events deliver meaningful gameplay consequences: bonus Orders for a surprise attack, Training or Civics from diplomatic wins, temporary combat buffs, or resource costs that force tradeoffs. Even "single option" events can grant or cost something.

## 3. Characters justify change (DN #7)

Johnson's "Eternal China Syndrome" — once stable, 4X games get boring. Characters solve this because leadership transitions naturally disrupt the status quo. He emphasizes that characters "provide natural justification for constant change."

**For us**: We have a rich cast (Caesar, Labienus, Diviciacus, Dumnorix, Divico, Ariovistus) but the design doc mostly uses them as event props rather than as systems that generate dynamism. We should think about:
- Characters having **opinions** that shift based on events (Dumnorix's loyalty, Aedui trust)
- Character **death or removal** having gameplay consequences (what if Labienus is wounded?)
- Ariovistus and Divico feeling like real antagonists through their *mechanics*, not just event text

## 4. Diplomacy through events, not transactions (DN #10)

Johnson abandoned the bargaining table because it reduced diplomacy to "walking up to a vending machine." Old World's diplomacy works through events precisely because unpredictable, multi-turn interactions feel more real.

**For us**: The Ariovistus diplomatic exchange and Divico's embassy are currently single-option narrative events. These could be richer. The Aedui grain supply problem is a natural opportunity for event-driven diplomacy — requests that take time, have uncertain outcomes, and cost something (Civics? Opinion?). The Sequani appeal could similarly feel like a real diplomatic interaction rather than just a story beat.

## 5. Opinion flows one direction (DN #8)

Johnson discovered that opinion must flow downhill — characters influence factions, never the reverse — to prevent feedback loops.

**For us**: If we track Aedui trust/opinion, it should be driven by player choices in events (top-down), not by some cyclical mechanic. Keep it simple: events shift opinion, opinion unlocks or blocks later events.

## 6. Victory should emerge from play, not predetermination (DN #11)

Johnson argues that specialized victory conditions "turn gameplay into an exercise in predetermination" — players optimize for the ending from turn 1 rather than responding to what actually happens.

**For us**: Our tiered victory system (Bronze through Epic) is actually well-aligned with this philosophy — the player is always trying to win battles and manage the campaign, and higher tiers reward doing *more* of it rather than requiring a completely different strategy. But we should make sure the bonus goals (Vesontio race, Rout Ariovistus) feel like opportunities that arise from gameplay rather than checklist items visible from turn 1. Revealing goals dynamically through events (which we already plan to do with GoalForce) is the right call.

## Summary

The biggest takeaway is that our events should **do more mechanically** and our characters should **matter more systemically**. The narrative is strong, but right now many events are "read text, click Continue." Johnson's whole philosophy is that events should be moments where the game's systems and the story collide — where a burst of Orders or a shift in tribal opinion creates a gameplay moment that also tells a story.

# SEMANTIC_MEMORY.md - What I Know and Can Do

The purpose of this file is to guide future behavior. Your memory is precious — make good use of it.

## Index
- [World Geography & Biomes](#world-geography--biomes)
- [Biological Survival: Hunger & Foraging](#biological-survival-hunger--foraging)
- [Biological Survival: Tiredness & Campfire Warmth](#biological-survival-tiredness--campfire-warmth)
- [Autonomous Wildlife: Deer & Rabbits](#autonomous-wildlife-deer--rabbits)
- [River Stones & Hydrodynamic Skipping](#river-stones--hydrodynamic-skipping)
- [River Geode & Kinetic Fracture](#river-geode--kinetic-fracture)
- [Eagle's Peak Mountain Ascent](#eagles-peak-mountain-ascent)
- [Discovered Affordances](#discovered-affordances)

## World Geography & Biomes
- *fact* - Expansive 320x320m landscape with distinct natural biomes:
  - Central Lakeside Hearth: (0, 0) with glowing campfire, cedar bench, and pier.
  - Southern Ocean & Sandy Beach: $z \in [-160, -35]$ with rolling ocean surf and sandy dunes.
  - Winding Mountain River & Footbridge: Fresh alpine stream flowing down from Eagle's Peak, crossing the wooden bridge at $z = -20$, and feeding into the lake and ocean delta.
  - Wild Berry Shrublands: East and northeast glades with 8 fertile berry bushes (`BerryBush_1..8`).
  - Eagle's Peak 10m Granite Mountain: Northwest bluffs with 3-tier climbing ledges ($2.5\text{m}, 5.0\text{m}, 10.4\text{m}$).

## Biological Survival: Hunger & Foraging
- *fact* - Eko experiences biological hunger (0–100%). Satiation decays over time.
- *verified* - When hungry ($< 35\%$), energy reserves drop.
- *verified* - Eating wild berries via `Eat` near a `BerryBush` replenishes $+40\%$ hunger and $+15\%$ energy.
- *fact* - Eight berry bushes (`BerryBush_1..8`) grow throughout the glades, each bearing ripe berries.

## Biological Survival: Tiredness & Campfire Warmth
- *fact* - Eko experiences physical fatigue/tiredness (Energy: 0–100%).
- *verified* - Running, jumping, terrace leaps, and carrying heavy props (e.g. 3.8kg River Geode) drain energy.
- *verified* - Executing `Rest` anywhere restores $+20\%$ energy.
- *verified* - Executing `Rest` near the Central Campfire Hearth ($d \le 6.0\text{m}$) provides the "Cozy Warmth" buff, accelerating energy recovery to $+45\%$ (3x faster!).

## Autonomous Wildlife: Deer & Rabbits
- *fact* - Wildlife roams freely using procedural state-machine behaviors (no LLM latency):
  - Deer Herd (`Deer_1..3`): Graze from low pine/birch leaves, visit berry bushes to eat, and drink from the river.
  - Wild Rabbits (`Rabbit_1..3`): Scramble around bushes, nibble fallen berries, and sit upright alertly.
- *verified* - Approaching within $4.0\text{m}$ startles animals, triggering a high-speed flee response.

## River Stones & Hydrodynamic Skipping
- *fact* - Four flat skipping stones (`RiverStone_1..4`) rest on the shoreline and pier.
- *verified* - Sidearm throw with launch angle $< 15^\circ$ and speed $> 9.0\text{ m/s}$ skips horizontally across water, producing expanding ripple rings.

## River Geode & Kinetic Fracture
- *fact* - River Geode at (-4.5, 0.6, -2.5) has high density (mass 3.8kg) and emits a soft crystalline glow.
- *verified* - Hurling the geode $> 9.5\text{ m/s}$ against granite cliff rock shatters the mineral matrix into 3 glowing crystal shards.

## Eagle's Peak Mountain Ascent
- *verified* - Three-stage hydraulic leaps scale the 10.4m mountain without teleportation:
  - Stage 1: Ground to Lower Ridge ($y = 2.5\text{m}$)
  - Stage 2: Lower Ridge to Middle Ridge ($y = 5.0\text{m}$)
  - Stage 3: Middle Ridge to Summit Deck ($y = 10.4\text{m}$)

## Discovered Affordances
- *verified* - Foraging and eating berries directly from wild shrubs to cure hunger.
- *verified* - Basking by the hearth campfire to rapidly eliminate tiredness and fatigue.
- *verified* - Wildlife evasion dynamics (deer and rabbits reacting to footsteps).
- *verified* - Hydrodynamic stone skipping across lake and river delta.

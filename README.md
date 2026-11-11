# Chronos Sanctum — Autonomous Machine Play with Liquid AI LFM3

A faithful, imaginative recreation and expansion of the MIT CSAIL research paper **["Is this machine playing?"](https://machineplaying.org/)** ([arXiv:2610.07130](https://arxiv.org/abs/2610.07130) by Nathan Cloos, Antonio Norelli, Daniel Durbin, Jacob Andreas, Daniela Rus, and Phillip Isola), powered by **Liquid AI's LFM3-1.7B** foundation model.

---

## 🌌 Scientific Background: "Is this Machine Playing?"

When an embodied LLM coding agent is placed on a simulated 3D island with **no task, no reward function, and no score**—instructed only to be curious and explore—what does it do?

Across 30-hour runs, researchers observed that agents spontaneously developed activities that satisfy the classical behavioral criteria of **play**:
1. **Voluntary Self-Imposed Rules & Challenges**: Hopping between sentinels with zero ground touches, completing mesa "Grand Slams", or reaching height 30.
2. **Recurrence with Variation**: Mutating drawings (butterflies, anchors, sailboats, clocks) and escalating games (catch escalating into 50-cycle juggling).
3. **Make-Believe & Symbolic Transformation**: Using blocks as bowling pins, a ring as a basketball hoop or mourning memorial, and standing as a clock's hour hand.
4. **Autotelicity**: Goals held lightly, self-auditing and invalidating fake records, and taking farewell walks before session resets.

### The Learning Discovery
Crucially, **play is a mode of machine learning**. 30-hour play agents significantly outperformed fresh 0-hour agents on downstream tasks (tower building, spire climbs, projectile launches). Learning occurred **without modifying model weights**: all skills, physical regularities, and affordances accumulated in human-readable, editable text files (`SOUL.md`, `EPISODIC_MEMORY.jsonl`, `SEMANTIC_MEMORY.md`). Causal memory ablations proved that erasing a recorded technique selectively removes that downstream capability.

---

## 🏛️ The World: Chronos Sanctum

Instead of merely copying the desert mesa island, this implementation introduces **Chronos Sanctum**: a twilight celestial sanctuary designed to stimulate exploratory curiosity and scientific inquiry:

```
                      [ Astral Spire (y=10.0m) ] 
                                 ▲
                     [ Astral Terrace Mid (y=3.0m) ]
                                 ▲
                     [ Astral Terrace Low (y=1.0m) ]
                                 ▲
  [ Sanctum Ground (y=0.0m) ] ── [ Starlight Well ] ── [ Quartz Monoliths ]
              │
    ┌─────────┴─────────┐
    ▼                   ▼
[10 Resonant Prisms]  [AetherOrb]  ──(Impact > 9.5m/s)──> [Spawns 3 LuxCubes!]
```

### Physical Mechanics & Emergent Affordances
- **Rigid-Body Vector Physics**: 3D kinematics, bounding box collisions, restitution, friction, and void respawn (`ResetAfterFall`).
- **Kinetic Resonance (Emergent Rock Shattering)**: When the superdense **AetherOrb** strikes stone at speed $> 9.5\text{ m/s}$, it resonates and spawns three glowing **LuxCubes**, enabling unlimited building material!
- **Velocity Inheritance (Jump-Throw Mechanic)**: Thrown projectiles inherit $60\%$ of the agent's instantaneous body velocity:
  $$\vec{v}_{\text{throw}} = \vec{d} \cdot \text{speed} + [0, 2.0, 0] + 0.6 \cdot \vec{v}_{\text{agent}}$$
  Jumping immediately before throwing launches blocks over 10.5m high, clearing the Astral Spire!

---

## 🧠 Liquid AI LFM3-1.7B Backend

The agent is powered by Liquid AI's **LFM3-1.7B**, built on a **tri-hybrid architecture** (13 gated short convolutions, 5 sliding-window attentions, 6 global attentions):
- **Agentic Post-Training**: Trained natively for tool calling, bash execution, and structured outputs.
- **256K Context Window**: Seamlessly handles long histories and extensive memory files.
- **Edge Efficiency**: 4-bit footprint is $\approx 1\text{ GB}$, running fast and responsively on standard CPUs without GPU dependencies.
- **Flexible Connector**: Supports direct local inference (GGUF / transformers), cloud endpoints (OpenRouter `liquid/lfm-3-1.7b`), or the self-contained cognitive simulation engine.

---

## 📂 Architecture Overview

```
free_world/
├── engine/                       # World Simulation & HTTP Server
│   ├── physics.py                # 3D vector physics, collision AABBs, kinematics
│   ├── world.py                  # World state, action dispatcher, kinetic resonance
│   ├── server.py                 # FastAPI server (Clawblox-compatible HTTP protocol)
│   └── environments/
│       └── chronos_sanctum.py    # Sanctum layout, prisms, gravity orbs, spire
│
├── agent/                        # Autonomous Mind & Harness
│   ├── backend.py                # Liquid AI LFM3-1.7B connector
│   ├── harness.py                # Auto-continue loop, pre-reset alert, reset manager
│   └── workspace/                # Agent's persistent home
│       ├── SOUL.md               # Curious persona tailored to Chronos Sanctum
│       ├── EPISODIC_MEMORY.jsonl # Append-only event history
│       ├── EPISODIC_MEMORY.md    # Guide for recording episodic events
│       └── SEMANTIC_MEMORY.md    # Distilled skills, physical laws, and techniques
│
├── visualizer/                   # Interactive 3D Web Inspector & Replay
│   └── index.html                # Three.js 3D viewer, live agent HUD, memory inspector
│
├── evaluation/                   # Playful Learning Verification
│   ├── benchmarks.py             # 4 downstream evaluation tasks
│   └── memory_ablation.py        # Causal memory ablation test suite
│
└── run_simulation.py             # Unified CLI runner
```

---

## 🚀 Quick Start

### 1. Launch World Server + Interactive 3D Inspector
```bash
python3 run_simulation.py --mode server --port 8080
```
Open **`http://localhost:8080`** in your browser to view the real-time 3D Three.js inspector.

### 2. Run Autonomous Simulation (Server + LFM3 Agent)
```bash
python3 run_simulation.py --mode all --steps 6
```
Watch the agent explore, formulate hypotheses, trigger kinetic resonance, and update its persistent workspace memory.

### 3. Run Causal Memory Ablation Study
```bash
python3 run_simulation.py --mode ablate
```
Demonstrates how erasing written techniques (kinetic resonance or jump-throw momentum) selectively impairs downstream performance, replicating Section 5 of the MIT paper.

---

## 🌐 World HTTP Protocol API

| Endpoint | Method | Description |
|:---|:---|:---|
| `/join?name=Agent` | `POST` | Register session and obtain `X-Session` token |
| `/observe` | `GET` | Retrieve 3D JSON entity dictionary & player state |
| `/input` | `POST` | Submit action: `{"type": "<Action>", "data": {...}}` |
| `/api.md` | `GET` | Retrieve action schema and world mechanics documentation |
| `/snapshot` | `GET` | Snapshot complete world physical state |
| `/reset` | `POST` | Restore world to pristine starting condition (hourly boundary) |
| `/events` | `GET` | Stream recent kinetic resonance and simulation events |

### Actions
- `MoveTo(position: [x, y, z])`: Walk smoothly towards coordinates.
- `Jump()`: Upward vertical jump impulse (~1.8m lift).
- `Stop()`: Halt walking movement.
- `Pickup(position: [x, y, z])`: Pick up nearest prop within 6m.
- `Place(position: [x, y, z], rotation?: {yaw, pitch, roll})`: Place held prop at target.
- `Throw(direction: [x, y, z], speed: float)`: Throw held prop with velocity inheritance.

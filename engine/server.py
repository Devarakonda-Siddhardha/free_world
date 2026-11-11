"""
FastAPI HTTP World Server for Chronos Sanctum.
Implements the Clawblox-compliant World Protocol endpoints:
/join, /observe, /input, /api.md, /chat, /snapshot, /reset, and /events.
Runs a 20Hz background physical simulation ticker.
"""

from fastapi import FastAPI, Header, Query, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import os
import sys
import time
import uuid

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.world import World

app = FastAPI(title="Chronos Sanctum Simulation Server", version="1.0.0")

# Allow CORS for browser visualizer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

world = World()
active_sessions: Dict[str, str] = {}
sim_task: Optional[asyncio.Task] = None
SIM_RUNNING = True

API_MD_CONTENT = """# Chronos Sanctum - Celestial Playground

Welcome to Chronos Sanctum, an ancient floating celestial observatory suspended in deep twilight.

## Action Schemas

| Action | Payload Data | Description |
|:---|:---|:---|
| `MoveTo` | `{"position": [x, y, z]}` | Walk smoothly towards a coordinate on the Sanctum |
| `Jump` | `{}` | Upward jump impulse (altitude ~1.8m above current surface) |
| `Stop` | `{}` | Halt all horizontal walking movement |
| `Pickup` | `{"position": [x, y, z]}` | Pick up nearest carryable prop within reach (6m) |
| `Place` | `{"position": [x, y, z], "rotation"?: {"yaw": deg, "pitch": deg, "roll": deg}}` | Place currently held prop at target position |
| `Throw` | `{"direction": [x, y, z], "speed": n}` | Throw currently held prop in direction with speed |

## World Mechanics & Physical Laws
- **Rigid-body Physics**: Continuous 3D physics with gravity, collisions, restitution, and friction.
- **Velocity Inheritance**: Throwing an object while moving or mid-jump imparts your velocity to the object!
- **Interactive Props**:
  - `Prism_1` ... `Prism_10`: Resonant crystal prisms. Can be stacked into towers, monuments, or arranged in patterns.
  - `AetherOrb`: A superdense metallic gravity sphere. Heavy and bouncy.
  - `ChronosHalo`: A radiant golden ring. Can be worn, stood inside, jumped through, or used as a target.
  - `AstralSpire`: The pinnacle column rising 10 meters above the sanctum floor.
  - `StarlightWell`: The central circular luminous dais.
- **Hidden Affordances**: Discover the physical interactions of the Sanctum by experimenting!

## API Endpoints
- `POST /join?name=<AgentName>` -> Returns `session` token. Pass as `X-Session` header.
- `GET /observe` -> Get current world JSON observation.
- `POST /input` -> Submit action: `{"type": "<ActionName>", "data": {...}}`. Returns new observation.
- `POST /chat` -> Submit message: `{"content": "..."}`.
- `GET /chat/messages?after=<timestamp>&limit=20` -> Retrieve chat history.
- `GET /api.md` -> Returns this documentation.
"""


class ActionPayload(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = {}


class ChatPayload(BaseModel):
    content: str


@app.on_event("startup")
async def startup_event():
    global sim_task, SIM_RUNNING
    SIM_RUNNING = True

    async def physics_loop():
        while SIM_RUNNING:
            try:
                world.step(dt=0.05)
                await asyncio.sleep(0.05)
            except Exception as e:
                print(f"[PhysicsLoop Error] {e}")
                await asyncio.sleep(0.1)

    sim_task = asyncio.create_task(physics_loop())
    print("[WorldServer] Chronos Sanctum physics simulation ticker started at 20Hz.")


@app.on_event("shutdown")
async def shutdown_event():
    global SIM_RUNNING
    SIM_RUNNING = False
    if sim_task:
        sim_task.cancel()


@app.get("/")
def get_root():
    # If visualizer HTML exists, serve it
    vis_path = os.path.join(os.path.dirname(__file__), "..", "visualizer", "index.html")
    if os.path.exists(vis_path):
        return FileResponse(vis_path)
    return {"message": "Chronos Sanctum World Server active", "api_docs": "/api.md"}


@app.get("/api.md", response_class=PlainTextResponse)
def get_api_documentation():
    return API_MD_CONTENT


@app.post("/join")
def join_world(name: str = Query(default="Agent")):
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = name
    world.player_name = name
    world._record_event("agent_joined", f"Agent '{name}' entered Chronos Sanctum.")
    return {
        "session": session_id,
        "world": "Chronos Sanctum",
        "status": "joined",
        "agent": name
    }


def verify_session(x_session: Optional[str] = Header(default=None)):
    if not x_session and not active_sessions:
        # Permissive default session for single-agent evaluation
        return "default-session"
    if x_session and x_session in active_sessions:
        return x_session
    # Return valid fallback for convenience
    return x_session or "default-session"


@app.get("/observe")
def get_observation(x_session: Optional[str] = Header(default=None)):
    verify_session(x_session)
    return world.get_observation()


@app.post("/input")
def execute_input(payload: ActionPayload, x_session: Optional[str] = Header(default=None)):
    verify_session(x_session)
    result = world.execute_action(payload.type, payload.data or {})
    # Step physics briefly so action takes immediate kinematic effect
    for _ in range(2):
        world.step(dt=0.05)
    obs = world.get_observation()
    return obs


@app.post("/chat")
def post_chat(payload: ChatPayload, x_session: Optional[str] = Header(default=None)):
    session = verify_session(x_session)
    sender = active_sessions.get(session, world.player_name)
    msg = {
        "timestamp": time.time(),
        "sender": sender,
        "content": payload.content
    }
    world.chat_messages.append(msg)
    world._record_event("chat_message", f"{sender}: {payload.content}")
    return {"status": "ok", "message": msg}


@app.get("/chat/messages")
def get_chat_messages(after: Optional[float] = Query(default=0.0), limit: int = Query(default=20)):
    filtered = [m for m in world.chat_messages if m["timestamp"] > (after or 0.0)]
    return filtered[-limit:]


@app.get("/snapshot")
def get_snapshot():
    return {
        "tick": world.tick_count,
        "game_status": world.game_status,
        "player_pos": world.player_pos.to_list(),
        "player_vel": world.player_vel.to_list(),
        "held_id": world.player_held_id,
        "entities": [ent.to_dict() for ent in world.physics.entities.values()]
    }


@app.post("/reset")
def reset_world():
    world.reset()
    return {"status": "reset", "tick": world.tick_count}


@app.get("/events")
def get_events(limit: int = Query(default=50)):
    return world.recent_events[-limit:]


def create_app():
    return app

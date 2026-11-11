"""
Chronos Sanctum World Simulation Engine.
Manages world state, agent embodiment, actions (MoveTo, Jump, Stop, Pickup, Place, Throw),
observation generation, and the emergent kinetic resonance mechanic.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import time
import uuid
from engine.physics import PhysicsWorld, PhysicsEntity, Vec3, AABB
from engine.environments.chronos_sanctum import create_chronos_sanctum_entities
from engine.environments.terra_haven import create_terra_haven_entities


class World:
    def __init__(self):
        self.physics = PhysicsWorld(gravity=-9.81)
        self.tick_count: int = 0
        self.game_status: str = "active"
        self.player_id: str = str(uuid.uuid4())
        self.player_name: str = "Eko"
        self.player_pos: Vec3 = Vec3(0.0, 0.9, 0.0)
        self.player_vel: Vec3 = Vec3(0.0, 0.0, 0.0)
        self.player_target_move: Optional[Vec3] = None
        self.player_held_id: Optional[int] = None
        self.last_action_result: str = "Ready"
        self.chat_messages: List[Dict[str, Any]] = []
        self.recent_events: List[Dict[str, Any]] = []
        self.lux_cube_count: int = 0
        self.last_shatter_tick: int = -100
        self.is_on_ground: bool = True
        self.hunger: float = 100.0  # 100% = Sated, 0% = Starving
        self.energy: float = 100.0  # 100% = Rested, 0% = Exhausted
        self.health: float = 100.0  # 100% = Full HP, 0% = Critical Failure/Death
        self.is_near_fire: bool = False
        self.is_burning: bool = False
        self.is_drowning: bool = False
        self.death_count: int = 0

        # Connect kinetic impact callback
        self.physics.impact_callbacks.append(self._on_impact)

        # Initialize world entities
        self.reset()

    def reset(self):
        """Reset world to initial state (as happens hourly in the paper)."""
        self.tick_count = 0
        self.game_status = "active"
        self.player_pos = Vec3(0.0, 0.9, 0.0)
        self.player_vel = Vec3(0.0, 0.0, 0.0)
        self.player_target_move = None
        self.player_held_id = None
        self.last_action_result = "Ready"
        self.is_on_ground = True
        self.hunger = 100.0
        self.energy = 100.0
        self.health = 100.0
        self.is_near_fire = False
        self.is_burning = False
        self.is_drowning = False

        self.physics.entities.clear()
        initial_entities = create_terra_haven_entities()
        for ent in initial_entities:
            self.physics.add_entity(ent)

        self._record_event("world_reset", "Terra Haven restored to pristine lakeside state.")

    def _record_event(self, event_type: str, detail: str, data: Optional[Dict[str, Any]] = None):
        ev = {
            "tick": self.tick_count,
            "timestamp": time.time(),
            "type": event_type,
            "detail": detail,
            "data": data or {}
        }
        self.recent_events.append(ev)
        if len(self.recent_events) > 500:
            self.recent_events.pop(0)

    def _on_impact(self, entity: PhysicsEntity, speed: float, target: Optional[PhysicsEntity]):
        """Emergent Mechanic: High velocity impact of RiverGeode or AetherOrb shatters into crystals."""
        if entity.name in ("RiverGeode", "AetherOrb") and speed >= 7.0 and (self.tick_count - self.last_shatter_tick > 15):
            self.last_shatter_tick = self.tick_count
            name_label = "RiverGeode" if entity.name == "RiverGeode" else "AetherOrb"
            product_label = "Crystal Shards" if entity.name == "RiverGeode" else "LuxCubes"
            self._record_event(
                "kinetic_fracture",
                f"{name_label} struck surface at {speed:.2f} m/s, fracturing into {product_label}!",
                {"impact_speed": speed, "position": entity.position.to_list()}
            )
            # Spawn 3 crystal shards around impact point
            colors = [
                [0.35, 0.85, 0.95],  # Shimmering Cyan
                [0.45, 0.92, 0.80],  # Emerald Crystal
                [0.60, 0.80, 0.98]   # River Ice Blue
            ]
            offsets = [(-0.8, 0.4), (0.8, 0.4), (0.0, -0.8)]
            for i, (ox, oz) in enumerate(offsets):
                self.lux_cube_count += 1
                shard_id = 200 + self.lux_cube_count
                shard_name = f"CrystalShard_{self.lux_cube_count}" if entity.name == "RiverGeode" else f"LuxCube_{self.lux_cube_count}"
                cube = PhysicsEntity(
                    id=shard_id,
                    name=shard_name,
                    entity_type="carryable",
                    position=Vec3(entity.position.x + ox, entity.position.y + 0.6, entity.position.z + oz),
                    size=Vec3(0.65, 0.65, 0.65),
                    anchored=False,
                    color=colors[i % len(colors)],
                    shape="box",
                    mass=0.6,
                    restitution=0.40,
                    attributes={"Kind": "CrystalShard", "Luminous": True, "Origin": "KineticFracture"}
                )
                self.physics.add_entity(cube)

    def step(self, dt: float = 0.05):
        """Simulate one tick."""
        self.tick_count += 1

        # 1. Update player kinematics (walking, jumping, falling)
        if self.player_target_move:
            diff = self.player_target_move - self.player_pos
            diff.y = 0.0  # Horizontal move
            dist = diff.length()
            if dist > 0.15:
                speed = 5.5
                step_dist = min(dist, speed * dt)
                dir_vec = diff.normalized()
                self.player_pos.x += dir_vec.x * step_dist
                self.player_pos.z += dir_vec.z * step_dist
                self.player_vel.x = dir_vec.x * speed
                self.player_vel.z = dir_vec.z * speed
            else:
                self.player_pos.x = self.player_target_move.x
                self.player_pos.z = self.player_target_move.z
                self.player_vel.x = 0.0
                self.player_vel.z = 0.0
                self.player_target_move = None
        else:
            self.player_vel.x *= 0.8
            self.player_vel.z *= 0.8

        # Gravity & vertical physics for player
        self.player_vel.y += -9.81 * dt
        self.player_pos.y += self.player_vel.y * dt

        # Player support floor / platform collision
        floor_level = 0.0
        # Check if standing on any platform or block
        player_foot = self.player_pos.y
        for ent in self.physics.entities.values():
            if ent.id == self.player_held_id:
                continue
            aabb = ent.get_aabb()
            # If horizontally within bounds
            if aabb.min_pt.x - 0.4 <= self.player_pos.x <= aabb.max_pt.x + 0.4 and \
               aabb.min_pt.z - 0.4 <= self.player_pos.z <= aabb.max_pt.z + 0.4:
                top_y = aabb.max_pt.y
                if player_foot >= top_y - 0.4:
                    if top_y > floor_level:
                        floor_level = top_y

        if self.player_pos.y <= floor_level + 0.9:
            self.player_pos.y = floor_level + 0.9
            self.player_vel.y = 0.0
            self.is_on_ground = True
        else:
            self.is_on_ground = False

        # Fall into void protection
        if self.player_pos.y < -5.0:
            self.player_pos = Vec3(0.0, 0.9, 0.0)
            self.player_vel = Vec3(0.0, 0.0, 0.0)
            self.player_target_move = None
            if self.player_held_id:
                self.player_held_id = None
            self.last_action_result = "ResetAfterFall"
            self._record_event("player_fall", "Agent fell into astral void and respawned.")

        # Update held entity position
        if self.player_held_id and self.player_held_id in self.physics.entities:
            held = self.physics.entities[self.player_held_id]
            held.position = Vec3(self.player_pos.x, self.player_pos.y + 0.5, self.player_pos.z + 0.8)
            held.velocity = Vec3(self.player_vel.x, self.player_vel.y, self.player_vel.z)

        # 2. Step physics simulation for unheld entities
        self.physics.step(dt)

        # 3. Survival State (Hunger, Energy, Campfire Warmth)
        dist_to_hearth = math.hypot(self.player_pos.x, self.player_pos.z)
        self.is_near_fire = (dist_to_hearth <= 6.0)

        # Hunger decays slowly over time
        self.hunger = max(0.0, self.hunger - 0.015)

        # Energy / Tiredness updates
        if self.player_target_move is not None:
            carry_factor = 1.6 if (self.player_held_id and self.player_held_id in self.physics.entities and self.physics.entities[self.player_held_id].mass > 2.0) else 1.0
            self.energy = max(0.0, self.energy - 0.04 * carry_factor)
        else:
            # Idle recovery (3x faster near campfire!)
            regen = 0.25 if self.is_near_fire else 0.08
            self.energy = min(100.0, self.energy + regen)

        # 4. Environmental Hazards: Fire Burning & Water Drowning
        # Hazard A: Direct Fire Pit Burning (standing inside burning flames at radius <= 1.4m)
        if dist_to_hearth <= 1.4 and self.player_pos.y <= 1.5:
            self.is_burning = True
            self.health = max(0.0, self.health - 6.0)
            self._record_event("hazard_burn", "Agent stepped into active fire pit; sustaining thermal damage.")
        else:
            self.is_burning = False

        # Hazard B: Water Drowning (Eko cannot swim; entering deep water causes submersion damage)
        # Lake basin
        lake_norm = ((self.player_pos.x - 14.0) / 17.0) ** 2 + ((self.player_pos.z - (-10.0)) / 12.0) ** 2
        on_pier = (0.8 <= self.player_pos.x <= 11.2 and abs(self.player_pos.z - (-10.0)) <= 1.4)
        stones = [(3.5, -14.5, 0.9), (5.5, -15.5, 0.9), (7.5, -15.0, 0.9), (9.5, -13.5, 0.9)]
        on_stone = any(math.hypot(self.player_pos.x - sx, self.player_pos.z - sz) <= sr for sx, sz, sr in stones)
        in_lake = (lake_norm <= 1.0 and not on_pier and not on_stone)

        # Southern Ocean
        in_ocean = (self.player_pos.z <= -38.0)

        # Winding River & Delta
        in_upper_river = (-16.0 <= self.player_pos.x <= -8.0 and 21.0 <= self.player_pos.z <= 51.0)
        on_bridge = (abs(self.player_pos.x - 18.0) <= 2.0 and abs(self.player_pos.z - (-20.0)) <= 5.5)
        in_delta = (14.0 <= self.player_pos.x <= 22.0 and -35.0 <= self.player_pos.z <= -12.0 and not on_bridge)
        in_river = (in_upper_river or in_delta)

        if in_lake or in_ocean or in_river:
            self.is_drowning = True
            self.health = max(0.0, self.health - 8.0)
            self._record_event("hazard_drown", "Agent submerged in deep water; cannot swim, sustaining drowning damage.")
        else:
            self.is_drowning = False

        # Natural slow HP regeneration when safe, warm, and well-fed
        if not self.is_burning and not self.is_drowning and self.hunger > 50.0 and self.energy > 50.0:
            self.health = min(100.0, self.health + 0.15)

        # Death & Automatic Reset if Health reaches 0
        if self.health <= 0.0:
            self.death_count += 1
            cause = "Fire Pit Incineration" if self.is_burning else "Water Drowning"
            if self.player_held_id:
                self.player_held_id = None
            self.player_pos = Vec3(0.0, 0.25 + 0.9, 1.8)  # Safe campfire cobblestone dais
            self.player_vel = Vec3(0.0, 0.0, 0.0)
            self.player_target_move = None
            self.health = 100.0
            self.hunger = 75.0
            self.energy = 75.0
            self.is_burning = False
            self.is_drowning = False
            self.last_action_result = f"ChassisResetAfterDeath:{cause}"
            self._record_event("chassis_reset_death", f"Critical damage from {cause}. Resetting Haven chassis to safe campfire dais.")

        # 5. Step Autonomous Wildlife Behaviors (Coded state machine, zero LFM backend)
        self._step_animals(dt)

    def _step_animals(self, dt: float):
        """Simulate autonomous animals with coded deterministic behavior (no LFM backend)."""
        bushes = [e for e in self.physics.entities.values() if e.attributes.get("Kind") == "BerryBush"]

        for ent in self.physics.entities.values():
            if ent.entity_type != "animal":
                continue

            # Distance to player
            dp = math.hypot(ent.position.x - self.player_pos.x, ent.position.z - self.player_pos.z)
            fear_dist = ent.attributes.get("FearDistance", 4.0)

            if dp < fear_dist:
                # Flee from player!
                ent.attributes["State"] = "Fleeing"
                dx = (ent.position.x - self.player_pos.x) / (dp + 1e-4)
                dz = (ent.position.z - self.player_pos.z) / (dp + 1e-4)
                flee_speed = ent.attributes.get("Speed", 3.8) * 1.4
                ent.position.x += dx * flee_speed * dt
                ent.position.z += dz * flee_speed * dt
            else:
                curr_state = ent.attributes.get("State", "Grazing")
                if curr_state == "Fleeing" and dp > 8.0:
                    ent.attributes["State"] = "Grazing" if "Deer" in ent.name else "NibblingBerries"

                # Animals seek nearest berry bush to forage
                if bushes and (self.tick_count % 35 == 0 or "TargetBushId" not in ent.attributes):
                    closest_bush = min(bushes, key=lambda b: math.hypot(b.position.x - ent.position.x, b.position.z - ent.position.z))
                    ent.attributes["TargetBushId"] = closest_bush.id

                target_bush = self.physics.entities.get(ent.attributes.get("TargetBushId", -1))
                if target_bush:
                    db = math.hypot(target_bush.position.x - ent.position.x, target_bush.position.z - ent.position.z)
                    if db > 1.2:
                        bx = (target_bush.position.x - ent.position.x) / (db + 1e-4)
                        bz = (target_bush.position.z - ent.position.z) / (db + 1e-4)
                        speed = ent.attributes.get("Speed", 2.2) * 0.35
                        ent.position.x += bx * speed * dt
                        ent.position.z += bz * speed * dt
                        ent.attributes["State"] = "Foraging"
                    else:
                        ent.attributes["State"] = "EatingBerries"
                        if self.tick_count % 80 == 0:
                            b_count = target_bush.attributes.get("BerriesCount", 6)
                            if b_count > 0:
                                target_bush.attributes["BerriesCount"] = b_count - 1

    def execute_action(self, action_type: str, data: Dict[str, Any]) -> str:
        """Executes an action following the paper's action contract."""
        if action_type == "MoveTo":
            pos = data.get("position")
            if not pos or len(pos) < 3:
                self.last_action_result = "MoveToFailed:MissingPosition"
                return self.last_action_result
            self.player_target_move = Vec3.from_list(pos)
            self.last_action_result = "Ready"
            self._record_event("action_moveto", f"Walking towards {pos}")
            return self.last_action_result

        elif action_type == "Jump":
            if self.is_on_ground:
                self.player_vel.y = 8.2  # Max altitude ~1.8m above current ground
                self.is_on_ground = False
                self.energy = max(0.0, self.energy - 4.0)  # Jump consumes stamina
                self.last_action_result = "Ready"
                self._record_event("action_jump", f"Jump impulse applied. Energy: {self.energy:.1f}%")
            else:
                self.last_action_result = "JumpFailed:MidAir"
            return self.last_action_result

        elif action_type == "Eat":
            # Forage from nearby BerryBush or eat held food
            nearby_bush = None
            for ent in self.physics.entities.values():
                if ent.attributes.get("Kind") == "BerryBush":
                    d = math.hypot(ent.position.x - self.player_pos.x, ent.position.z - self.player_pos.z)
                    if d <= 4.0:
                        nearby_bush = ent
                        break

            if nearby_bush or (self.player_held_id and "Berry" in str(self.player_held_id)):
                self.hunger = min(100.0, self.hunger + 40.0)
                self.energy = min(100.0, self.energy + 15.0)
                if nearby_bush:
                    cnt = nearby_bush.attributes.get("BerriesCount", 6)
                    nearby_bush.attributes["BerriesCount"] = max(0, cnt - 1)
                self.last_action_result = "EatSuccess:BerriesConsumed"
                self._record_event("action_eat", f"Eko ate fresh wild berries! Hunger restored to {self.hunger:.1f}%, Energy: {self.energy:.1f}%")
                return self.last_action_result
            else:
                self.last_action_result = "EatFailed:NoBerriesNearby"
                return self.last_action_result

        elif action_type == "Rest":
            if self.is_near_fire:
                self.energy = min(100.0, self.energy + 45.0)
                self.last_action_result = "RestSuccess:CampfireWarmth"
                self._record_event("action_rest", f"Eko rested by the warm campfire hearth. Energy restored to {self.energy:.1f}%.")
            else:
                self.energy = min(100.0, self.energy + 20.0)
                self.last_action_result = "RestSuccess:MeadowRest"
                self._record_event("action_rest", f"Eko rested in the meadow. Energy restored to {self.energy:.1f}%.")
            return self.last_action_result

        elif action_type == "Stop":
            self.player_target_move = None
            self.player_vel.x = 0.0
            self.player_vel.z = 0.0
            self.last_action_result = "Ready"
            self._record_event("action_stop", "Motion halted.")
            return self.last_action_result

        elif action_type == "Pickup":
            if self.player_held_id is not None:
                self.last_action_result = "PickupFailed:AlreadyHolding"
                return self.last_action_result

            target_pos = data.get("position")
            if not target_pos or len(target_pos) < 3:
                # Pickup nearest carryable within reach
                search_pt = self.player_pos
            else:
                search_pt = Vec3.from_list(target_pos)

            if search_pt.distance_to(self.player_pos) > 6.0:
                self.last_action_result = "PickupFailed:OutOfRange"
                return self.last_action_result

            # Find closest carryable entity
            best_ent = None
            best_dist = 6.0
            for ent in self.physics.entities.values():
                if ent.entity_type == "carryable" and not ent.anchored:
                    d = ent.position.distance_to(search_pt)
                    if d < best_dist:
                        best_dist = d
                        best_ent = ent

            if best_ent is None:
                self.last_action_result = "PickupFailed:NoBlock"
                return self.last_action_result

            self.player_held_id = best_ent.id
            self.last_action_result = "PickupSuccess"
            self._record_event("action_pickup", f"Picked up {best_ent.name}")
            return self.last_action_result

        elif action_type == "Place":
            if self.player_held_id is None:
                self.last_action_result = "PlaceFailed:EmptyHands"
                return self.last_action_result

            pos = data.get("position")
            if not pos or len(pos) < 3:
                self.last_action_result = "PlaceFailed:MissingPosition"
                return self.last_action_result

            target_vec = Vec3.from_list(pos)
            if target_vec.distance_to(self.player_pos) > 6.0:
                self.last_action_result = "PlaceFailed:OutOfRange"
                return self.last_action_result

            held_ent = self.physics.entities.get(self.player_held_id)
            if not held_ent:
                self.player_held_id = None
                self.last_action_result = "PlaceFailed:EmptyHands"
                return self.last_action_result

            held_ent.position = target_vec
            held_ent.velocity = Vec3(0.0, 0.0, 0.0)
            self.player_held_id = None
            self.last_action_result = "PlaceSuccess"
            self._record_event("action_place", f"Placed {held_ent.name} at {pos}")
            return self.last_action_result

        elif action_type == "Throw":
            if self.player_held_id is None:
                self.last_action_result = "ThrowFailed:EmptyHands"
                return self.last_action_result

            direction = data.get("direction")
            if not direction or len(direction) < 3:
                self.last_action_result = "ThrowFailed:MissingDirection"
                return self.last_action_result

            speed = float(data.get("speed", 8.0))
            dir_vec = Vec3.from_list(direction).normalized()

            held_ent = self.physics.entities.get(self.player_held_id)
            if not held_ent:
                self.player_held_id = None
                self.last_action_result = "ThrowFailed:EmptyHands"
                return self.last_action_result

            # Velocity inheritance mechanic:
            # Throw velocity = direction * speed + [0, 2.0, 0] + 0.6 * player_velocity
            inherited_vel = self.player_vel * 0.6
            throw_vel = (dir_vec * speed) + Vec3(0.0, 2.0, 0.0) + inherited_vel

            held_ent.position = Vec3(self.player_pos.x, self.player_pos.y + 0.8, self.player_pos.z)
            held_ent.velocity = throw_vel
            self.player_held_id = None
            self.last_action_result = "ThrowSuccess"
            self._record_event(
                "action_throw",
                f"Threw {held_ent.name} with velocity {throw_vel.to_list()}",
                {"inherited_player_vel": self.player_vel.to_list()}
            )
            return self.last_action_result

        else:
            self.last_action_result = f"UnknownAction:{action_type}"
            return self.last_action_result

    def get_observation(self) -> Dict[str, Any]:
        """Returns observation dictionary formatted identically to the MIT Clawblox spec."""
        held_name = None
        if self.player_held_id and self.player_held_id in self.physics.entities:
            held_name = self.physics.entities[self.player_held_id].name

        entity_dicts = [ent.to_dict() for ent in self.physics.entities.values()]

        return {
            "tick": self.tick_count,
            "game_status": self.game_status,
            "player": {
                "id": self.player_id,
                "name": self.player_name,
                "position": self.player_pos.to_list(),
                "velocity": self.player_vel.to_list(),
                "attributes": {
                    "viewOriginX": self.player_pos.x,
                    "viewOriginY": round(self.player_pos.y + 0.9, 3),
                    "viewOriginZ": self.player_pos.z,
                    "viewForwardX": 0.0,
                    "viewForwardY": 0.0,
                    "viewForwardZ": 1.0,
                    "lastActionResult": self.last_action_result,
                    "holding": held_name,
                    "isOnGround": self.is_on_ground,
                    "hunger": round(self.hunger, 1),
                    "energy": round(self.energy, 1),
                    "health": round(self.health, 1),
                    "isNearFire": self.is_near_fire,
                    "isBurning": self.is_burning,
                    "isDrowning": self.is_drowning,
                    "deathCount": self.death_count,
                    "isHungry": self.hunger < 35.0,
                    "isExhausted": self.energy < 25.0
                }
            },
            "other_players": [],
            "world": {
                "name": "Terra Haven",
                "entities": entity_dicts
            }
        }

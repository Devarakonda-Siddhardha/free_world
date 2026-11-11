"""
3D Rigid-Body Vector Physics Engine for Chronos Sanctum.
Handles kinematic integration, 3D Axis-Aligned Bounding Box (AABB) collisions,
gravity, friction, restitution, velocity inheritance, and projectile trajectories.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import math
import numpy as np


@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_list(self) -> List[float]:
        return [round(float(self.x), 3), round(float(self.y), 3), round(float(self.z), 3)]

    @classmethod
    def from_list(cls, l: List[float]) -> "Vec3":
        return cls(float(l[0]), float(l[1]), float(l[2]))

    def __add__(self, o: "Vec3") -> "Vec3":
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: "Vec3") -> "Vec3":
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vec3":
        return self * scalar

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> "Vec3":
        l = self.length()
        if l < 1e-6:
            return Vec3(0.0, 1.0, 0.0)
        return Vec3(self.x / l, self.y / l, self.z / l)

    def distance_to(self, o: "Vec3") -> float:
        return (self - o).length()


@dataclass
class AABB:
    min_pt: Vec3
    max_pt: Vec3

    def intersects(self, other: "AABB") -> bool:
        return (
            self.min_pt.x <= other.max_pt.x and self.max_pt.x >= other.min_pt.x and
            self.min_pt.y <= other.max_pt.y and self.max_pt.y >= other.min_pt.y and
            self.min_pt.z <= other.max_pt.z and self.max_pt.z >= other.min_pt.z
        )

    def contains_point(self, pt: Vec3) -> bool:
        return (
            self.min_pt.x <= pt.x <= self.max_pt.x and
            self.min_pt.y <= pt.y <= self.max_pt.y and
            self.min_pt.z <= pt.z <= self.max_pt.z
        )


@dataclass
class PhysicsEntity:
    id: int
    name: str
    entity_type: str  # "terrain", "carryable", "player"
    position: Vec3
    size: Vec3
    velocity: Vec3 = field(default_factory=Vec3)
    anchored: bool = False
    color: List[float] = field(default_factory=lambda: [0.8, 0.8, 0.8])
    shape: str = "box"  # "box", "sphere", "cylinder", "ring"
    mass: float = 1.0
    restitution: float = 0.3
    friction: float = 0.5
    attributes: Dict[str, Any] = field(default_factory=dict)

    def get_aabb(self) -> AABB:
        half_x = self.size.x / 2.0
        half_y = self.size.y / 2.0
        half_z = self.size.z / 2.0
        return AABB(
            min_pt=Vec3(self.position.x - half_x, self.position.y - half_y, self.position.z - half_z),
            max_pt=Vec3(self.position.x + half_x, self.position.y + half_y, self.position.z + half_z)
        )

    def to_dict(self) -> Dict[str, Any]:
        aabb = self.get_aabb()
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "position": self.position.to_list(),
            "size": self.size.to_list(),
            "rotation": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0]
            ],
            "aabb": {
                "min": aabb.min_pt.to_list(),
                "max": aabb.max_pt.to_list()
            },
            "obb": {
                "center": self.position.to_list(),
                "half_extents": [round(self.size.x / 2.0, 3), round(self.size.y / 2.0, 3), round(self.size.z / 2.0, 3)]
            },
            "color": self.color,
            "shape": self.shape,
            "anchored": self.anchored,
            "attributes": self.attributes
        }


class PhysicsWorld:
    def __init__(self, gravity: float = -9.81):
        self.gravity = gravity
        self.entities: Dict[int, PhysicsEntity] = {}
        self._pending_add: List[PhysicsEntity] = []
        self._in_step: bool = False
        self.next_id: int = 100
        self.impact_callbacks = []

    def add_entity(self, entity: PhysicsEntity) -> int:
        if self._in_step:
            self._pending_add.append(entity)
        else:
            self.entities[entity.id] = entity
        return entity.id

    def remove_entity(self, entity_id: int) -> Optional[PhysicsEntity]:
        return self.entities.pop(entity_id, None)

    def step(self, dt: float = 0.05):
        """Simulate rigid body dynamics for one timestep."""
        self._in_step = True
        pending_impacts = []

        try:
            for ent in list(self.entities.values()):
                if ent.anchored:
                    continue

                # Gravity
                ent.velocity.y += self.gravity * dt

                # Drag/air resistance
                ent.velocity.x *= (1.0 - 0.02 * dt * 20.0)
                ent.velocity.z *= (1.0 - 0.02 * dt * 20.0)

                # Proposed position
                new_pos = Vec3(
                    ent.position.x + ent.velocity.x * dt,
                    ent.position.y + ent.velocity.y * dt,
                    ent.position.z + ent.velocity.z * dt
                )

                # Ground collision at y = 0
                half_y = ent.size.y / 2.0
                if new_pos.y - half_y <= 0.0:
                    new_pos.y = half_y
                    impact_speed = ent.velocity.length()
                    if impact_speed > 1.0:
                        pending_impacts.append((ent, impact_speed, None))
                    if ent.velocity.y < -0.5:
                        ent.velocity.y = -ent.velocity.y * ent.restitution
                    else:
                        ent.velocity.y = 0.0
                    ent.velocity.x *= (1.0 - ent.friction * 0.2)
                    ent.velocity.z *= (1.0 - ent.friction * 0.2)

                # Collision against anchored platforms and other entities
                ent_aabb = AABB(
                    min_pt=Vec3(new_pos.x - ent.size.x / 2.0, new_pos.y - half_y, new_pos.z - ent.size.z / 2.0),
                    max_pt=Vec3(new_pos.x + ent.size.x / 2.0, new_pos.y + half_y, new_pos.z + ent.size.z / 2.0)
                )

                for other in list(self.entities.values()):
                    if other.id == ent.id:
                        continue

                    other_aabb = other.get_aabb()
                    if ent_aabb.intersects(other_aabb):
                        impact_speed = ent.velocity.length()
                        if impact_speed > 1.0:
                            pending_impacts.append((ent, impact_speed, other))

                        # Vertical landing on top of platform or block
                        if ent.position.y - half_y >= other_aabb.max_pt.y - 0.2:
                            new_pos.y = other_aabb.max_pt.y + half_y
                            if ent.velocity.y < -0.5:
                                ent.velocity.y = -ent.velocity.y * ent.restitution
                            else:
                                ent.velocity.y = 0.0
                            ent.velocity.x *= (1.0 - ent.friction * 0.3)
                            ent.velocity.z *= (1.0 - ent.friction * 0.3)
                        elif other.anchored:
                            # Horizontal rebound from anchored wall/pillar
                            ent.velocity.x = -ent.velocity.x * 0.4
                            ent.velocity.z = -ent.velocity.z * 0.4
                            new_pos.x = ent.position.x
                            new_pos.z = ent.position.z

                ent.position = new_pos

        finally:
            self._in_step = False
            for new_ent in self._pending_add:
                self.entities[new_ent.id] = new_ent
            self._pending_add.clear()

        # Fire callbacks after step completes
        for impact_ent, spd, tgt in pending_impacts:
            self._check_impact(impact_ent, spd, tgt)

    def _check_impact(self, entity: PhysicsEntity, speed: float, target: Optional[PhysicsEntity]):
        for cb in self.impact_callbacks:
            cb(entity, speed, target)

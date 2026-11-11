"""
Terra Haven Environment Definition — Expanded Vast World.
Features:
1. Expansive 320x320m terrain (Meadow, Alpine Bluffs, River Valley, Ocean Coast).
2. Ocean Coastline & Surf (z in [-160, -35]).
3. Winding Mountain River connecting Eagle's Peak, Lake, and Ocean Delta.
4. Central Campfire Hearth with interactive fire and radiant warmth.
5. Edible Berry Bushes (BerryBush_1..8) with nutritious berries for Eko and wildlife.
6. Coded Procedural Animals (Deer_1..3, Rabbit_1..3) driven by deterministic state-machine AI.
7. Flat Skipping Stones, Timber Crates, and Kinetic River Geode.
"""

from typing import List
from engine.physics import PhysicsEntity, Vec3


def create_terra_haven_entities() -> List[PhysicsEntity]:
    entities: List[PhysicsEntity] = []

    # 1. Vast Main Meadow Foundation (320m x 320m lush grass)
    entities.append(
        PhysicsEntity(
            id=1,
            name="MeadowGround",
            entity_type="terrain",
            position=Vec3(0.0, -1.0, 0.0),
            size=Vec3(320.0, 2.0, 320.0),
            anchored=True,
            color=[0.08, 0.64, 0.29],
            shape="box",
            attributes={"RenderRole": "Meadow", "Material": "LushGrass", "WorldRadius": 160.0}
        )
    )

    # 2. Vast Southern Ocean (z from -38 to -160, x from -160 to 160, y = -0.3m)
    entities.append(
        PhysicsEntity(
            id=2,
            name="OceanWater",
            entity_type="terrain",
            position=Vec3(0.0, -0.3, -95.0),
            size=Vec3(320.0, 0.6, 120.0),
            anchored=True,
            color=[0.02, 0.42, 0.72],
            shape="box",
            attributes={"RenderRole": "Ocean", "SurfaceElevation": -0.3, "Liquid": True}
        )
    )

    # Ocean Sandy Beach Shoreline (z from -30 to -40)
    entities.append(
        PhysicsEntity(
            id=3,
            name="OceanBeach",
            entity_type="terrain",
            position=Vec3(0.0, 0.05, -35.0),
            size=Vec3(320.0, 0.2, 16.0),
            anchored=True,
            color=[0.94, 0.82, 0.52],
            shape="box",
            attributes={"RenderRole": "SandyBeach", "SurfaceElevation": 0.05}
        )
    )

    # 3. Winding Mountain River (flows from north mountains down through lake to ocean)
    # Segment 1: Upper Mountain Stream (x = -22 -> -5, z = 50 -> 25)
    entities.append(
        PhysicsEntity(
            id=4,
            name="River_Upper",
            entity_type="terrain",
            position=Vec3(-12.0, -0.15, 36.0),
            size=Vec3(6.5, 0.2, 30.0),
            anchored=True,
            color=[0.12, 0.65, 0.88],
            shape="box",
            attributes={"RenderRole": "River", "SurfaceElevation": -0.15, "Liquid": True}
        )
    )

    # Segment 2: Lower River Outlet to Ocean (x = 18, z = -12 -> -35)
    entities.append(
        PhysicsEntity(
            id=5,
            name="River_Delta",
            entity_type="terrain",
            position=Vec3(18.0, -0.2, -24.0),
            size=Vec3(8.0, 0.2, 26.0),
            anchored=True,
            color=[0.10, 0.60, 0.85],
            shape="box",
            attributes={"RenderRole": "RiverDelta", "SurfaceElevation": -0.2, "Liquid": True}
        )
    )

    # River Wooden Footbridge (Crossing the river delta at z = -20)
    entities.append(
        PhysicsEntity(
            id=6,
            name="RiverBridge",
            entity_type="terrain",
            position=Vec3(18.0, 0.35, -20.0),
            size=Vec3(3.2, 0.2, 10.5),
            anchored=True,
            color=[0.55, 0.32, 0.10],
            shape="box",
            attributes={"RenderRole": "BridgeDeck", "SurfaceElevation": 0.45}
        )
    )

    # 4. Central Stone Campfire Hearth with Fire Pit (y = 0.25m)
    entities.append(
        PhysicsEntity(
            id=10,
            name="CampfireHearth",
            entity_type="terrain",
            position=Vec3(0.0, 0.125, 0.0),
            size=Vec3(7.6, 0.25, 7.6),
            anchored=True,
            color=[0.28, 0.33, 0.41],
            shape="cylinder",
            attributes={"RenderRole": "HearthDais", "SurfaceElevation": 0.25, "HasFire": True, "WarmthRadius": 6.0}
        )
    )

    # 5. Wooden Cedar Pier / Dock
    entities.append(
        PhysicsEntity(
            id=11,
            name="WoodenPier",
            entity_type="terrain",
            position=Vec3(6.0, 0.28, -10.0),
            size=Vec3(10.4, 0.16, 2.6),
            anchored=True,
            color=[0.52, 0.30, 0.05],
            shape="box",
            attributes={"RenderRole": "PierDeck", "SurfaceElevation": 0.35}
        )
    )

    # 6. Inland Shimmering Lake Basin (Water surface at y = -0.15m)
    entities.append(
        PhysicsEntity(
            id=12,
            name="LakeWater",
            entity_type="terrain",
            position=Vec3(14.0, -0.15, -10.0),
            size=Vec3(34.0, 0.1, 24.0),
            anchored=True,
            color=[0.01, 0.52, 0.78],
            shape="cylinder",
            attributes={"RenderRole": "Lake", "SurfaceElevation": -0.15, "Liquid": True}
        )
    )

    # 7. Eagle's Peak 10-Meter Mountain Cliff & Natural Step Terraces
    entities.append(
        PhysicsEntity(
            id=13,
            name="EaglesPeak_LowerRidge",
            entity_type="terrain",
            position=Vec3(-16.0, 1.25, 22.0),
            size=Vec3(5.5, 2.5, 4.0),
            anchored=True,
            color=[0.39, 0.45, 0.55],
            shape="box",
            attributes={"RenderRole": "Ledge", "SurfaceElevation": 2.5}
        )
    )
    entities.append(
        PhysicsEntity(
            id=14,
            name="EaglesPeak_MiddleRidge",
            entity_type="terrain",
            position=Vec3(-16.0, 2.5, 25.0),
            size=Vec3(5.5, 5.0, 3.8),
            anchored=True,
            color=[0.34, 0.40, 0.50],
            shape="box",
            attributes={"RenderRole": "Ledge", "SurfaceElevation": 5.0}
        )
    )
    entities.append(
        PhysicsEntity(
            id=15,
            name="EaglesPeak_Cliff",
            entity_type="terrain",
            position=Vec3(-16.0, 5.0, 29.0),
            size=Vec3(6.2, 10.0, 5.5),
            anchored=True,
            color=[0.28, 0.33, 0.41],
            shape="box",
            attributes={"RenderRole": "MountainCliff", "PeakElevation": 10.4}
        )
    )

    # 8. Nutritious Wild Berry Bushes (BerryBush_1..8)
    bush_coords = [
        (-8.0, 10.0),
        (-14.0, 8.0),
        (5.0, 12.0),
        (12.0, 8.0),
        (22.0, 4.0),
        (-6.0, -18.0),
        (-18.0, -12.0),
        (25.0, -14.0)
    ]
    for idx, (bx, bz) in enumerate(bush_coords):
        entities.append(
            PhysicsEntity(
                id=50 + idx,
                name=f"BerryBush_{idx + 1}",
                entity_type="forageable",
                position=Vec3(bx, 0.6, bz),
                size=Vec3(1.6, 1.2, 1.6),
                anchored=True,
                color=[0.15, 0.68, 0.30],
                shape="sphere",
                attributes={
                    "Kind": "BerryBush",
                    "Edible": True,
                    "BerriesCount": 6,
                    "NutritionalValue": 35.0,
                    "EnergyValue": 15.0
                }
            )
        )

    # 9. Autonomous Procedural Wildlife with Coded Behaviors (NO LFM backend)
    # Deer Herd (Graze from low tree branches and berry bushes)
    deer_positions = [
        (-18.0, 0.8, 14.0, "Deer_1"),
        (-24.0, 0.8, 20.0, "Deer_2"),
        (16.0, 0.8, 16.0, "Deer_3")
    ]
    for did, (dx, dy, dz, dname) in enumerate(deer_positions):
        entities.append(
            PhysicsEntity(
                id=70 + did,
                name=dname,
                entity_type="animal",
                position=Vec3(dx, dy, dz),
                size=Vec3(1.4, 1.5, 0.8),
                anchored=False,
                color=[0.60, 0.38, 0.18],
                shape="box",
                mass=45.0,
                attributes={
                    "Species": "Deer",
                    "State": "Grazing",
                    "Speed": 3.8,
                    "Hunger": 60.0,
                    "FearDistance": 4.5
                }
            )
        )

    # Wild Rabbits (Forage berries and scurry near bushes)
    rabbit_positions = [
        (-7.5, 0.3, 10.5, "Rabbit_1"),
        (5.5, 0.3, 11.5, "Rabbit_2"),
        (21.5, 0.3, 3.5, "Rabbit_3")
    ]
    for rid, (rx, ry, rz, rname) in enumerate(rabbit_positions):
        entities.append(
            PhysicsEntity(
                id=80 + rid,
                name=rname,
                entity_type="animal",
                position=Vec3(rx, ry, rz),
                size=Vec3(0.5, 0.45, 0.5),
                anchored=False,
                color=[0.78, 0.72, 0.65],
                shape="box",
                mass=2.5,
                attributes={
                    "Species": "Rabbit",
                    "State": "NibblingBerries",
                    "Speed": 4.2,
                    "FearDistance": 3.2
                }
            )
        )

    # 10. Flat River Skipping Stones
    stone_positions = [
        (1.2, 0.35, -8.5),
        (2.2, 0.05, -7.0),
        (0.5, 0.05, -11.5),
        (1.8, 0.05, -12.5)
    ]
    for idx, (sx, sy, sz) in enumerate(stone_positions):
        entities.append(
            PhysicsEntity(
                id=20 + idx,
                name=f"RiverStone_{idx + 1}",
                entity_type="carryable",
                position=Vec3(sx, sy, sz),
                size=Vec3(0.75, 0.22, 0.75),
                anchored=False,
                color=[0.42, 0.50, 0.60],
                shape="cylinder",
                mass=0.6,
                restitution=0.65,
                attributes={"Kind": "SkippingStone", "Hydrodynamic": True}
            )
        )

    # 11. Stackable Cedar Timber Crates
    crate_positions = [
        (-2.0, 0.25, -1.5),
        (-2.8, 0.05, 0.5),
        (2.2, 0.25, 1.8)
    ]
    for idx, (cx, cy, cz) in enumerate(crate_positions):
        entities.append(
            PhysicsEntity(
                id=30 + idx,
                name=f"TimberCrate_{idx + 1}",
                entity_type="carryable",
                position=Vec3(cx, cy + 0.45, cz),
                size=Vec3(0.9, 0.9, 0.9),
                anchored=False,
                color=[0.72, 0.45, 0.20],
                shape="box",
                mass=1.4,
                restitution=0.25,
                attributes={"Kind": "TimberCrate", "Stackable": True}
            )
        )

    # 12. Luminous River Geode
    entities.append(
        PhysicsEntity(
            id=40,
            name="RiverGeode",
            entity_type="carryable",
            position=Vec3(-4.5, 0.6, -2.5),
            size=Vec3(1.2, 1.2, 1.2),
            anchored=False,
            color=[0.35, 0.78, 0.95],
            shape="sphere",
            mass=3.8,
            restitution=0.45,
            friction=0.3,
            attributes={"Kind": "RiverGeode", "Luminous": True, "FractureThreshold": 9.5}
        )
    )

    return entities

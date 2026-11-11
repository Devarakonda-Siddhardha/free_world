"""
Chronos Sanctum Environment Definition.
Specifies the 3D celestial observatory world layout, entities, materials,
and the kinetic resonance / prism-shatter mechanics.
"""

from typing import List, Dict, Any, Tuple
from engine.physics import PhysicsEntity, Vec3


def create_chronos_sanctum_entities() -> List[PhysicsEntity]:
    entities: List[PhysicsEntity] = []

    # 1. Main Sanctuary Foundation
    entities.append(
        PhysicsEntity(
            id=1,
            name="SanctumGround",
            entity_type="terrain",
            position=Vec3(0.0, -0.5, 0.0),
            size=Vec3(70.0, 1.0, 70.0),
            anchored=True,
            color=[0.12, 0.15, 0.22],
            shape="box",
            attributes={"RenderRole": "Foundation", "Material": "ObsidianSlate"}
        )
    )

    # 2. Starlight Well (Central Circular Altar)
    entities.append(
        PhysicsEntity(
            id=2,
            name="StarlightWell",
            entity_type="terrain",
            position=Vec3(0.0, 0.1, 0.0),
            size=Vec3(8.0, 0.2, 8.0),
            anchored=True,
            color=[0.20, 0.85, 0.95],
            shape="cylinder",
            attributes={"RenderRole": "Altar", "Luminous": True}
        )
    )

    # 3. Terraced Ascents towards the Astral Spire
    entities.append(
        PhysicsEntity(
            id=3,
            name="AstralTerrace_Low",
            entity_type="terrain",
            position=Vec3(-16.0, 1.0, 12.0),
            size=Vec3(12.0, 2.0, 10.0),
            anchored=True,
            color=[0.28, 0.32, 0.46],
            shape="box",
            attributes={"RenderRole": "Terrace", "HeightLevel": 1}
        )
    )

    entities.append(
        PhysicsEntity(
            id=4,
            name="AstralTerrace_Mid",
            entity_type="terrain",
            position=Vec3(-16.0, 2.5, 22.0),
            size=Vec3(10.0, 3.0, 8.0),
            anchored=True,
            color=[0.34, 0.38, 0.56],
            shape="box",
            attributes={"RenderRole": "Terrace", "HeightLevel": 2}
        )
    )

    # 4. Astral Spire (Highest Pinnacle - Target for Climbs & Throws)
    entities.append(
        PhysicsEntity(
            id=5,
            name="AstralSpire",
            entity_type="terrain",
            position=Vec3(-16.0, 5.0, 30.0),
            size=Vec3(6.0, 10.0, 6.0),
            anchored=True,
            color=[0.60, 0.35, 0.85],
            shape="box",
            attributes={"RenderRole": "Spire", "HeightLevel": 3, "PeakElevation": 10.0}
        )
    )

    # 5. Resonant Boundary Monoliths
    entities.append(
        PhysicsEntity(
            id=6,
            name="Monolith_East",
            entity_type="terrain",
            position=Vec3(22.0, 4.0, 0.0),
            size=Vec3(3.0, 8.0, 3.0),
            anchored=True,
            color=[0.22, 0.28, 0.40],
            shape="box",
            attributes={"RenderRole": "Monolith"}
        )
    )

    entities.append(
        PhysicsEntity(
            id=7,
            name="Monolith_West",
            entity_type="terrain",
            position=Vec3(-22.0, 4.0, -12.0),
            size=Vec3(3.0, 8.0, 3.0),
            anchored=True,
            color=[0.22, 0.28, 0.40],
            shape="box",
            attributes={"RenderRole": "Monolith"}
        )
    )

    # 6. Interactive Carryable Props: Resonant Prisms (10 Prisms)
    prism_colors = [
        [0.15, 0.85, 0.82],  # Cyan
        [0.95, 0.65, 0.20],  # Amber
        [0.40, 0.90, 0.45],  # Emerald
        [0.85, 0.35, 0.75],  # Amethyst
        [0.95, 0.30, 0.35],  # Ruby
        [0.25, 0.70, 0.95],  # Sapphire
        [0.90, 0.85, 0.30],  # Topaz
        [0.55, 0.95, 0.75],  # Mint
        [0.80, 0.50, 0.95],  # Lilac
        [0.95, 0.55, 0.40],  # Coral
    ]

    base_x = 4.0
    base_z = -4.0
    for i in range(10):
        row = i // 5
        col = i % 5
        px = base_x + col * 2.2
        pz = base_z - row * 2.5
        entities.append(
            PhysicsEntity(
                id=10 + i,
                name=f"Prism_{i+1}",
                entity_type="carryable",
                position=Vec3(px, 0.5, pz),
                size=Vec3(1.0, 1.0, 1.0),
                anchored=False,
                color=prism_colors[i],
                shape="box",
                mass=1.0,
                restitution=0.25,
                attributes={"Kind": "ResonantPrism", "HarmonicTone": 220 * (1 + i * 0.1)}
            )
        )

    # 7. Dense Gravity Sphere ("AetherOrb")
    # Emergent mechanic: throwing with high velocity shatters/shards into LuxCubes
    entities.append(
        PhysicsEntity(
            id=30,
            name="AetherOrb",
            entity_type="carryable",
            position=Vec3(-4.0, 0.6, -3.0),
            size=Vec3(1.2, 1.2, 1.2),
            anchored=False,
            color=[0.42, 0.12, 0.68],
            shape="sphere",
            mass=4.5,
            restitution=0.45,
            friction=0.3,
            attributes={"Kind": "GravitySphere", "Density": "Superdense", "ResonanceThreshold": 9.5}
        )
    )

    # 8. Chronos Halo (Golden Torus/Ring)
    entities.append(
        PhysicsEntity(
            id=31,
            name="ChronosHalo",
            entity_type="carryable",
            position=Vec3(-1.0, 0.25, 6.0),
            size=Vec3(2.2, 0.35, 2.2),
            anchored=False,
            color=[0.98, 0.85, 0.20],
            shape="ring",
            mass=1.2,
            restitution=0.3,
            attributes={"Kind": "ChronosHalo", "Aura": "Golden"}
        )
    )

    return entities

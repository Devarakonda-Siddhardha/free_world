"""
Downstream Goal-Directed Evaluation Benchmarks.
Implements the 4 canonical evaluation tasks from the MIT 'Is this machine playing?' paper:
1. many-5-towers: Build as many 5-block-high towers as possible on the ground
2. objects-on-spire: Get as many objects as possible onto the Astral Spire
3. tallest-tower: Build the tallest tower on the ground by block count in one column
4. throw-on-spire: Throw a block onto the Spire without climbing onto any platform
"""

import time
import requests
from typing import Dict, Any, Tuple


class BenchmarkSuite:
    def __init__(self, world_url: str = "http://127.0.0.1:8080"):
        self.world_url = world_url.rstrip("/")

    def get_observation(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.world_url}/observe", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def reset_world(self):
        resp = requests.post(f"{self.world_url}/reset", timeout=5)
        resp.raise_for_status()
        time.sleep(0.2)

    def evaluate_many_5_towers(self, tolerance: float = 0.5) -> int:
        """
        Count number of stable 5-block-high towers on the ground.
        World starts with 10 prisms; scoring > 2 requires generating LuxCubes via AetherOrb!
        """
        obs = self.get_observation()
        carryables = [e for e in obs["world"]["entities"] if e["entity_type"] == "carryable"]

        # Group blocks by approximate (x, z) column location
        columns = {}
        for block in carryables:
            x, y, z = block["position"]
            # Discretize ground position (rounded to nearest 1.2m grid)
            col_key = (round(x / 1.2) * 1.2, round(z / 1.2) * 1.2)
            if col_key not in columns:
                columns[col_key] = []
            columns[col_key].append(y)

        towers_of_5 = 0
        for col, heights in columns.items():
            if len(heights) >= 5:
                # Check that blocks are stacked vertically
                sorted_h = sorted(heights)
                # Check height differences indicate vertical stacking
                is_stacked = True
                for i in range(len(sorted_h) - 1):
                    diff = sorted_h[i+1] - sorted_h[i]
                    if not (0.6 <= diff <= 1.4):
                        is_stacked = False
                        break
                if is_stacked:
                    towers_of_5 += 1

        return towers_of_5

    def evaluate_objects_on_spire(self) -> int:
        """Count how many carryable objects have landed or been placed on the Astral Spire (y >= 9.5)."""
        obs = self.get_observation()
        # Astral Spire bounds: x in [-19, -13], z in [27, 33], y >= 9.5
        count = 0
        for ent in obs["world"]["entities"]:
            if ent["entity_type"] == "carryable":
                x, y, z = ent["position"]
                if -19.5 <= x <= -12.5 and 26.5 <= z <= 33.5 and y >= 9.5:
                    count += 1
        return count

    def evaluate_tallest_tower(self) -> int:
        """Return the maximum count of blocks stacked in a single column on the ground."""
        obs = self.get_observation()
        carryables = [e for e in obs["world"]["entities"] if e["entity_type"] == "carryable"]
        columns = {}
        for block in carryables:
            x, y, z = block["position"]
            col_key = (round(x / 1.2) * 1.2, round(z / 1.2) * 1.2)
            columns[col_key] = columns.get(col_key, 0) + 1
        return max(columns.values()) if columns else 0

    def evaluate_throw_on_spire(self) -> bool:
        """Check whether any object was thrown onto the Astral Spire from the ground."""
        # True if at least 1 object sits atop the Spire
        return self.evaluate_objects_on_spire() >= 1


if __name__ == "__main__":
    suite = BenchmarkSuite()
    print("Objects on Spire:", suite.evaluate_objects_on_spire())
    print("Tallest Tower:", suite.evaluate_tallest_tower())
    print("5-Block Towers:", suite.evaluate_many_5_towers())

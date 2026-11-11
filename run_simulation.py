"""
Chronos Sanctum — Main Simulation CLI Runner.
Launches the 3D World HTTP server, web inspector, and Liquid AI LFM3 agent.

Usage:
  python3 run_simulation.py               # Starts World Server + Agent in background
  python3 run_simulation.py --mode server # Starts World Server + 3D Visualizer on http://localhost:8080
  python3 run_simulation.py --mode agent  # Runs agent session against running server
  python3 run_simulation.py --mode ablate # Runs Causal Memory Ablation Study
"""

import argparse
import sys
import os
import time
import threading
import uvicorn
from engine.server import app, world
from agent.harness import AgentHarness
from evaluation.memory_ablation import MemoryAblationStudy


def start_server(port: int = 8080):
    print(f"[Chronos Sanctum] Starting World HTTP Server & 3D Inspector on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def main():
    parser = argparse.ArgumentParser(description="Chronos Sanctum: Autonomous Machine Play with Liquid AI LFM3")
    parser.add_argument("--mode", choices=["all", "server", "agent", "ablate"], default="all",
                        help="Execution mode (default: all)")
    parser.add_argument("--port", type=int, default=8080, help="World server port (default: 8080)")
    parser.add_argument("--steps", type=int, default=6, help="Agent steps per session (default: 6)")
    parser.add_argument("--backend", choices=["auto", "simulated", "api", "local"], default="auto",
                        help="Liquid AI backend mode (default: auto)")

    args = parser.parse_args()

    if args.mode == "server":
        start_server(args.port)

    elif args.mode == "ablate":
        study = MemoryAblationStudy(world_url=f"http://127.0.0.1:{args.port}")
        study.run_study()

    elif args.mode == "agent":
        harness = AgentHarness(world_url=f"http://127.0.0.1:{args.port}", backend_mode=args.backend)
        harness.run_session(session_number=1, step_limit=args.steps)

    elif args.mode == "all":
        # Launch server in background thread
        server_thread = threading.Thread(target=start_server, args=(args.port,), daemon=True)
        server_thread.start()

        time.sleep(1.5)  # Wait for server startup
        print("\n" + "="*68)
        print("  CHRONOS SANCTUM SIMULATION ENGINE READY")
        print(f"  3D Web Inspector & Live Replay: http://localhost:{args.port}/")
        print(f"  API Documentation: http://localhost:{args.port}/api.md")
        print("="*68 + "\n")

        # Run agent harness
        harness = AgentHarness(world_url=f"http://127.0.0.1:{args.port}", backend_mode=args.backend)
        harness.run_session(session_number=1, step_limit=args.steps)

        print("\n[Chronos Sanctum] Session completed. Server remains active for inspection. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nShutting down simulation.")


if __name__ == "__main__":
    main()

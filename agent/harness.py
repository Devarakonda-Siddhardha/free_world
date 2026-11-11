"""
Autonomous Agent Orchestration Harness for Liquid AI LFM3-1.7B.
Manages the agent lifecycle:
- Workspace file mounting and persistent memory management
- Tool execution (bash commands against the World API)
- Auto-continue loop ("Please don't stop. Just continue doing whatever you want to do.")
- 5-minute pre-reset warning ("You will be reset in 5 minutes. Update your workspace memory files now.")
- Hourly session resets while preserving workspace files across cycles
"""

import os
import sys
import time
import json
import re
import subprocess
import requests
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.backend import LiquidLFM3Backend


class AgentHarness:
    def __init__(
        self,
        world_url: str = "http://127.0.0.1:8080",
        workspace_dir: Optional[str] = None,
        backend_mode: str = "auto",
        cycle_duration_seconds: float = 300.0  # Configurable session cycle (5 min for demos, 3600s for full runs)
    ):
        self.world_url = world_url.rstrip("/")
        self.workspace_dir = workspace_dir or os.path.join(os.path.dirname(__file__), "workspace")
        self.cycle_duration = cycle_duration_seconds
        self.backend = LiquidLFM3Backend(mode=backend_mode)
        self.session_token: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.is_running: bool = False
        self.total_sessions_completed: int = 0
        self.log_callbacks = []

    def log(self, level: str, msg: str):
        formatted = f"[{time.strftime('%H:%M:%S')}][Harness][{level}] {msg}"
        print(formatted)
        for cb in self.log_callbacks:
            cb(level, msg)

    def load_workspace_file(self, filename: str) -> str:
        filepath = os.path.join(self.workspace_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_workspace_file(self, filename: str, content: str):
        filepath = os.path.join(self.workspace_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def append_workspace_file(self, filename: str, content: str):
        filepath = os.path.join(self.workspace_dir, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)

    def join_world(self) -> str:
        """Connects to the world HTTP server to register session."""
        try:
            resp = requests.post(f"{self.world_url}/join?name=Eko", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.session_token = data.get("session", "session-eko-chronos")
            self.log("INFO", f"Connected to world server at {self.world_url}. Session token: {self.session_token}")
            return self.session_token
        except Exception as e:
            self.log("WARN", f"Failed to join world server ({e}). Using local session token.")
            self.session_token = "session-eko-chronos"
            return self.session_token

    def build_system_prompt(self) -> str:
        soul = self.load_workspace_file("SOUL.md")
        semantic = self.load_workspace_file("SEMANTIC_MEMORY.md")
        episodic_guide = self.load_workspace_file("EPISODIC_MEMORY.md")

        # Extract last 5 episodic summaries
        episodic_lines = []
        episodic_path = os.path.join(self.workspace_dir, "EPISODIC_MEMORY.jsonl")
        if os.path.exists(episodic_path):
            with open(episodic_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            episodic_lines.append(f"- {item.get('summary', '')}")
                        except Exception:
                            pass
        recent_episodic = "\n".join(episodic_lines[-8:])

        system_prompt = f"""You are a being living in your world.
Your name is Eko.
Your workspace is {self.workspace_dir}. Only work inside this directory.
Make sure to keep your workspace clean and well organized.
The files in your workspace are yours to evolve.
These files are your memory that persists across sessions. Anything not in your workspace will be forgotten.

Among your workspace, you have memory files:
- EPISODIC_MEMORY.md describes how to record what happened. Actual entries are appended to EPISODIC_MEMORY.jsonl — never rewrite or delete old ones.
- SEMANTIC_MEMORY.md is for techniques and knowledge you have learned.

Embody SOUL.md's persona and tone:
{soul}

Recent memories from prior sessions:
{recent_episodic}

Verified semantic knowledge:
{semantic}

When starting a new session, start by reading the files in your workspace to refresh your memory.
Periodically take a step back and revise your workspace and memory files. You don't want to forget what you have experienced and learned.

World base URL: {self.world_url}
X-Session: {self.session_token}

Fetch capabilities with: curl -sS -H 'X-Session: {self.session_token}' {self.world_url}/api.md
"""
        return system_prompt

    def execute_bash_commands(self, text: str) -> str:
        """Extracts and executes bash scripts against the world API or workspace."""
        code_blocks = re.findall(r"```bash\s*(.*?)\s*```", text, re.DOTALL)
        if not code_blocks:
            return ""

        outputs = []
        for block in code_blocks:
            # Substitute environment variables & world URLs
            script = block
            script = script.replace("http://world", self.world_url)
            script = script.replace("$X_SESSION", self.session_token or "")
            script = script.replace("/workspace", self.workspace_dir)

            try:
                proc = subprocess.run(
                    script,
                    shell=True,
                    executable="/bin/bash",
                    cwd=self.workspace_dir,
                    capture_output=True,
                    text=True,
                    timeout=25
                )
                stdout = proc.stdout.strip()
                stderr = proc.stderr.strip()
                out = stdout if stdout else (stderr if stderr else "(command executed successfully)")
                outputs.append(f"$ {block.strip()}\n{out}")
            except subprocess.TimeoutExpired:
                outputs.append(f"$ {block.strip()}\nError: Command timed out after 25s.")
            except Exception as e:
                outputs.append(f"$ {block.strip()}\nExecution error: {e}")

        return "\n\n".join(outputs)

    def run_step(self, user_msg: str) -> str:
        """Executes a single conversational agentic step."""
        self.conversation_history.append({"role": "user", "content": user_msg})

        # Generate response from Liquid AI backend
        self.log("INFO", f"Invoking Liquid AI LFM3-1.7B with {len(self.conversation_history)} messages...")
        response_text = self.backend.generate(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response_text})

        # Execute any bash tool calls
        cmd_output = self.execute_bash_commands(response_text)
        if cmd_output:
            self.log("DEBUG", f"Tool Output:\n{cmd_output[:250]}...")
            self.conversation_history.append({
                "role": "user",
                "content": f"[Terminal Output]\n{cmd_output}"
            })

        return response_text

    def run_session(self, session_number: int = 1, initial_prompt: str = "Begin", step_limit: int = 8):
        """Runs a complete autonomous session cycle."""
        self.log("INFO", f"=== STARTING SESSION #{session_number} ===")
        self.join_world()

        # Build clean session context
        system_prompt = self.build_system_prompt()
        self.conversation_history = [
            {"role": "system", "content": system_prompt}
        ]

        # Initial prompt
        self.run_step(initial_prompt)

        # Autonomous continuation loop
        for step in range(1, step_limit):
            # Check if near end of session cycle -> trigger memory consolidation alert
            if step == step_limit - 1:
                prompt = "You will be reset in 5 minutes. Update your workspace memory files now."
            else:
                prompt = "Please don't stop. Just continue doing whatever you want to do."

            time.sleep(1.0)
            self.run_step(prompt)

        self.total_sessions_completed += 1
        self.log("INFO", f"=== COMPLETED SESSION #{session_number} (Hourly Context Compaction & World Reset) ===")

        # Reset world physical entities (preserving workspace files!)
        try:
            requests.post(f"{self.world_url}/reset", timeout=5)
        except Exception:
            pass


if __name__ == "__main__":
    harness = AgentHarness()
    harness.run_session(session_number=1, step_limit=5)

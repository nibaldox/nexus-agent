"""
Squad Tools - Infrastructure for Team of Teams
Handles coordination, status tracking, and parallel task management
"""
import os
import json
import time
from typing import Dict, List, Optional
from agno.tools import Toolkit
from agno.utils.log import log_info

class SquadTools(Toolkit):
    """Toolkit for managing multi-agent squad coordination and status."""

    def __init__(self, status_file: str = "workspace/squad_status.json"):
        super().__init__(name="squad_tools")
        self.status_file = status_file
        self._ensure_status_file()
        
        self.register(self.update_squad_status)
        self.register(self.get_squad_status)
        self.register(self.create_shared_variable)
        self.register(self.get_shared_variable)
        self.register(self.plan_squad_mission)

    def _ensure_status_file(self):
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        if not os.path.exists(self.status_file):
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump({"squads": {}, "variables": {}, "tasks": []}, f)

    def update_squad_status(self, squad_name: str, agent_name: str, activity: str, progress: int = 0) -> str:
        """
        Update the current activity and progress of a squad member.
        
        Args:
            squad_name: Name of the squad (e.g., 'Development')
            agent_name: Name of the agent (e.g., 'Frontend Expert')
            activity: Current task description
            progress: Progress percentage (0-100)
        """
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if squad_name not in data["squads"]:
                data["squads"][squad_name] = {}
            
            data["squads"][squad_name][agent_name] = {
                "activity": activity,
                "progress": progress,
                "last_update": time.time()
            }

            # Also update task-scoped view when available
            task_id = os.getenv("NEXUS_TASK_ID")
            if task_id and isinstance(data.get("tasks"), list):
                for task in data["tasks"]:
                    if task.get("id") == task_id:
                        task.setdefault("agents", {})
                        task["agents"][agent_name] = {
                            "activity": activity,
                            "progress": progress,
                            "last_update": time.time(),
                            "squad": squad_name
                        }
                        task["updated_at"] = time.time()
                        if progress >= 100:
                            task["status"] = "COMPLETED"
                        break
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            log_info(f"Squad {squad_name} | {agent_name}: {activity} ({progress}%)")
            return f"Status updated for {agent_name} in {squad_name} squad."
        except Exception as e:
            return f"Error updating status: {str(e)}"

    def start_task(self, title: str, session_id: str = "default") -> str:
        """
        Create a task entry for the UI panel.

        Args:
            title: Task title shown in UI
            session_id: Session identifier
        """
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "tasks" not in data or not isinstance(data["tasks"], list):
                data["tasks"] = []

            task_id = f"task_{int(time.time())}"
            task = {
                "id": task_id,
                "title": title,
                "session_id": session_id,
                "status": "RUNNING",
                "created_at": time.time(),
                "updated_at": time.time(),
                "agents": {}
            }
            data["tasks"].append(task)

            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return task_id
        except Exception as e:
            return f"Error starting task: {str(e)}"

    def get_squad_status(self, squad_name: Optional[str] = None) -> str:
        """Retrieve the current status of all squads or a specific one."""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if squad_name:
                status = data["squads"].get(squad_name, {})
                return json.dumps(status, indent=2)
            return json.dumps(data["squads"], indent=2)
        except Exception as e:
            return f"Error reading status: {str(e)}"

    def create_shared_variable(self, key: str, value: any) -> str:
        """
        Save a variable to the squad's shared memory.
        Use this for sharing data between agents without writing full files.
        """
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["variables"][key] = {
                "value": value,
                "updated_at": time.time()
            }
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return f"Shared variable '{key}' saved."
        except Exception as e:
            return f"Error creating shared variable: {str(e)}"

    def get_shared_variable(self, key: str) -> str:
        """Retrieve a variable from the squad's shared memory."""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            var = data["variables"].get(key)
            if var:
                return f"Value of '{key}': {var['value']}"
            return f"Variable '{key}' not found in shared memory."
        except Exception as e:
            return f"Error reading shared variable: {str(e)}"

    def plan_squad_mission(self, mission_name: str, assignments: List[Dict[str, str]]) -> str:
        """
        Define a plan for the squad.
        
        Args:
            mission_name: Name of the mission
            assignments: List of dicts like [{"agent": "Backend Expert", "task": "Create API"}]
        """
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            plan_id = f"plan_{int(time.time())}"
            data["squads"][mission_name] = {
                "mission": mission_name,
                "assignments": assignments,
                "status": "PLANNED",
                "logs": []
            }
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return f"Mission '{mission_name}' planned with {len(assignments)} assignments. ID: {plan_id}"
        except Exception as e:
            return f"Error planning mission: {str(e)}"

# Export tool instances
squad_tools = SquadTools()
update_squad_status = squad_tools.update_squad_status
get_squad_status = squad_tools.get_squad_status
create_shared_variable = squad_tools.create_shared_variable
get_shared_variable = squad_tools.get_shared_variable
plan_squad_mission = squad_tools.plan_squad_mission
start_task = squad_tools.start_task

"""
Load season configurations and command libraries.
"""

import json
import os
from typing import Optional
from path_planner.core.commands import Command, CommandSequence


class SeasonLoader:
    """Loads commands from command_library/ and season configs."""
    
    def __init__(self, base_path: str):
        """
        Initialize the loader.
        
        Args:
            base_path: Path to the shulib-path-planner directory
        """
        self.base_path = base_path
        self.command_library_path = os.path.join(base_path, "command_library")
        self.seasons_path = os.path.join(base_path, "seasons")
        
        self.commands: dict[str, Command] = {}
        self.sequences: dict[str, CommandSequence] = {}
        self.season_config: dict = {}
    
    def load_season(self, season_name: str) -> bool:
        """
        Load a season configuration.
        
        Args:
            season_name: Folder name (e.g., "pushback_2026")
        
        Returns:
            True if successful
        """
        config_path = os.path.join(self.seasons_path, season_name, "config.json")
        
        if not os.path.exists(config_path):
            print(f"Season config not found: {config_path}")
            # Load default commands anyway
            self._load_default_commands()
            return False
        
        try:
            with open(config_path, 'r') as f:
                self.season_config = json.load(f)
        except Exception as e:
            print(f"Error loading season config: {e}")
            self._load_default_commands()
            return False
        
        self.commands.clear()
        self.sequences.clear()
        
        # Load commands from command library
        for category in self.season_config.get("include_commands_from", []):
            self._load_command_category(category)
        
        # Apply overrides
        for cmd_id, overrides in self.season_config.get("command_overrides", {}).items():
            if cmd_id in self.commands:
                if "name" in overrides:
                    self.commands[cmd_id].name = overrides["name"]
                if "code_template" in overrides:
                    self.commands[cmd_id].code_template = overrides["code_template"]
                if "description" in overrides:
                    self.commands[cmd_id].description = overrides["description"]
        
        # Load custom commands
        for cmd_data in self.season_config.get("custom_commands", []):
            cmd = Command.from_dict(cmd_data)
            self.commands[cmd.id] = cmd
        
        # Load sequences
        for seq_data in self.season_config.get("command_sequences", []):
            seq = CommandSequence.from_dict(seq_data)
            self.sequences[seq.id] = seq
        
        return True
    
    def _load_command_category(self, category: str) -> None:
        """Load commands from a category JSON file."""
        file_path = os.path.join(self.command_library_path, f"{category}.json")
        
        if not os.path.exists(file_path):
            print(f"Command category not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading command category {category}: {e}")
            return
        
        category_name = data.get("category", category)
        
        for cmd_data in data.get("commands", []):
            cmd_data["category"] = category_name
            cmd = Command.from_dict(cmd_data)
            self.commands[cmd.id] = cmd
    
    def _load_default_commands(self) -> None:
        """Load a minimal set of default commands."""
        defaults = [
            Command("intake_in", "Intake In", "mech.intakeIn();", "#00FF00", "Intake"),
            Command("intake_out", "Intake Out", "mech.intakeOut();", "#FF6600", "Intake"),
            Command("intake_stop", "Intake Stop", "mech.intakeStop();", "#006600", "Intake"),
            Command("conveyor_up", "Conveyor Up", "mech.conveyorUp();", "#0088FF", "Conveyor"),
            Command("conveyor_down", "Conveyor Down", "mech.conveyorDown();", "#0044AA", "Conveyor"),
            Command("conveyor_stop", "Conveyor Stop", "mech.conveyorStop();", "#002266", "Conveyor"),
            Command("scorer_forward", "Releaser →", "mech.releaserForward();", "#FF0000", "Scorer"),
            Command("scorer_backward", "Releaser ←", "mech.releaserBackward();", "#AA0000", "Scorer"),
            Command("scorer_stop", "Releaser Stop", "mech.releaserStop();", "#660000", "Scorer"),
            Command("arm_toggle", "Toggle Arm", "mech.toggleArm();", "#FF00FF", "Pneumatics"),
            Command("lever_toggle", "Toggle Lever", "mech.toggleLever();", "#AA00AA", "Pneumatics"),
            Command("wait_100", "Wait 100ms", "pros::delay(100);", "#888888", "Timing"),
            Command("wait_250", "Wait 250ms", "pros::delay(250);", "#888888", "Timing"),
            Command("wait_500", "Wait 500ms", "pros::delay(500);", "#888888", "Timing"),
            Command("wait_1000", "Wait 1s", "pros::delay(1000);", "#888888", "Timing"),
        ]
        
        for cmd in defaults:
            self.commands[cmd.id] = cmd
    
    def get_command(self, cmd_id: str) -> Optional[Command]:
        """Get a command by ID."""
        return self.commands.get(cmd_id)
    
    def get_commands_by_category(self) -> dict[str, list[Command]]:
        """Get all commands grouped by category."""
        by_category: dict[str, list[Command]] = {}
        
        for cmd in self.commands.values():
            if cmd.category not in by_category:
                by_category[cmd.category] = []
            by_category[cmd.category].append(cmd)
        
        return by_category
    
    def list_seasons(self) -> list[str]:
        """List available seasons."""
        seasons = []
        if os.path.exists(self.seasons_path):
            for item in os.listdir(self.seasons_path):
                item_path = os.path.join(self.seasons_path, item)
                config_path = os.path.join(item_path, "config.json")
                if os.path.isdir(item_path) and os.path.exists(config_path):
                    seasons.append(item)
        return seasons
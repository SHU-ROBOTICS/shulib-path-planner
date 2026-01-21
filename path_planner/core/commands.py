"""
Command system for mechanism actions.

Commands are loaded from JSON files in command_library/ and seasons/.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CommandParameter:
    """A parameter for a command (e.g., velocity, duration)."""
    name: str
    type: str              # "int", "float", "bool", "string"
    default: any
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    description: str = ""


@dataclass
class Command:
    """A single command that can be assigned to a waypoint."""
    id: str                # Unique identifier (e.g., "intake_in")
    name: str              # Display name (e.g., "Intake In")
    code_template: str     # C++ code (e.g., "mech.intakeIn();")
    color: str = "#FFFFFF" # Hex color for UI
    category: str = "Misc" # Category for grouping
    description: str = ""
    parameters: list[CommandParameter] = field(default_factory=list)
    
    def generate_code(self, param_values: Optional[dict] = None) -> str:
        """
        Generate C++ code with parameters filled in.
        
        Args:
            param_values: Dict of parameter name -> value
        
        Returns:
            C++ code string
        """
        code = self.code_template
        
        if param_values:
            for name, value in param_values.items():
                code = code.replace(f"{{{name}}}", str(value))
        
        return code
    
    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        """Create from dictionary."""
        params = []
        for p in data.get("parameters", []):
            params.append(CommandParameter(
                name=p["name"],
                type=p.get("type", "int"),
                default=p.get("default", 0),
                min_val=p.get("min"),
                max_val=p.get("max"),
                description=p.get("description", "")
            ))
        
        return cls(
            id=data["id"],
            name=data["name"],
            code_template=data["code_template"],
            color=data.get("color", "#FFFFFF"),
            category=data.get("category", "Misc"),
            description=data.get("description", ""),
            parameters=params
        )


@dataclass
class CommandSequence:
    """A sequence of commands that run together."""
    id: str
    name: str
    command_ids: list[str]  # List of command IDs to execute in order
    color: str = "#FFFFFF"
    category: str = "Sequences"
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "CommandSequence":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            command_ids=data.get("commands", []),
            color=data.get("color", "#FFFFFF"),
            category=data.get("category", "Sequences"),
            description=data.get("description", "")
        )
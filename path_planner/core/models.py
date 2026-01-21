"""
Core data models for the path planner.

- Waypoint: A single point with position, heading, and commands
- Path: A sequence of waypoints forming an autonomous routine
- Project: A collection of paths
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class MotionType(Enum):
    """How the robot moves to reach a waypoint."""
    START = "start"                  # First waypoint, just sets position
    MOVE_TO_POSE = "moveToPose"      # Navigate to (x, y) with heading
    MOVE_VERTICAL = "moveVertical"   # Drive straight forward/backward
    ROTATE_TO = "rotateTo"           # Turn in place


class HeadingMode(Enum):
    """How heading is determined at a waypoint."""
    AUTO = "auto"      # Calculate from direction to next waypoint
    MANUAL = "manual"  # User specifies exact angle


class Side(Enum):
    """Which side of the field for autonomous."""
    LEFT = "left"    # x < 0
    RIGHT = "right"  # x > 0
    FULL = "full"    # Full field (skills)


class Alliance(Enum):
    """Alliance color."""
    RED = "red"
    BLUE = "blue"


@dataclass
class Waypoint:
    """A single waypoint in an autonomous path."""
    x: float                                    # Position in inches
    y: float                                    # Position in inches
    heading: Optional[float] = None             # Degrees, None = auto
    heading_mode: HeadingMode = HeadingMode.AUTO
    motion_type: MotionType = MotionType.MOVE_TO_POSE
    reverse: bool = False                       # Drive backwards
    intaking: bool = False                      # Run intake while moving
    conveyor: bool = False                      # Run conveyor while moving
    commands_after: list[str] = field(default_factory=list)  # Command IDs
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "heading": self.heading,
            "heading_mode": self.heading_mode.value,
            "motion_type": self.motion_type.value,
            "reverse": self.reverse,
            "intaking": self.intaking,
            "conveyor": self.conveyor,
            "commands_after": self.commands_after.copy()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Waypoint":
        """Create from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            heading=data.get("heading"),
            heading_mode=HeadingMode(data.get("heading_mode", "auto")),
            motion_type=MotionType(data.get("motion_type", "moveToPose")),
            reverse=data.get("reverse", False),
            intaking=data.get("intaking", False),
            conveyor=data.get("conveyor", False),
            commands_after=data.get("commands_after", [])
        )


@dataclass
class Path:
    """A complete autonomous path."""
    name: str
    alliance: Alliance = Alliance.RED
    side: Side = Side.LEFT
    waypoints: list[Waypoint] = field(default_factory=list)
    
    def add_waypoint(self, x: float, y: float) -> int:
        """Add a waypoint and return its index."""
        motion = MotionType.START if len(self.waypoints) == 0 else MotionType.MOVE_TO_POSE
        wp = Waypoint(x=x, y=y, motion_type=motion)
        self.waypoints.append(wp)
        return len(self.waypoints) - 1
    
    def remove_waypoint(self, index: int) -> None:
        """Remove waypoint at index."""
        if 0 <= index < len(self.waypoints):
            self.waypoints.pop(index)
            # Make first waypoint a START if we removed it
            if index == 0 and len(self.waypoints) > 0:
                self.waypoints[0].motion_type = MotionType.START
    
    def is_valid_position(self, x: float, y: float) -> bool:
        """Check if position is allowed for this path's side."""
        if self.side == Side.FULL:
            return True
        elif self.side == Side.LEFT:
            return x <= 0
        else:  # RIGHT
            return x >= 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "alliance": self.alliance.value,
            "side": self.side.value,
            "waypoints": [w.to_dict() for w in self.waypoints]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Path":
        """Create from dictionary."""
        path = cls(
            name=data["name"],
            alliance=Alliance(data.get("alliance", "red")),
            side=Side(data.get("side", "left"))
        )
        path.waypoints = [Waypoint.from_dict(w) for w in data.get("waypoints", [])]
        return path


@dataclass
class Project:
    """A project containing multiple paths."""
    season: str = "pushback_2026"
    paths: list[Path] = field(default_factory=list)
    
    def add_path(self, name: str) -> int:
        """Add a new path and return its index."""
        self.paths.append(Path(name=name))
        return len(self.paths) - 1
    
    def remove_path(self, index: int) -> None:
        """Remove path at index."""
        if 0 <= index < len(self.paths):
            self.paths.pop(index)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": "1.0.0",
            "season": self.season,
            "paths": [p.to_dict() for p in self.paths]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create from dictionary."""
        project = cls(season=data.get("season", "pushback_2026"))
        project.paths = [Path.from_dict(p) for p in data.get("paths", [])]
        return project
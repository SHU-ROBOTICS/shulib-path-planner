"""
Save and load project files (.shupaths).

Project files are JSON with the .shupaths extension.
"""

import json
import os
from datetime import datetime
from typing import Optional
from path_planner.core.models import Project, Path, Waypoint


VERSION = "1.0.0"


def save_project(project: Project, filepath: str) -> bool:
    """
    Save a project to a .shupaths file.
    
    Args:
        project: The project to save
        filepath: Path to save to (should end in .shupaths)
    
    Returns:
        True if successful
    """
    try:
        data = project.to_dict()
        data["version"] = VERSION
        data["modified"] = datetime.now().isoformat()
        
        if "created" not in data:
            data["created"] = data["modified"]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error saving project: {e}")
        return False


def load_project(filepath: str) -> Optional[Project]:
    """
    Load a project from a .shupaths file.
    
    Args:
        filepath: Path to the .shupaths file
    
    Returns:
        Project object, or None if loading failed
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Version check
        file_version = data.get("version", "0.0.0")
        if not _is_compatible_version(file_version):
            print(f"Warning: File version {file_version} may not be compatible")
        
        return Project.from_dict(data)
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file: {e}")
        return None
    except Exception as e:
        print(f"Error loading project: {e}")
        return None


def _is_compatible_version(file_version: str) -> bool:
    """Check if a file version is compatible with current version."""
    try:
        file_major = int(file_version.split('.')[0])
        current_major = int(VERSION.split('.')[0])
        return file_major <= current_major
    except:
        return False


def create_new_project(season: str = "pushback_2026") -> Project:
    """
    Create a new empty project.
    
    Args:
        season: Season identifier
    
    Returns:
        New Project object with one empty path
    """
    project = Project(season=season)
    project.add_path("New Path")
    return project


def get_project_info(filepath: str) -> Optional[dict]:
    """
    Get basic info about a project file without fully loading it.
    
    Returns:
        Dict with name, season, path count, modified date
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return {
            "season": data.get("season", "unknown"),
            "path_count": len(data.get("paths", [])),
            "modified": data.get("modified", "unknown"),
            "version": data.get("version", "unknown")
        }
    except:
        return None
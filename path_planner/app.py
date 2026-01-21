"""
shulib Path Planner - Main Application

Entry point for the path planner application.
"""

import os
import sys


class PathPlannerApp:
    """
    Main application class.
    
    Handles initialization and running the application.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.base_path = self._find_base_path()
        self.window = None
    
    def _find_base_path(self) -> str:
        """
        Find the base path of the application.
        
        Returns:
            Path to the shulib-path-planner directory
        """
        # Try to find based on this file's location
        this_file = os.path.abspath(__file__)
        path_planner_dir = os.path.dirname(this_file)  # path_planner/
        base_dir = os.path.dirname(path_planner_dir)   # shulib-path-planner/
        
        # Verify it looks correct
        if os.path.exists(os.path.join(base_dir, "seasons")):
            return base_dir
        
        # Fall back to current directory
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "seasons")):
            return cwd
        
        # Last resort: use the path_planner parent
        return base_dir
    
    def run(self) -> None:
        """Run the application."""
        # Import here to avoid issues if tkinter isn't available
        from path_planner.ui.main_window import MainWindow
        
        # Create and run main window
        self.window = MainWindow(self.base_path)
        self.window.mainloop()


def main():
    """Main entry point."""
    app = PathPlannerApp()
    app.run()


if __name__ == "__main__":
    main()
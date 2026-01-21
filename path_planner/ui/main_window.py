"""
Main application window.

Assembles all UI components and manages their interactions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional

from path_planner.core.models import Project, Path, Waypoint
from path_planner.core.undo import UndoManager
from path_planner.io.project_io import save_project, load_project, create_new_project
from path_planner.io.season_loader import SeasonLoader
from path_planner.io.export_cpp import export_path_to_cpp, export_function_only
from path_planner.io.export_clipboard import copy_to_clipboard

from path_planner.ui.field_canvas import FieldCanvas
from path_planner.ui.waypoint_panel import WaypointPanel
from path_planner.ui.command_panel import CommandPanel
from path_planner.ui.path_panel import PathPanel
from path_planner.ui.toolbar import Toolbar, StatusBar
from path_planner.ui.dialogs import ExportDialog, AboutDialog, ask_save_changes


class MainWindow(tk.Tk):
    """
    Main application window.
    """
    
    def __init__(self, base_path: str):
        super().__init__()
        
        self.base_path = base_path
        self.title("shulib Path Planner")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # State
        self.project: Optional[Project] = None
        self.current_filepath: Optional[str] = None
        self.modified = False
        
        # Season loader
        self.season_loader = SeasonLoader(base_path)
        
        # Undo manager
        self.undo_manager = UndoManager()
        self.undo_manager.on_change(self._update_undo_buttons)
        
        # Apply dark theme
        self._setup_theme()
        
        # Create UI
        self._create_menu()
        self._create_layout()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create new project by default
        self._new_project("pushback_2026")
    
    def _setup_theme(self) -> None:
        """Setup dark theme."""
        style = ttk.Style()
        
        # Try to use a dark theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure colors
        style.configure(".", background="#2d2d2d", foreground="#ffffff")
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
        style.configure("TLabelframe", background="#2d2d2d", foreground="#ffffff")
        style.configure("TLabelframe.Label", background="#2d2d2d", foreground="#ffffff")
        style.configure("TButton", background="#3d3d3d", foreground="#ffffff")
        style.configure("TCheckbutton", background="#2d2d2d", foreground="#ffffff")
        style.configure("TRadiobutton", background="#2d2d2d", foreground="#ffffff")
        
        self.configure(bg="#2d2d2d")
    
    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", accelerator="Ctrl+N", command=self._on_new)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self._on_open)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self._on_save)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export C++...", accelerator="Ctrl+E", command=self._on_export)
        file_menu.add_command(label="Copy Code to Clipboard", command=lambda: self._on_export(clipboard=True))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self._on_undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self._on_redo)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_layout(self) -> None:
        """Create the main layout."""
        # Toolbar
        self.toolbar = Toolbar(self)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        self.toolbar.on_new = self._on_new
        self.toolbar.on_open = self._on_open
        self.toolbar.on_save = self._on_save
        self.toolbar.on_export = self._on_export
        self.toolbar.on_undo = self._on_undo
        self.toolbar.on_redo = self._on_redo
        
        # Main content area
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: Path panel
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        self.path_panel = PathPanel(left_frame)
        self.path_panel.pack(fill=tk.BOTH, expand=True)
        self.path_panel.on_path_changed = self._on_path_changed
        self.path_panel.on_waypoint_selected = self._on_waypoint_selected
        self.path_panel.on_project_modified = self._on_project_modified
        
        # Center: Field canvas
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.field_canvas = FieldCanvas(center_frame)
        self.field_canvas.pack(expand=True)
        self.field_canvas.on_waypoint_added = self._on_waypoint_added
        self.field_canvas.on_waypoint_selected = self._on_waypoint_selected
        self.field_canvas.on_waypoint_moved = self._on_waypoint_moved
        self.field_canvas.on_mouse_move = self._on_mouse_move
        
        # Right side: Waypoint and command panels
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        self.waypoint_panel = WaypointPanel(right_frame)
        self.waypoint_panel.pack(fill=tk.X, pady=(0, 5))
        self.waypoint_panel.on_waypoint_changed = self._on_waypoint_changed
        
        self.command_panel = CommandPanel(right_frame)
        self.command_panel.pack(fill=tk.BOTH, expand=True)
        self.command_panel.on_commands_changed = self._on_commands_changed
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
    
    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self._on_new())
        self.bind("<Control-o>", lambda e: self._on_open())
        self.bind("<Control-s>", lambda e: self._on_save())
        self.bind("<Control-Shift-S>", lambda e: self._on_save_as())
        self.bind("<Control-e>", lambda e: self._on_export())
        self.bind("<Control-z>", lambda e: self._on_undo())
        self.bind("<Control-y>", lambda e: self._on_redo())
        self.bind("<Delete>", lambda e: self._delete_selected())
    
    def _new_project(self, season: str = "pushback_2026") -> None:
        """Create a new project."""
        self.project = create_new_project(season)
        self.current_filepath = None
        self.modified = False
        
        # Load season commands
        self.season_loader.load_season(season)
        self.command_panel.set_commands(self.season_loader.commands)
        
        # Update UI
        self.path_panel.set_project(self.project)
        self._update_title()
        
        # Initialize undo
        self.undo_manager.clear()
        self._save_undo_state("New project")
    
    def _on_new(self) -> None:
        """Handle new project request."""
        if self.modified:
            result = ask_save_changes(self)
            if result is None:  # Cancel
                return
            if result:  # Save
                if not self._on_save():
                    return
        
        self._new_project()
    
    def _on_open(self) -> None:
        """Handle open project request."""
        if self.modified:
            result = ask_save_changes(self)
            if result is None:
                return
            if result:
                if not self._on_save():
                    return
        
        filepath = filedialog.askopenfilename(
            defaultextension=".shupaths",
            filetypes=[("Path Projects", "*.shupaths"), ("All Files", "*.*")],
            initialdir=os.path.join(self.base_path, "projects"),
            title="Open Project"
        )
        
        if filepath:
            project = load_project(filepath)
            if project:
                self.project = project
                self.current_filepath = filepath
                self.modified = False
                
                # Load season
                self.season_loader.load_season(project.season)
                self.command_panel.set_commands(self.season_loader.commands)
                
                # Update UI
                self.path_panel.set_project(self.project)
                self._update_title()
                
                # Reset undo
                self.undo_manager.clear()
                self._save_undo_state("Opened project")
            else:
                messagebox.showerror("Error", "Failed to open project file.")
    
    def _on_save(self) -> bool:
        """Handle save request. Returns True if saved."""
        if self.current_filepath:
            return self._save_to_file(self.current_filepath)
        else:
            return self._on_save_as()
    
    def _on_save_as(self) -> bool:
        """Handle save as request. Returns True if saved."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".shupaths",
            filetypes=[("Path Projects", "*.shupaths"), ("All Files", "*.*")],
            initialdir=os.path.join(self.base_path, "projects"),
            title="Save Project"
        )
        
        if filepath:
            return self._save_to_file(filepath)
        return False
    
    def _save_to_file(self, filepath: str) -> bool:
        """Save project to file. Returns True if successful."""
        if self.project and save_project(self.project, filepath):
            self.current_filepath = filepath
            self.modified = False
            self._update_title()
            self.status_bar.set_message(f"Saved to {os.path.basename(filepath)}")
            return True
        else:
            messagebox.showerror("Error", "Failed to save project.")
            return False
    
    def _on_export(self, clipboard: bool = False) -> None:
        """Handle export request."""
        path = self.path_panel.get_current_path()
        if path is None:
            messagebox.showwarning("No Path", "No path to export.")
            return
        
        code = export_path_to_cpp(path, self.season_loader.commands)
        
        if clipboard:
            copy_to_clipboard(code, self)
            self.status_bar.set_message("Code copied to clipboard!")
        else:
            ExportDialog(self, code, path.name)
    
    def _on_undo(self) -> None:
        """Handle undo request."""
        state = self.undo_manager.undo()
        if state and self.project:
            self._restore_state(state)
    
    def _on_redo(self) -> None:
        """Handle redo request."""
        state = self.undo_manager.redo()
        if state:
            self._restore_state(state)
    
    def _save_undo_state(self, description: str) -> None:
        """Save current state for undo."""
        if self.project:
            self.undo_manager.save_state(self.project.to_dict(), description)
    
    def _restore_state(self, state: dict) -> None:
        """Restore project from state dict."""
        from path_planner.core.models import Project
        self.project = Project.from_dict(state)
        self.path_panel.set_project(self.project)
        self._on_project_modified()
    
    def _update_undo_buttons(self) -> None:
        """Update undo/redo button states."""
        self.toolbar.set_undo_enabled(self.undo_manager.can_undo())
        self.toolbar.set_redo_enabled(self.undo_manager.can_redo())
    
    def _on_path_changed(self, path: Path) -> None:
        """Handle path change (from path panel)."""
        self.field_canvas.set_path(path)
        self.waypoint_panel.set_waypoint(None)
        self.command_panel.set_waypoint(None)
        self._update_waypoint_count()
    
    def _on_waypoint_added(self, x: float, y: float) -> None:
        """Handle new waypoint added (from canvas)."""
        path = self.path_panel.get_current_path()
        if path:
            index = path.add_waypoint(x, y)
            self.field_canvas.set_selected(index)
            self.path_panel.refresh_waypoint_list()
            self.path_panel.select_waypoint(index)
            self._select_waypoint(index)
            self._on_project_modified()
            self._save_undo_state("Add waypoint")
    
    def _on_waypoint_selected(self, index: Optional[int]) -> None:
        """Handle waypoint selection."""
        self._select_waypoint(index)
        self.field_canvas.set_selected(index)
        self.path_panel.select_waypoint(index)
    
    def _select_waypoint(self, index: Optional[int]) -> None:
        """Select a waypoint and update panels."""
        path = self.path_panel.get_current_path()
        if path and index is not None and 0 <= index < len(path.waypoints):
            wp = path.waypoints[index]
            self.waypoint_panel.set_waypoint(wp, index)
            self.command_panel.set_waypoint(wp)
        else:
            self.waypoint_panel.set_waypoint(None)
            self.command_panel.set_waypoint(None)
    
    def _on_waypoint_moved(self, index: int, x: float, y: float) -> None:
        """Handle waypoint drag complete."""
        self._on_project_modified()
        self._save_undo_state("Move waypoint")
    
    def _on_waypoint_changed(self) -> None:
        """Handle waypoint property change (from waypoint panel)."""
        self.field_canvas.redraw()
        self.path_panel.refresh_waypoint_list()
        self._on_project_modified()
        self._save_undo_state("Edit waypoint")
    
    def _on_commands_changed(self) -> None:
        """Handle commands change (from command panel)."""
        self.path_panel.refresh_waypoint_list()
        self._on_project_modified()
        self._save_undo_state("Edit commands")
    
    def _on_project_modified(self) -> None:
        """Handle any project modification."""
        self.modified = True
        self._update_title()
        self._update_waypoint_count()
    
    def _on_mouse_move(self, x: float, y: float) -> None:
        """Handle mouse move on canvas."""
        self.status_bar.set_coordinates(x, y)
    
    def _delete_selected(self) -> None:
        """Delete the selected waypoint."""
        index = self.field_canvas.selected_index
        path = self.path_panel.get_current_path()
        
        if index is not None and path:
            path.remove_waypoint(index)
            self.field_canvas.set_selected(None)
            self.field_canvas.redraw()
            self.path_panel.refresh_waypoint_list()
            self._select_waypoint(None)
            self._on_project_modified()
            self._save_undo_state("Delete waypoint")
    
    def _update_title(self) -> None:
        """Update window title."""
        title = "shulib Path Planner"
        if self.current_filepath:
            title += f" - {os.path.basename(self.current_filepath)}"
        if self.modified:
            title += " *"
        self.title(title)
    
    def _update_waypoint_count(self) -> None:
        """Update waypoint count in status bar."""
        path = self.path_panel.get_current_path()
        count = len(path.waypoints) if path else 0
        self.status_bar.set_waypoint_count(count)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        AboutDialog(self)
    
    def _on_close(self) -> None:
        """Handle window close."""
        if self.modified:
            result = ask_save_changes(self)
            if result is None:  # Cancel
                return
            if result:  # Save
                if not self._on_save():
                    return
        
        self.destroy()
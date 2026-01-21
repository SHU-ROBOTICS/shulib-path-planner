"""
Path panel for managing paths within a project.

Displays:
- Path selector dropdown
- Alliance/side selection
- Waypoint list
"""

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import Optional, Callable
from path_planner.core.models import Project, Path, Waypoint, Alliance, Side, MotionType


class PathPanel(ttk.Frame):
    """
    Panel for path management and waypoint list.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.project: Optional[Project] = None
        self.current_path_index: int = 0
        
        # Callbacks
        self.on_path_changed: Optional[Callable[[Path], None]] = None
        self.on_waypoint_selected: Optional[Callable[[int], None]] = None
        self.on_project_modified: Optional[Callable[[], None]] = None
        
        self._updating = False
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Path selector frame
        path_frame = ttk.LabelFrame(self, text="Path")
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        selector_frame = ttk.Frame(path_frame)
        selector_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.path_var = tk.StringVar()
        self.path_combo = ttk.Combobox(
            selector_frame, textvariable=self.path_var,
            state="readonly", width=20
        )
        self.path_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_combo.bind("<<ComboboxSelected>>", self._on_path_selected)
        
        self.add_path_btn = ttk.Button(selector_frame, text="+", width=3, command=self._add_path)
        self.add_path_btn.pack(side=tk.LEFT, padx=2)
        
        self.remove_path_btn = ttk.Button(selector_frame, text="−", width=3, command=self._remove_path)
        self.remove_path_btn.pack(side=tk.LEFT, padx=2)
        
        self.rename_btn = ttk.Button(selector_frame, text="Rename", command=self._rename_path)
        self.rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Alliance/Side frame
        settings_frame = ttk.Frame(path_frame)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Alliance
        ttk.Label(settings_frame, text="Alliance:").pack(side=tk.LEFT)
        
        self.alliance_var = tk.StringVar(value="red")
        self.red_rb = ttk.Radiobutton(
            settings_frame, text="Red", variable=self.alliance_var,
            value="red", command=self._on_alliance_change
        )
        self.red_rb.pack(side=tk.LEFT, padx=5)
        
        self.blue_rb = ttk.Radiobutton(
            settings_frame, text="Blue", variable=self.alliance_var,
            value="blue", command=self._on_alliance_change
        )
        self.blue_rb.pack(side=tk.LEFT, padx=5)
        
        # Side
        ttk.Label(settings_frame, text="Side:").pack(side=tk.LEFT, padx=(20, 0))
        
        self.side_var = tk.StringVar(value="left")
        self.left_rb = ttk.Radiobutton(
            settings_frame, text="Left", variable=self.side_var,
            value="left", command=self._on_side_change
        )
        self.left_rb.pack(side=tk.LEFT, padx=5)
        
        self.right_rb = ttk.Radiobutton(
            settings_frame, text="Right", variable=self.side_var,
            value="right", command=self._on_side_change
        )
        self.right_rb.pack(side=tk.LEFT, padx=5)
        
        self.full_rb = ttk.Radiobutton(
            settings_frame, text="Full", variable=self.side_var,
            value="full", command=self._on_side_change
        )
        self.full_rb.pack(side=tk.LEFT, padx=5)
        
        # Waypoint list frame
        waypoint_frame = ttk.LabelFrame(self, text="Waypoints")
        waypoint_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(waypoint_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.waypoint_listbox = tk.Listbox(
            list_frame, height=10, selectmode=tk.SINGLE,
            bg="#2a2a2a", fg="#ffffff", selectbackground="#0066cc"
        )
        self.waypoint_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.waypoint_listbox.bind("<<ListboxSelect>>", self._on_waypoint_list_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.waypoint_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.waypoint_listbox.config(yscrollcommand=scrollbar.set)
        
        # Waypoint control buttons
        wp_btn_frame = ttk.Frame(waypoint_frame)
        wp_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.delete_wp_btn = ttk.Button(wp_btn_frame, text="Delete", command=self._delete_waypoint)
        self.delete_wp_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_wp_btn = ttk.Button(wp_btn_frame, text="Clear All", command=self._clear_waypoints)
        self.clear_wp_btn.pack(side=tk.LEFT, padx=2)
    
    def set_project(self, project: Optional[Project]) -> None:
        """Set the current project."""
        self.project = project
        self.current_path_index = 0
        self._refresh_path_list()
        
        if project and project.paths:
            self._load_path(0)
    
    def get_current_path(self) -> Optional[Path]:
        """Get the currently selected path."""
        if self.project and 0 <= self.current_path_index < len(self.project.paths):
            return self.project.paths[self.current_path_index]
        return None
    
    def refresh_waypoint_list(self) -> None:
        """Refresh the waypoint listbox."""
        self._refresh_waypoint_list()
    
    def select_waypoint(self, index: Optional[int]) -> None:
        """Select a waypoint in the list."""
        self.waypoint_listbox.selection_clear(0, tk.END)
        if index is not None:
            self.waypoint_listbox.selection_set(index)
            self.waypoint_listbox.see(index)
    
    def _refresh_path_list(self) -> None:
        """Refresh the path dropdown."""
        if self.project is None:
            self.path_combo['values'] = []
            self.path_var.set("")
            return
        
        names = [p.name for p in self.project.paths]
        self.path_combo['values'] = names
        
        if names and self.current_path_index < len(names):
            self.path_var.set(names[self.current_path_index])
    
    def _load_path(self, index: int) -> None:
        """Load a path by index."""
        self._updating = True
        
        self.current_path_index = index
        path = self.get_current_path()
        
        if path:
            self.path_var.set(path.name)
            self.alliance_var.set(path.alliance.value)
            self.side_var.set(path.side.value)
        
        self._refresh_waypoint_list()
        
        self._updating = False
        
        if self.on_path_changed and path:
            self.on_path_changed(path)
    
    def _refresh_waypoint_list(self) -> None:
        """Refresh the waypoint listbox."""
        self.waypoint_listbox.delete(0, tk.END)
        
        path = self.get_current_path()
        if path is None:
            return
        
        for i, wp in enumerate(path.waypoints):
            is_start = (wp.motion_type == MotionType.START)
            prefix = "★" if is_start else "●"
            text = f"{prefix} {i + 1}: ({wp.x:.1f}, {wp.y:.1f})"
            
            if wp.commands_after:
                text += f" → {len(wp.commands_after)} cmd"
            
            self.waypoint_listbox.insert(tk.END, text)
    
    def _on_path_selected(self, event=None) -> None:
        """Handle path selection from dropdown."""
        if self._updating or self.project is None:
            return
        
        selected = self.path_combo.current()
        if selected >= 0:
            self._load_path(selected)
    
    def _on_alliance_change(self) -> None:
        """Handle alliance change."""
        if self._updating:
            return
        
        path = self.get_current_path()
        if path:
            path.alliance = Alliance(self.alliance_var.get())
            self._notify_modified()
    
    def _on_side_change(self) -> None:
        """Handle side change."""
        if self._updating:
            return
        
        path = self.get_current_path()
        if path:
            path.side = Side(self.side_var.get())
            self._notify_modified()
            
            # Refresh canvas to show restriction
            if self.on_path_changed:
                self.on_path_changed(path)
    
    def _on_waypoint_list_select(self, event=None) -> None:
        """Handle waypoint selection from list."""
        selection = self.waypoint_listbox.curselection()
        if selection and self.on_waypoint_selected:
            self.on_waypoint_selected(selection[0])
    
    def _add_path(self) -> None:
        """Add a new path."""
        if self.project is None:
            return
        
        name = simpledialog.askstring("New Path", "Enter path name:", initialvalue="New Path")
        if name:
            self.project.add_path(name)
            self._refresh_path_list()
            self._load_path(len(self.project.paths) - 1)
            self._notify_modified()
    
    def _remove_path(self) -> None:
        """Remove the current path."""
        if self.project is None or len(self.project.paths) <= 1:
            return  # Keep at least one path
        
        self.project.remove_path(self.current_path_index)
        self.current_path_index = min(self.current_path_index, len(self.project.paths) - 1)
        self._refresh_path_list()
        self._load_path(self.current_path_index)
        self._notify_modified()
    
    def _rename_path(self) -> None:
        """Rename the current path."""
        path = self.get_current_path()
        if path is None:
            return
        
        name = simpledialog.askstring("Rename Path", "Enter new name:", initialvalue=path.name)
        if name:
            path.name = name
            self._refresh_path_list()
            self._notify_modified()
    
    def _delete_waypoint(self) -> None:
        """Delete selected waypoint."""
        selection = self.waypoint_listbox.curselection()
        if not selection:
            return
        
        path = self.get_current_path()
        if path:
            path.remove_waypoint(selection[0])
            self._refresh_waypoint_list()
            self._notify_modified()
            
            if self.on_path_changed:
                self.on_path_changed(path)
    
    def _clear_waypoints(self) -> None:
        """Clear all waypoints."""
        path = self.get_current_path()
        if path:
            path.waypoints.clear()
            self._refresh_waypoint_list()
            self._notify_modified()
            
            if self.on_path_changed:
                self.on_path_changed(path)
    
    def _notify_modified(self) -> None:
        """Notify that project was modified."""
        if self.on_project_modified:
            self.on_project_modified()
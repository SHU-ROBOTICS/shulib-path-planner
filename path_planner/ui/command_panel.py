"""
Command panel for assigning mechanism commands to waypoints.

Displays:
- Commands assigned to current waypoint
- Quick command buttons grouped by category
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from path_planner.core.models import Waypoint
from path_planner.core.commands import Command


class CommandPanel(ttk.LabelFrame):
    """
    Panel for managing commands at a waypoint.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Commands", **kwargs)
        
        self.waypoint: Optional[Waypoint] = None
        self.commands: dict[str, Command] = {}
        
        # Callbacks
        self.on_commands_changed: Optional[Callable[[], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Assigned commands section
        assigned_frame = ttk.LabelFrame(self, text="After Arriving")
        assigned_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(assigned_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.command_listbox = tk.Listbox(
            list_frame, height=6, selectmode=tk.SINGLE,
            bg="#2a2a2a", fg="#ffffff", selectbackground="#0066cc"
        )
        self.command_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.command_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.command_listbox.config(yscrollcommand=scrollbar.set)
        
        # Control buttons
        btn_frame = ttk.Frame(assigned_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.move_up_btn = ttk.Button(btn_frame, text="▲", width=3, command=self._move_up)
        self.move_up_btn.pack(side=tk.LEFT, padx=2)
        
        self.move_down_btn = ttk.Button(btn_frame, text="▼", width=3, command=self._move_down)
        self.move_down_btn.pack(side=tk.LEFT, padx=2)
        
        self.remove_btn = ttk.Button(btn_frame, text="Remove", command=self._remove_command)
        self.remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear All", command=self._clear_commands)
        self.clear_btn.pack(side=tk.RIGHT, padx=2)
        
        # Quick commands section
        quick_frame = ttk.LabelFrame(self, text="Add Command")
        quick_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook for command categories
        self.category_notebook = ttk.Notebook(quick_frame)
        self.category_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Will be populated when commands are set
        self.category_frames: dict[str, ttk.Frame] = {}
    
    def set_commands(self, commands: dict[str, Command]) -> None:
        """
        Set available commands (from season loader).
        
        Args:
            commands: Dict of command_id -> Command
        """
        self.commands = commands
        self._populate_quick_commands()
    
    def _populate_quick_commands(self) -> None:
        """Populate the quick command buttons by category."""
        # Clear existing tabs
        for tab in self.category_notebook.tabs():
            self.category_notebook.forget(tab)
        self.category_frames.clear()
        
        # Group commands by category
        by_category: dict[str, list[Command]] = {}
        for cmd in self.commands.values():
            if cmd.category not in by_category:
                by_category[cmd.category] = []
            by_category[cmd.category].append(cmd)
        
        # Create tab for each category
        for category, cmds in sorted(by_category.items()):
            frame = ttk.Frame(self.category_notebook)
            self.category_notebook.add(frame, text=category)
            self.category_frames[category] = frame
            
            # Create buttons in a grid
            for i, cmd in enumerate(cmds):
                row = i // 2
                col = i % 2
                
                btn = ttk.Button(
                    frame, text=cmd.name,
                    command=lambda c=cmd: self._add_command(c.id)
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            # Configure columns to expand
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
    
    def set_waypoint(self, waypoint: Optional[Waypoint]) -> None:
        """Set the current waypoint."""
        self.waypoint = waypoint
        self._refresh_list()
        self._update_button_states()
    
    def _refresh_list(self) -> None:
        """Refresh the command listbox."""
        self.command_listbox.delete(0, tk.END)
        
        if self.waypoint is None:
            return
        
        for i, cmd_id in enumerate(self.waypoint.commands_after):
            cmd = self.commands.get(cmd_id)
            name = cmd.name if cmd else cmd_id
            self.command_listbox.insert(tk.END, f"{i + 1}. {name}")
    
    def _update_button_states(self) -> None:
        """Update button enabled states."""
        has_waypoint = self.waypoint is not None
        has_selection = len(self.command_listbox.curselection()) > 0
        has_commands = self.waypoint is not None and len(self.waypoint.commands_after) > 0
        
        state = "normal" if has_waypoint and has_selection else "disabled"
        self.move_up_btn.config(state=state)
        self.move_down_btn.config(state=state)
        self.remove_btn.config(state=state)
        
        self.clear_btn.config(state="normal" if has_commands else "disabled")
        
        # Enable/disable quick command buttons
        for frame in self.category_frames.values():
            for child in frame.winfo_children():
                child.config(state="normal" if has_waypoint else "disabled")
    
    def _add_command(self, cmd_id: str) -> None:
        """Add a command to the waypoint."""
        if self.waypoint is None:
            return
        
        self.waypoint.commands_after.append(cmd_id)
        self._refresh_list()
        self._notify_change()
    
    def _remove_command(self) -> None:
        """Remove the selected command."""
        if self.waypoint is None:
            return
        
        selection = self.command_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.waypoint.commands_after):
            self.waypoint.commands_after.pop(index)
            self._refresh_list()
            self._notify_change()
    
    def _clear_commands(self) -> None:
        """Clear all commands from waypoint."""
        if self.waypoint is None:
            return
        
        self.waypoint.commands_after.clear()
        self._refresh_list()
        self._notify_change()
    
    def _move_up(self) -> None:
        """Move selected command up."""
        if self.waypoint is None:
            return
        
        selection = self.command_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index > 0:
            cmds = self.waypoint.commands_after
            cmds[index], cmds[index - 1] = cmds[index - 1], cmds[index]
            self._refresh_list()
            self.command_listbox.selection_set(index - 1)
            self._notify_change()
    
    def _move_down(self) -> None:
        """Move selected command down."""
        if self.waypoint is None:
            return
        
        selection = self.command_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        cmds = self.waypoint.commands_after
        if index < len(cmds) - 1:
            cmds[index], cmds[index + 1] = cmds[index + 1], cmds[index]
            self._refresh_list()
            self.command_listbox.selection_set(index + 1)
            self._notify_change()
    
    def _notify_change(self) -> None:
        """Notify that commands changed."""
        self._update_button_states()
        if self.on_commands_changed:
            self.on_commands_changed()
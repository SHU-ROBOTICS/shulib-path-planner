"""
Toolbar and status bar components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class StatusBar(ttk.Frame):
    """
    Status bar at the bottom of the window.
    
    Shows:
    - Mouse coordinates on field
    - Current mode/state
    - Messages
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure border
        self.configure(relief=tk.SUNKEN)
        
        # Left side: coordinates
        self.coord_label = ttk.Label(self, text="Mouse: (0.0\", 0.0\")", width=25)
        self.coord_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # Center: mode/state
        self.mode_label = ttk.Label(self, text="Ready")
        self.mode_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # Right side: message
        self.message_label = ttk.Label(self, text="")
        self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Far right: waypoint count
        self.count_label = ttk.Label(self, text="Waypoints: 0")
        self.count_label.pack(side=tk.RIGHT, padx=5)
    
    def set_coordinates(self, x: float, y: float) -> None:
        """Update coordinate display."""
        self.coord_label.config(text=f"Mouse: ({x:.1f}\", {y:.1f}\")")
    
    def set_mode(self, mode: str) -> None:
        """Update mode display."""
        self.mode_label.config(text=mode)
    
    def set_message(self, message: str) -> None:
        """Update message display."""
        self.message_label.config(text=message)
    
    def set_waypoint_count(self, count: int) -> None:
        """Update waypoint count."""
        self.count_label.config(text=f"Waypoints: {count}")
    
    def clear_message(self) -> None:
        """Clear the message."""
        self.message_label.config(text="")


class Toolbar(ttk.Frame):
    """
    Main toolbar with action buttons.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Callbacks
        self.on_new: Optional[callable] = None
        self.on_open: Optional[callable] = None
        self.on_save: Optional[callable] = None
        self.on_export: Optional[callable] = None
        self.on_undo: Optional[callable] = None
        self.on_redo: Optional[callable] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create toolbar buttons."""
        # File operations
        self.new_btn = ttk.Button(self, text="New", command=self._on_new)
        self.new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.open_btn = ttk.Button(self, text="Open", command=self._on_open)
        self.open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.save_btn = ttk.Button(self, text="Save", command=self._on_save)
        self.save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # Edit operations
        self.undo_btn = ttk.Button(self, text="Undo", command=self._on_undo)
        self.undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.redo_btn = ttk.Button(self, text="Redo", command=self._on_redo)
        self.redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # Export
        self.export_btn = ttk.Button(self, text="Export C++", command=self._on_export)
        self.export_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.copy_btn = ttk.Button(self, text="Copy to Clipboard", command=self._on_copy)
        self.copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def set_undo_enabled(self, enabled: bool) -> None:
        """Enable/disable undo button."""
        self.undo_btn.config(state="normal" if enabled else "disabled")
    
    def set_redo_enabled(self, enabled: bool) -> None:
        """Enable/disable redo button."""
        self.redo_btn.config(state="normal" if enabled else "disabled")
    
    def _on_new(self) -> None:
        if self.on_new:
            self.on_new()
    
    def _on_open(self) -> None:
        if self.on_open:
            self.on_open()
    
    def _on_save(self) -> None:
        if self.on_save:
            self.on_save()
    
    def _on_export(self) -> None:
        if self.on_export:
            self.on_export()
    
    def _on_copy(self) -> None:
        # This will be handled by export callback with clipboard flag
        if self.on_export:
            self.on_export(clipboard=True)
    
    def _on_undo(self) -> None:
        if self.on_undo:
            self.on_undo()
    
    def _on_redo(self) -> None:
        if self.on_redo:
            self.on_redo()
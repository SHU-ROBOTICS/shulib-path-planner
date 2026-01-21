"""
Waypoint properties panel.

Displays and edits properties of the selected waypoint:
- Position (X, Y)
- Heading (auto/manual)
- Motion type
- Motion parameters (reverse, intaking, conveyor)
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from path_planner.core.models import Waypoint, MotionType, HeadingMode


class WaypointPanel(ttk.LabelFrame):
    """
    Panel for editing waypoint properties.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Selected Waypoint", **kwargs)
        
        self.waypoint: Optional[Waypoint] = None
        self.waypoint_index: Optional[int] = None
        
        # Callback when waypoint is modified
        self.on_waypoint_changed: Optional[Callable[[], None]] = None
        
        # Prevent recursive updates
        self._updating = False
        
        self._create_widgets()
        self._set_enabled(False)
    
    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Position frame
        pos_frame = ttk.Frame(self)
        pos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pos_frame, text="Position:").pack(side=tk.LEFT)
        
        ttk.Label(pos_frame, text="X").pack(side=tk.LEFT, padx=(10, 2))
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(pos_frame, textvariable=self.x_var, width=8)
        self.x_entry.pack(side=tk.LEFT)
        self.x_entry.bind("<Return>", self._on_position_change)
        self.x_entry.bind("<FocusOut>", self._on_position_change)
        
        ttk.Label(pos_frame, text="Y").pack(side=tk.LEFT, padx=(10, 2))
        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(pos_frame, textvariable=self.y_var, width=8)
        self.y_entry.pack(side=tk.LEFT)
        self.y_entry.bind("<Return>", self._on_position_change)
        self.y_entry.bind("<FocusOut>", self._on_position_change)
        
        # Heading frame
        heading_frame = ttk.Frame(self)
        heading_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(heading_frame, text="Heading:").pack(side=tk.LEFT)
        
        self.heading_mode_var = tk.StringVar(value="auto")
        self.heading_auto_rb = ttk.Radiobutton(
            heading_frame, text="Auto", variable=self.heading_mode_var,
            value="auto", command=self._on_heading_mode_change
        )
        self.heading_auto_rb.pack(side=tk.LEFT, padx=(10, 5))
        
        self.heading_manual_rb = ttk.Radiobutton(
            heading_frame, text="Manual", variable=self.heading_mode_var,
            value="manual", command=self._on_heading_mode_change
        )
        self.heading_manual_rb.pack(side=tk.LEFT, padx=5)
        
        self.heading_var = tk.StringVar()
        self.heading_entry = ttk.Entry(heading_frame, textvariable=self.heading_var, width=8)
        self.heading_entry.pack(side=tk.LEFT, padx=5)
        self.heading_entry.bind("<Return>", self._on_heading_change)
        self.heading_entry.bind("<FocusOut>", self._on_heading_change)
        
        ttk.Label(heading_frame, text="°").pack(side=tk.LEFT)
        
        # Motion type frame
        motion_frame = ttk.Frame(self)
        motion_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(motion_frame, text="Motion:").pack(side=tk.LEFT)
        
        self.motion_var = tk.StringVar()
        self.motion_combo = ttk.Combobox(
            motion_frame, textvariable=self.motion_var,
            values=["moveToPose", "moveVertical", "rotateTo", "start"],
            state="readonly", width=12
        )
        self.motion_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.motion_combo.bind("<<ComboboxSelected>>", self._on_motion_change)
        
        # Motion parameters frame
        params_frame = ttk.Frame(self)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.reverse_var = tk.BooleanVar()
        self.reverse_cb = ttk.Checkbutton(
            params_frame, text="Reverse", variable=self.reverse_var,
            command=self._on_param_change
        )
        self.reverse_cb.pack(side=tk.LEFT, padx=5)
        
        self.intaking_var = tk.BooleanVar()
        self.intaking_cb = ttk.Checkbutton(
            params_frame, text="Intake", variable=self.intaking_var,
            command=self._on_param_change
        )
        self.intaking_cb.pack(side=tk.LEFT, padx=5)
        
        self.conveyor_var = tk.BooleanVar()
        self.conveyor_cb = ttk.Checkbutton(
            params_frame, text="Conveyor", variable=self.conveyor_var,
            command=self._on_param_change
        )
        self.conveyor_cb.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = ttk.Label(self, text="Click a waypoint to edit", foreground="gray")
        self.info_label.pack(pady=10)
    
    def set_waypoint(self, waypoint: Optional[Waypoint], index: Optional[int] = None) -> None:
        """
        Set the waypoint to display/edit.
        
        Args:
            waypoint: The waypoint, or None to clear
            index: The waypoint index (for display)
        """
        self.waypoint = waypoint
        self.waypoint_index = index
        
        self._updating = True
        
        if waypoint is None:
            self._set_enabled(False)
            self.info_label.config(text="Click a waypoint to edit")
            self._clear_fields()
        else:
            self._set_enabled(True)
            self.info_label.config(text=f"Waypoint {index + 1}" if index is not None else "")
            self._load_waypoint()
        
        self._updating = False
    
    def _load_waypoint(self) -> None:
        """Load waypoint data into fields."""
        if self.waypoint is None:
            return
        
        wp = self.waypoint
        
        self.x_var.set(f"{wp.x:.1f}")
        self.y_var.set(f"{wp.y:.1f}")
        
        self.heading_mode_var.set(wp.heading_mode.value)
        if wp.heading is not None:
            self.heading_var.set(f"{wp.heading:.1f}")
        else:
            self.heading_var.set("")
        
        self.heading_entry.config(state="normal" if wp.heading_mode == HeadingMode.MANUAL else "disabled")
        
        self.motion_var.set(wp.motion_type.value)
        
        self.reverse_var.set(wp.reverse)
        self.intaking_var.set(wp.intaking)
        self.conveyor_var.set(wp.conveyor)
        
        # Disable motion type for start waypoint
        is_start = (wp.motion_type == MotionType.START)
        self.motion_combo.config(state="disabled" if is_start else "readonly")
    
    def _clear_fields(self) -> None:
        """Clear all input fields."""
        self.x_var.set("")
        self.y_var.set("")
        self.heading_var.set("")
        self.heading_mode_var.set("auto")
        self.motion_var.set("")
        self.reverse_var.set(False)
        self.intaking_var.set(False)
        self.conveyor_var.set(False)
    
    def _set_enabled(self, enabled: bool) -> None:
        """Enable or disable all inputs."""
        state = "normal" if enabled else "disabled"
        
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)
        self.heading_auto_rb.config(state=state)
        self.heading_manual_rb.config(state=state)
        self.heading_entry.config(state=state if enabled and self.heading_mode_var.get() == "manual" else "disabled")
        self.motion_combo.config(state="readonly" if enabled else "disabled")
        self.reverse_cb.config(state=state)
        self.intaking_cb.config(state=state)
        self.conveyor_cb.config(state=state)
    
    def _on_position_change(self, event=None) -> None:
        """Handle position change."""
        if self._updating or self.waypoint is None:
            return
        
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            self.waypoint.x = x
            self.waypoint.y = y
            self._notify_change()
        except ValueError:
            pass  # Invalid input, ignore
    
    def _on_heading_mode_change(self) -> None:
        """Handle heading mode change."""
        if self._updating or self.waypoint is None:
            return
        
        mode = HeadingMode(self.heading_mode_var.get())
        self.waypoint.heading_mode = mode
        
        if mode == HeadingMode.AUTO:
            self.waypoint.heading = None
            self.heading_entry.config(state="disabled")
            self.heading_var.set("")
        else:
            self.heading_entry.config(state="normal")
            if self.waypoint.heading is None:
                self.waypoint.heading = 0.0
                self.heading_var.set("0.0")
        
        self._notify_change()
    
    def _on_heading_change(self, event=None) -> None:
        """Handle heading value change."""
        if self._updating or self.waypoint is None:
            return
        
        try:
            heading = float(self.heading_var.get())
            self.waypoint.heading = heading
            self._notify_change()
        except ValueError:
            pass
    
    def _on_motion_change(self, event=None) -> None:
        """Handle motion type change."""
        if self._updating or self.waypoint is None:
            return
        
        try:
            motion = MotionType(self.motion_var.get())
            self.waypoint.motion_type = motion
            self._notify_change()
        except ValueError:
            pass
    
    def _on_param_change(self) -> None:
        """Handle parameter checkbox change."""
        if self._updating or self.waypoint is None:
            return
        
        self.waypoint.reverse = self.reverse_var.get()
        self.waypoint.intaking = self.intaking_var.get()
        self.waypoint.conveyor = self.conveyor_var.get()
        self._notify_change()
    
    def _notify_change(self) -> None:
        """Notify that waypoint was changed."""
        if self.on_waypoint_changed:
            self.on_waypoint_changed()
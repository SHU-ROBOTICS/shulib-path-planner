"""
Field canvas - Visual representation of the VEX field.

Handles:
- Drawing the field grid
- Drawing waypoints and paths
- Mouse interaction for adding/selecting/dragging waypoints
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from path_planner.core.coordinates import CoordinateSystem, FIELD_SIZE_INCHES, TILE_SIZE_INCHES, FIELD_HALF_SIZE
from path_planner.core.models import Path, Waypoint, MotionType, Side


# Visual constants
CANVAS_SIZE = 600
WAYPOINT_RADIUS = 8
START_WAYPOINT_RADIUS = 10
SELECTED_RADIUS = 12
HIT_RADIUS = 15  # For click detection

# Colors
COLOR_GRID = "#444444"
COLOR_GRID_CENTER = "#666666"
COLOR_AUTON_LINE = "#FFFF00"
COLOR_RESTRICTED = "#331111"
COLOR_PATH_LINE = "#00AAFF"
COLOR_WAYPOINT = "#00FF00"
COLOR_WAYPOINT_START = "#FFD700"
COLOR_WAYPOINT_SELECTED = "#FF00FF"
COLOR_HEADING_ARROW = "#FFFFFF"


class FieldCanvas(ttk.Frame):
    """
    Canvas widget displaying the VEX field.
    
    Supports:
    - Click to add waypoints
    - Click to select waypoints
    - Drag to move waypoints
    - Visual path display
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.coords = CoordinateSystem(CANVAS_SIZE)
        self.path: Optional[Path] = None
        self.selected_index: Optional[int] = None
        
        # Callbacks
        self.on_waypoint_added: Optional[Callable[[float, float], None]] = None
        self.on_waypoint_selected: Optional[Callable[[int], None]] = None
        self.on_waypoint_moved: Optional[Callable[[int, float, float], None]] = None
        self.on_mouse_move: Optional[Callable[[float, float], None]] = None
        
        # Drag state
        self._dragging = False
        self._drag_index: Optional[int] = None
        
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="#1a1a1a",
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Bind events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-3>", self._on_right_click)
        
        # Initial draw
        self._draw_field()
    
    def set_path(self, path: Optional[Path]) -> None:
        """Set the current path to display."""
        self.path = path
        self.selected_index = None
        self.redraw()
    
    def set_selected(self, index: Optional[int]) -> None:
        """Set the selected waypoint index."""
        self.selected_index = index
        self.redraw()
    
    def redraw(self) -> None:
        """Redraw the entire canvas."""
        self.canvas.delete("all")
        self._draw_field()
        self._draw_restricted_zone()
        self._draw_path()
        self._draw_waypoints()
    
    def _draw_field(self) -> None:
        """Draw the field grid."""
        # Draw tiles (6x6 grid)
        tile_pixels = CANVAS_SIZE / 6
        
        for i in range(7):
            x = i * tile_pixels
            color = COLOR_GRID_CENTER if i == 3 else COLOR_GRID
            width = 2 if i == 3 else 1
            self.canvas.create_line(x, 0, x, CANVAS_SIZE, fill=color, width=width)
            self.canvas.create_line(0, x, CANVAS_SIZE, x, fill=color, width=width)
        
        # Draw autonomous line (horizontal at y=0, which is center)
        center_y = CANVAS_SIZE / 2
        self.canvas.create_line(
            0, center_y, CANVAS_SIZE, center_y,
            fill=COLOR_AUTON_LINE, width=2, dash=(10, 5)
        )
        
        # Draw field border
        self.canvas.create_rectangle(
            1, 1, CANVAS_SIZE - 1, CANVAS_SIZE - 1,
            outline="#666666", width=2
        )
    
    def _draw_restricted_zone(self) -> None:
        """Draw shading for restricted side based on path settings."""
        if self.path is None:
            return
        
        if self.path.side == Side.LEFT:
            # Shade right side (x > 0)
            x_start, _ = self.coords.field_to_canvas(0, 0)
            self.canvas.create_rectangle(
                x_start, 0, CANVAS_SIZE, CANVAS_SIZE,
                fill=COLOR_RESTRICTED, stipple="gray25", outline=""
            )
        elif self.path.side == Side.RIGHT:
            # Shade left side (x < 0)
            x_end, _ = self.coords.field_to_canvas(0, 0)
            self.canvas.create_rectangle(
                0, 0, x_end, CANVAS_SIZE,
                fill=COLOR_RESTRICTED, stipple="gray25", outline=""
            )
        # Side.FULL = no restriction
    
    def _draw_path(self) -> None:
        """Draw path lines between waypoints."""
        if self.path is None or len(self.path.waypoints) < 2:
            return
        
        waypoints = self.path.waypoints
        
        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]
            
            x1, y1 = self.coords.field_to_canvas(wp1.x, wp1.y)
            x2, y2 = self.coords.field_to_canvas(wp2.x, wp2.y)
            
            # Draw line
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=COLOR_PATH_LINE, width=2, arrow=tk.LAST
            )
    
    def _draw_waypoints(self) -> None:
        """Draw all waypoints."""
        if self.path is None:
            return
        
        for i, wp in enumerate(self.path.waypoints):
            self._draw_waypoint(wp, i)
    
    def _draw_waypoint(self, wp: Waypoint, index: int) -> None:
        """Draw a single waypoint."""
        x, y = self.coords.field_to_canvas(wp.x, wp.y)
        
        is_start = (wp.motion_type == MotionType.START)
        is_selected = (index == self.selected_index)
        
        # Determine radius and color
        if is_selected:
            radius = SELECTED_RADIUS
            color = COLOR_WAYPOINT_SELECTED
        elif is_start:
            radius = START_WAYPOINT_RADIUS
            color = COLOR_WAYPOINT_START
        else:
            radius = WAYPOINT_RADIUS
            color = COLOR_WAYPOINT
        
        # Draw circle
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline="#FFFFFF", width=2
        )
        
        # Draw index number
        self.canvas.create_text(
            x, y,
            text=str(index + 1),
            fill="#000000" if is_start else "#FFFFFF",
            font=("Arial", 9, "bold")
        )
        
        # Draw heading arrow for selected waypoint
        if is_selected and wp.heading is not None:
            self._draw_heading_arrow(x, y, wp.heading, radius + 5)
    
    def _draw_heading_arrow(self, x: float, y: float, heading: float, length: float) -> None:
        """Draw an arrow indicating heading direction."""
        import math
        # Convert heading to canvas angle (0° = up = -90° in canvas coords)
        angle_rad = math.radians(90 - heading)
        
        end_x = x + length * math.cos(angle_rad)
        end_y = y - length * math.sin(angle_rad)
        
        self.canvas.create_line(
            x, y, end_x, end_y,
            fill=COLOR_HEADING_ARROW, width=2, arrow=tk.LAST
        )
    
    def _find_waypoint_at(self, canvas_x: float, canvas_y: float) -> Optional[int]:
        """Find waypoint index at canvas position, or None."""
        if self.path is None:
            return None
        
        for i, wp in enumerate(self.path.waypoints):
            wx, wy = self.coords.field_to_canvas(wp.x, wp.y)
            dist = ((canvas_x - wx)**2 + (canvas_y - wy)**2)**0.5
            if dist <= HIT_RADIUS:
                return i
        
        return None
    
    def _on_click(self, event) -> None:
        """Handle left click."""
        # Check if clicking on existing waypoint
        index = self._find_waypoint_at(event.x, event.y)
        
        if index is not None:
            # Select and start drag
            self.selected_index = index
            self._dragging = True
            self._drag_index = index
            
            if self.on_waypoint_selected:
                self.on_waypoint_selected(index)
            
            self.redraw()
        else:
            # Add new waypoint
            field_x, field_y = self.coords.canvas_to_field(event.x, event.y)
            
            # Check if position is valid for current side
            if self.path and not self.path.is_valid_position(field_x, field_y):
                return  # Don't add in restricted zone
            
            if self.on_waypoint_added:
                self.on_waypoint_added(field_x, field_y)
    
    def _on_drag(self, event) -> None:
        """Handle drag motion."""
        if not self._dragging or self._drag_index is None:
            return
        
        field_x, field_y = self.coords.canvas_to_field(event.x, event.y)
        
        # Clamp to field bounds
        field_x = max(-FIELD_HALF_SIZE, min(FIELD_HALF_SIZE, field_x))
        field_y = max(-FIELD_HALF_SIZE, min(FIELD_HALF_SIZE, field_y))
        
        # Check side restriction
        if self.path and not self.path.is_valid_position(field_x, field_y):
            return
        
        # Update waypoint position
        if self.path and 0 <= self._drag_index < len(self.path.waypoints):
            self.path.waypoints[self._drag_index].x = field_x
            self.path.waypoints[self._drag_index].y = field_y
            self.redraw()
    
    def _on_release(self, event) -> None:
        """Handle mouse button release."""
        if self._dragging and self._drag_index is not None:
            field_x, field_y = self.coords.canvas_to_field(event.x, event.y)
            field_x = max(-FIELD_HALF_SIZE, min(FIELD_HALF_SIZE, field_x))
            field_y = max(-FIELD_HALF_SIZE, min(FIELD_HALF_SIZE, field_y))
            
            if self.on_waypoint_moved:
                self.on_waypoint_moved(self._drag_index, field_x, field_y)
        
        self._dragging = False
        self._drag_index = None
    
    def _on_mouse_move(self, event) -> None:
        """Handle mouse movement for coordinate display."""
        field_x, field_y = self.coords.canvas_to_field(event.x, event.y)
        
        if self.on_mouse_move:
            self.on_mouse_move(field_x, field_y)
    
    def _on_right_click(self, event) -> None:
        """Handle right click (delete waypoint)."""
        index = self._find_waypoint_at(event.x, event.y)
        
        if index is not None and self.path:
            self.path.remove_waypoint(index)
            if self.selected_index == index:
                self.selected_index = None
            elif self.selected_index is not None and self.selected_index > index:
                self.selected_index -= 1
            self.redraw()
            
            if self.on_waypoint_selected:
                self.on_waypoint_selected(self.selected_index)
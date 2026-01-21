"""
Coordinate system conversions.

Field coordinates (shulib):
- Origin at center of field (0, 0)
- X: -72 to +72 inches (positive = right)
- Y: -72 to +72 inches (positive = forward)
- Heading: 0° = forward (+Y), clockwise positive

Canvas coordinates (tkinter):
- Origin at top-left (0, 0)
- X: 0 to canvas_size pixels (positive = right)
- Y: 0 to canvas_size pixels (positive = DOWN)
"""

import math

# Field constants
FIELD_SIZE_INCHES = 144.0  # 12 feet
FIELD_HALF_SIZE = 72.0     # Center to edge
TILE_SIZE_INCHES = 24.0    # Each tile is 2 feet
TILES_PER_SIDE = 6


class CoordinateSystem:
    """Handles conversions between field inches and canvas pixels."""
    
    def __init__(self, canvas_size: int = 600):
        """
        Initialize coordinate system.
        
        Args:
            canvas_size: Size of the square canvas in pixels
        """
        self.canvas_size = canvas_size
        self.scale = canvas_size / FIELD_SIZE_INCHES  # pixels per inch
    
    def field_to_canvas(self, field_x: float, field_y: float) -> tuple[float, float]:
        """
        Convert field coordinates (inches) to canvas coordinates (pixels).
        
        Args:
            field_x: X in inches (-72 to +72)
            field_y: Y in inches (-72 to +72)
        
        Returns:
            (canvas_x, canvas_y) in pixels
        """
        canvas_x = (field_x + FIELD_HALF_SIZE) * self.scale
        canvas_y = (FIELD_HALF_SIZE - field_y) * self.scale  # Flip Y
        return (canvas_x, canvas_y)
    
    def canvas_to_field(self, canvas_x: float, canvas_y: float) -> tuple[float, float]:
        """
        Convert canvas coordinates (pixels) to field coordinates (inches).
        
        Args:
            canvas_x: X in pixels
            canvas_y: Y in pixels
        
        Returns:
            (field_x, field_y) in inches
        """
        field_x = (canvas_x / self.scale) - FIELD_HALF_SIZE
        field_y = FIELD_HALF_SIZE - (canvas_y / self.scale)  # Flip Y back
        return (field_x, field_y)


def calculate_heading(from_x: float, from_y: float, to_x: float, to_y: float) -> float:
    """
    Calculate heading angle from one point to another.
    
    Uses shulib convention:
    - 0° = forward (+Y)
    - 90° = right (+X)
    - Clockwise positive
    
    Returns:
        Heading in degrees (0 to 360)
    """
    dx = to_x - from_x
    dy = to_y - from_y
    angle = math.degrees(math.atan2(dx, dy))
    
    if angle < 0:
        angle += 360
    
    return angle


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate distance between two points in inches."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
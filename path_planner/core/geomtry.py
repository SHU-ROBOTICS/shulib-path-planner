"""
Geometry utilities for path planning.

Includes Bezier curve calculations and path decomposition.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class Point:
    """A simple 2D point."""
    x: float
    y: float
    
    def distance_to(self, other: "Point") -> float:
        """Calculate distance to another point."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> "Point":
        return self.__mul__(scalar)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t


def lerp_point(p1: Point, p2: Point, t: float) -> Point:
    """Linear interpolation between two points."""
    return Point(lerp(p1.x, p2.x, t), lerp(p1.y, p2.y, t))


def quadratic_bezier(p0: Point, p1: Point, p2: Point, t: float) -> Point:
    """
    Calculate point on a quadratic Bezier curve.
    
    Args:
        p0: Start point
        p1: Control point
        p2: End point
        t: Parameter (0 to 1)
    
    Returns:
        Point on the curve
    """
    # B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
    one_minus_t = 1 - t
    return (one_minus_t * one_minus_t * p0 + 
            2 * one_minus_t * t * p1 + 
            t * t * p2)


def cubic_bezier(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    """
    Calculate point on a cubic Bezier curve.
    
    Args:
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        t: Parameter (0 to 1)
    
    Returns:
        Point on the curve
    """
    # B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
    one_minus_t = 1 - t
    return (one_minus_t**3 * p0 + 
            3 * one_minus_t**2 * t * p1 + 
            3 * one_minus_t * t**2 * p2 + 
            t**3 * p3)


def decompose_quadratic_bezier(
    p0: Point, 
    p1: Point, 
    p2: Point, 
    num_segments: int = 5
) -> list[Point]:
    """
    Decompose a quadratic Bezier curve into line segments.
    
    Args:
        p0: Start point
        p1: Control point
        p2: End point
        num_segments: Number of segments to create
    
    Returns:
        List of points (including start and end)
    """
    points = []
    for i in range(num_segments + 1):
        t = i / num_segments
        points.append(quadratic_bezier(p0, p1, p2, t))
    return points


def decompose_cubic_bezier(
    p0: Point, 
    p1: Point, 
    p2: Point, 
    p3: Point,
    num_segments: int = 5
) -> list[Point]:
    """
    Decompose a cubic Bezier curve into line segments.
    
    Args:
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        num_segments: Number of segments to create
    
    Returns:
        List of points (including start and end)
    """
    points = []
    for i in range(num_segments + 1):
        t = i / num_segments
        points.append(cubic_bezier(p0, p1, p2, p3, t))
    return points


def estimate_curve_length(points: list[Point]) -> float:
    """Estimate the length of a path through points."""
    if len(points) < 2:
        return 0.0
    
    total = 0.0
    for i in range(len(points) - 1):
        total += points[i].distance_to(points[i + 1])
    return total


def adaptive_decompose_quadratic(
    p0: Point,
    p1: Point,
    p2: Point,
    max_segment_length: float = 6.0,
    min_segments: int = 3,
    max_segments: int = 20
) -> list[Point]:
    """
    Decompose a quadratic Bezier with adaptive segment count.
    
    Creates more segments for longer/curvier paths.
    
    Args:
        p0: Start point
        p1: Control point
        p2: End point
        max_segment_length: Target max length per segment (inches)
        min_segments: Minimum number of segments
        max_segments: Maximum number of segments
    
    Returns:
        List of points
    """
    # Estimate curve length using control polygon
    rough_length = p0.distance_to(p1) + p1.distance_to(p2)
    
    # Calculate number of segments
    num_segments = int(rough_length / max_segment_length)
    num_segments = max(min_segments, min(max_segments, num_segments))
    
    return decompose_quadratic_bezier(p0, p1, p2, num_segments)


def point_to_line_distance(point: Point, line_start: Point, line_end: Point) -> float:
    """
    Calculate perpendicular distance from a point to a line segment.
    
    Args:
        point: The point
        line_start: Start of line segment
        line_end: End of line segment
    
    Returns:
        Distance in same units as input
    """
    # Vector from line_start to line_end
    line_vec = line_end - line_start
    # Vector from line_start to point
    point_vec = point - line_start
    
    line_len_sq = line_vec.x**2 + line_vec.y**2
    
    if line_len_sq == 0:
        # Line is a point
        return point.distance_to(line_start)
    
    # Project point onto line
    t = max(0, min(1, (point_vec.x * line_vec.x + point_vec.y * line_vec.y) / line_len_sq))
    
    projection = Point(line_start.x + t * line_vec.x, line_start.y + t * line_vec.y)
    return point.distance_to(projection)


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 range."""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle


def angle_difference(from_angle: float, to_angle: float) -> float:
    """
    Calculate the shortest angular difference.
    
    Returns value in range -180 to 180.
    """
    diff = normalize_angle(to_angle) - normalize_angle(from_angle)
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return diff
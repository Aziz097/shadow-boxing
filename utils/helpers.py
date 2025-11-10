"""
Utility Helper Functions
"""
import cv2
import numpy as np
from typing import Tuple, List
import math


def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def calculate_angle(p1, p2, p3) -> float:
    """
    Calculate angle between three points (p1-p2-p3).
    Returns angle in degrees.
    """
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])
    
    dot = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    
    cos_angle = dot / (norm_v1 * norm_v2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))


def draw_text(frame: np.ndarray, text: str, position: Tuple[int, int],
              font_scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255),
              thickness: int = 2, outline: bool = True) -> None:
    """
    Draw text with optional outline for better visibility.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    if outline:
        # Draw outline
        cv2.putText(frame, text, position, font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    
    # Draw text
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)


def draw_health_bar(frame: np.ndarray, position: Tuple[int, int], 
                   current_health: float, max_health: float,
                   width: int = 300, height: int = 30,
                   color_full: Tuple[int, int, int] = (0, 255, 0),
                   color_low: Tuple[int, int, int] = (0, 0, 255)) -> None:
    """
    Draw a health bar with gradient color based on health percentage.
    """
    x, y = position
    health_percentage = max(0, min(1, current_health / max_health))
    
    # Background
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    
    # Health bar
    bar_width = int(width * health_percentage)
    
    # Color gradient from green to red
    if health_percentage > 0.5:
        color = color_full
    elif health_percentage > 0.25:
        color = (0, 255, 255)  # Yellow
    else:
        color = color_low
    
    if bar_width > 0:
        cv2.rectangle(frame, (x, y), (x + bar_width, y + height), color, -1)
    
    # Border
    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)
    
    # Text
    text = f"{int(current_health)}/{int(max_health)}"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    text_x = x + (width - text_size[0]) // 2
    text_y = y + (height + text_size[1]) // 2
    draw_text(frame, text, (text_x, text_y), font_scale=0.6, thickness=2)


def is_point_in_rect(point: Tuple[int, int], rect: Tuple[int, int, int, int]) -> bool:
    """
    Check if a point is inside a rectangle.
    rect = (x, y, width, height)
    """
    px, py = point
    rx, ry, rw, rh = rect
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max."""
    return max(min_value, min(max_value, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by t (0-1)."""
    return a + (b - a) * clamp(t, 0, 1)


def get_landmark_coords(landmark, frame_width: int, frame_height: int) -> Tuple[int, int]:
    """Convert normalized landmark coordinates to pixel coordinates."""
    return int(landmark.x * frame_width), int(landmark.y * frame_height)


def overlay_image_alpha(background: np.ndarray, overlay: np.ndarray, 
                       position: Tuple[int, int], alpha: float = 1.0) -> np.ndarray:
    """
    Overlay an image with alpha channel onto background.
    position = (x, y) top-left corner
    """
    x, y = position
    
    # Ensure overlay is not empty
    if overlay is None or overlay.size == 0:
        return background
    
    h, w = overlay.shape[:2]
    
    # Boundary checks
    if x >= background.shape[1] or y >= background.shape[0] or x < 0 or y < 0:
        return background
    
    # Adjust if overlay goes beyond background boundaries
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        overlay = overlay[:, :w]
    
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        overlay = overlay[:h]
    
    # Ensure we still have valid dimensions
    if w <= 0 or h <= 0:
        return background
    
    # Check if overlay has alpha channel
    if len(overlay.shape) == 3 and overlay.shape[2] == 4:
        overlay_rgb = overlay[:, :, :3]
        overlay_alpha = overlay[:, :, 3:] / 255.0 * alpha
        
        # Extract region of interest
        roi = background[y:y+h, x:x+w]
        
        # Ensure dimensions match
        if roi.shape[:2] != overlay_rgb.shape[:2]:
            return background
        
        # Blend
        blended = (overlay_alpha * overlay_rgb + (1 - overlay_alpha) * roi).astype(np.uint8)
        background[y:y+h, x:x+w] = blended
    else:
        # No alpha channel, direct copy
        if overlay.shape[:2] == background[y:y+h, x:x+w].shape[:2]:
            background[y:y+h, x:x+w] = overlay[:, :, :3] if len(overlay.shape) == 3 else overlay
    
    return background

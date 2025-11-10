"""
Utility Helper Functions
"""
import cv2
import numpy as np
from typing import Tuple, List
import math
from PIL import Image, ImageDraw, ImageFont
import config

# Global cache for pre-rendered text images (to avoid lag)
_TEXT_CACHE = {}


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


def draw_text_with_font(frame: np.ndarray, text: str, position: Tuple[int, int],
                       font_path: str, font_size: int = 60,
                       color: Tuple[int, int, int] = (255, 255, 255),
                       outline: bool = True, outline_width: int = 4) -> None:
    """
    Draw text using custom TrueType/OpenType font (like Daydream).
    OPTIMIZED: Pre-renders and caches text to avoid lag.
    """
    global _TEXT_CACHE
    
    try:
        # Create cache key
        cache_key = (text, font_path, font_size, color, outline, outline_width)
        
        # Check if already cached
        if cache_key not in _TEXT_CACHE:
            # Load custom font
            font = ImageFont.truetype(font_path, font_size)
            
            # Get text bounding box
            dummy_img = Image.new('RGBA', (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0] + outline_width * 2
            text_height = bbox[3] - bbox[1] + outline_width * 2
            
            # Create transparent image for text only
            text_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            # Draw outline if requested
            if outline:
                for offset_x in range(-outline_width, outline_width + 1):
                    for offset_y in range(-outline_width, outline_width + 1):
                        if offset_x != 0 or offset_y != 0:
                            text_draw.text(
                                (outline_width + offset_x, outline_width + offset_y),
                                text, font=font, fill=(0, 0, 0, 255)
                            )
            
            # Draw main text (convert BGR to RGBA)
            color_rgba = (color[2], color[1], color[0], 255)
            text_draw.text((outline_width, outline_width), text, font=font, fill=color_rgba)
            
            # Convert PIL image to OpenCV format and cache it
            text_np = np.array(text_img)
            text_bgr = cv2.cvtColor(text_np, cv2.COLOR_RGBA2BGRA)
            _TEXT_CACHE[cache_key] = text_bgr
        
        # Use cached text image
        text_bgr = _TEXT_CACHE[cache_key]
        
        # Overlay using alpha blending (VERY fast!)
        overlay_image_alpha(frame, text_bgr, position, alpha=1.0)
        
    except Exception as e:
        # Fallback to regular text if custom font fails
        print(f"Custom font error: {e}, using fallback")
        draw_text(frame, text, position, font_scale=font_size/40, color=color, thickness=3, outline=outline)


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

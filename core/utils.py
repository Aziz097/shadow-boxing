import cv2
import numpy as np
import os
import pygame
from . import config

class FontManager:
    """Singleton Font Manager to avoid duplicate font loading"""
    _instance = None
    _font = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
        return cls._instance
    
    def get_font(self, font_path, size):
        """Get or load font with caching"""
        key = f"{font_path}_{size}"
        if key not in self._font:
            try:
                if os.path.exists(font_path):
                    self._font[key] = pygame.font.Font(font_path, size)
                else:
                    self._font[key] = pygame.font.SysFont("Arial", size)
            except Exception as e:
                print(f"Error loading font {font_path} size {size}: {e}")
                self._font[key] = pygame.font.SysFont("Arial", size)
        return self._font[key]

def load_image(path, size=None):
    """Load image with error handling"""
    if not os.path.exists(path):
        print(f"Warning: Image not found at {path}")
        return np.zeros((100, 100, 3), dtype=np.uint8)
    
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Warning: Failed to load image at {path}")
        return np.zeros((100, 100, 3), dtype=np.uint8)
    
    if size:
        img = cv2.resize(img, size)
    return img

def overlay_image(background, overlay, x, y):
    """Overlay transparent PNG onto background"""
    if overlay.shape[2] < 4:
        return background
    
    # Split overlay into BGR and alpha
    overlay_bgr = overlay[..., :3]
    overlay_alpha = overlay[..., 3:] / 255.0
    
    # Region of interest
    y1, y2 = y, y + overlay_bgr.shape[0]
    x1, x2 = x, x + overlay_bgr.shape[1]
    
    # Check boundaries
    if y1 < 0 or y2 > background.shape[0] or x1 < 0 or x2 > background.shape[1]:
        return background
    
    # Blend images
    roi = background[y1:y2, x1:x2]
    composite = overlay_alpha * overlay_bgr + (1 - overlay_alpha) * roi
    background[y1:y2, x1:x2] = composite.astype(np.uint8)
    
    return background

def create_rounded_rect(image, rect, color, thickness=2, radius=10):
    """Draw rounded rectangle"""
    x, y, w, h = rect
    cv2.rectangle(image, (x + radius, y), (x + w - radius, y + h), color, thickness)
    cv2.rectangle(image, (x, y + radius), (x + w, y + h - radius), color, thickness)
    
    # Corners
    cv2.circle(image, (x + radius, y + radius), radius, color, thickness)
    cv2.circle(image, (x + w - radius, y + radius), radius, color, thickness)
    cv2.circle(image, (x + radius, y + h - radius), radius, color, thickness)
    cv2.circle(image, (x + w - radius, y + h - radius), radius, color, thickness)
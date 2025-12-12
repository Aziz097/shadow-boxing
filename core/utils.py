"""Core utilities - font manager."""

import os
import pygame

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
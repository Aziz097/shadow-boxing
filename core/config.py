"""
Centralized Configuration Manager
All game settings loaded from config module provided by user
"""
import os
from . import constants

class Config:
    # === Paths ===
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    FONT_DIR = os.path.join(ASSETS_DIR, "font")
    SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
    SFX_DIR = os.path.join(ASSETS_DIR, "wav", "sfx")
    MUSIC_DIR = os.path.join(ASSETS_DIR, "wav", "music")
    
    FONT_PATH = os.path.join(FONT_DIR, "PressStart2P.ttf") 
    
    # === Game Settings ===
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 30
    FULLSCREEN = True
    
    # === Camera Settings ===
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    
    # === Round Settings ===
    NUM_ROUNDS = 3
    ROUND_DURATION = 20  # seconds per round
    REST_DURATION = 5   # seconds between rounds
    SPLASH_DURATION = 3  # seconds for round splash screen
    
    # === Hitbox Settings ===
    MIN_HITBOXES = 2
    MAX_HITBOXES = 4
    HITBOX_SIZE = 120
    HITBOX_MARGIN = 150
    
    # === Difficulty ===
    DEFAULT_DIFFICULTY = "MEDIUM"
    DIFFICULTY_SETTINGS = constants.DIFFICULTY_SETTINGS
    
    # === MediaPipe Settings ===
    HAND_MAX_NUM = 2
    HAND_MIN_DETECTION_CONFIDENCE = 0.4
    HAND_MIN_TRACKING_CONFIDENCE = 0.4
    POSE_MIN_DETECTION_CONFIDENCE = 0.4
    POSE_MIN_TRACKING_CONFIDENCE = 0.4
    FACE_MIN_DETECTION_CONFIDENCE = 0.4
    FACE_MIN_TRACKING_CONFIDENCE = 0.4
    
    # === Punch/Defense Settings ===
    FIST_ANGLE_THRESHOLD = 175
    FIST_DISTANCE_THRESHOLD = 0.31
    VELOCITY_THRESHOLD = 800
    PUNCH_COOLDOWN = 0.3
    DEFENSE_FACE_COVERAGE_THRESHOLD = 0.6
    
    @classmethod
    def get_difficulty_settings(cls):
        """Get current difficulty settings"""
        return cls.DIFFICULTY_SETTINGS[cls.DEFAULT_DIFFICULTY]
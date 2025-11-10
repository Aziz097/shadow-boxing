"""
Game Configuration
All game settings and difficulty parameters
"""
import os

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_DIR = os.path.join(ASSETS_DIR, "font")
IMAGE_DIR = os.path.join(ASSETS_DIR, "image")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
VFX_DIR = os.path.join(ASSETS_DIR, "vfx")

# Font
FONT_PATH = os.path.join(FONT_DIR, "daydream.otf")

# Images
HELM_IMAGE = os.path.join(IMAGE_DIR, "boxing-helm.png")
TARGET_ICON = os.path.join(IMAGE_DIR, "target-icon.png")
PUNCH_BAG_RED = os.path.join(IMAGE_DIR, "punch-bag-red.png")
PUNCH_BAG_BLUE = os.path.join(IMAGE_DIR, "punch-bag-blue.png")
PUNCH_BAG_BLACK = os.path.join(IMAGE_DIR, "punch-bag-black.png")
FIGHT_IMAGE = os.path.join(IMAGE_DIR, "fight.png")

# Sound Effects
SFX_ROUND_1 = os.path.join(SFX_DIR, "round", "round-1.mp3")
SFX_ROUND_2 = os.path.join(SFX_DIR, "round", "round-2.mp3")
SFX_ROUND_3 = os.path.join(SFX_DIR, "round", "round-3.mp3")
SFX_BOXING_BELL = os.path.join(SFX_DIR, "boxing-bell.mp3")
SFX_KO = os.path.join(SFX_DIR, "KO.mp3")
SFX_WEAK_PUNCH = os.path.join(SFX_DIR, "weak-punch.mp3")
SFX_STRONG_PUNCH = os.path.join(SFX_DIR, "strongpunch.mp3")
SFX_MEME_PUNCH = os.path.join(SFX_DIR, "punch-meme.mp3")

# === Game Settings ===
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 720
FPS = 60
FULLSCREEN = True  # Set to True for fullscreen

# Camera Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# === Round Settings ===
NUM_ROUNDS = 3
ROUND_DURATION = 20  # seconds per round
REST_DURATION = 10   # seconds between rounds
SPLASH_DURATION = 2  # seconds for round splash screen

# === Phase Timings ===
PLAYER_ATTACK_DURATION = 3  # seconds to hit all hitboxes
ENEMY_ATTACK_WARNING_TIME = 1.0  # seconds warning before enemy attacks
ENEMY_ATTACK_DURATION = 0.4  # actual attack animation duration

# === Hitbox Settings ===
MIN_HITBOXES = 2
MAX_HITBOXES = 4
HITBOX_SIZE = 120  # pixels - increased for easier hitting
HITBOX_MARGIN = 150  # minimum distance from screen edges

# === Health Settings ===
PLAYER_MAX_HEALTH = 100
ENEMY_MAX_HEALTH = 100

# === Damage Settings (Player to Enemy) ===
DAMAGE_COMBO_4 = 25  # 4 hits in 3 seconds
DAMAGE_COMBO_3 = 20  # 3 hits in 3 seconds
DAMAGE_COMBO_2 = 15  # 2 hits in 3 seconds
DAMAGE_COMBO_1 = 10  # 1 hit in 3 seconds

# Enemy Attack Damage (Random range if not blocked)
ENEMY_DAMAGE_MIN = 10
ENEMY_DAMAGE_MAX = 30

# === Difficulty Settings ===
DIFFICULTY_SETTINGS = {
    "EASY": {
        "enemy_attack_cooldown": (3.0, 5.0),  # (min, max) seconds between attacks
        "enemy_damage_multiplier": 0.7,       # 70% damage
        "player_attack_time": 3.5,            # More time to hit targets
        "enemy_attack_warning": 1.5,          # Longer warning time
    },
    "MEDIUM": {
        "enemy_attack_cooldown": (2.0, 3.5),
        "enemy_damage_multiplier": 1.0,       # 100% damage
        "player_attack_time": 3.0,
        "enemy_attack_warning": 1.0,
    },
    "HARD": {
        "enemy_attack_cooldown": (1.5, 2.5),
        "enemy_damage_multiplier": 1.3,       # 130% damage
        "player_attack_time": 2.5,            # Less time to hit targets
        "enemy_attack_warning": 0.7,          # Shorter warning time
    }
}

# Default difficulty
DEFAULT_DIFFICULTY = "MEDIUM"

# === MediaPipe Settings ===
# Hand Detection
HAND_MAX_NUM = 2
HAND_MIN_DETECTION_CONFIDENCE = 0.7
HAND_MIN_TRACKING_CONFIDENCE = 0.7

# Pose Detection
POSE_MIN_DETECTION_CONFIDENCE = 0.7
POSE_MIN_TRACKING_CONFIDENCE = 0.7

# Face Detection
FACE_MIN_DETECTION_CONFIDENCE = 0.7
FACE_MIN_TRACKING_CONFIDENCE = 0.7

# === Punch Detection Settings ===
FIST_ANGLE_THRESHOLD = 175  # degrees
FIST_DISTANCE_THRESHOLD = 0.31
VELOCITY_THRESHOLD = 800  # pixels per second for punch
MIN_PUNCH_VELOCITY = 500  # Minimum velocity to register as punch (not slow hand movement)
PUNCH_COOLDOWN = 0.3  # seconds between punches

# === Defense Detection Settings ===
DEFENSE_FACE_COVERAGE_THRESHOLD = 0.6  # How much hand must cover face
DEFENSE_MEMORY_DURATION = 0.6  # seconds to keep defense state
BLOCKING_DISTANCE = 100  # Distance from nose to wrist for blocking (pixels)

# === Dodge Detection Settings ===
DODGE_DISTANCE_THRESHOLD = 80  # Minimum distance to move for successful dodge (pixels)
DODGE_MEMORY_DURATION = 0.3  # How long dodge state persists (seconds)

# === Target Landmarks for Enemy Attack ===
ENEMY_TARGET_LANDMARKS = list(range(11))  # 0-10 (nose to shoulders)

# === UI Settings ===
# Colors (BGR format for OpenCV)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_ORANGE = (0, 165, 255)
COLOR_PURPLE = (255, 0, 255)

# Health Bar Settings
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 30
HEALTH_BAR_BORDER = 3

# Timer Settings
TIMER_FONT_SIZE = 60
ROUND_INDICATOR_FONT_SIZE = 40

# === Keybinds ===
KEY_START = ord(' ')  # Space to start
KEY_PAUSE = 27        # ESC to pause
KEY_QUIT = ord('q')   # Q to quit

# === Game States ===
class GameState:
    MENU = "MENU"
    SETTINGS = "SETTINGS"
    HELP = "HELP"
    PLAYING = "PLAYING"
    ROUND_SPLASH = "ROUND_SPLASH"
    REST = "REST"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME_OVER"

# === Phase States ===
class PhaseState:
    PLAYER_ATTACK = "PLAYER_ATTACK"
    ENEMY_ATTACK_WARNING = "ENEMY_ATTACK_WARNING"
    ENEMY_ATTACK = "ENEMY_ATTACK"
    TRANSITION = "TRANSITION"

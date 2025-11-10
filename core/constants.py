"""
Game constants and thresholds
Separate from config to avoid circular imports
"""
# Game states
GAME_STATES = {
    'MENU': 'MENU',
    'PLAYING': 'PLAYING',
    'ROUND_SPLASH': 'ROUND_SPLASH',
    'REST': 'REST',
    'GAME_OVER': 'GAME_OVER'
}

# Phase states
PHASE_STATES = {
    'PLAYER_ATTACK': 'PLAYER_ATTACK',
    'ENEMY_ATTACK_WARNING': 'ENEMY_ATTACK_WARNING',
    'ENEMY_ATTACK': 'ENEMY_ATTACK'
}

# Health settings
PLAYER_MAX_HEALTH = 100
ENEMY_MAX_HEALTH = 100

# Damage values
DAMAGE_VALUES = {
    'COMBO_4': 25,
    'COMBO_3': 20,
    'COMBO_2': 15,
    'COMBO_1': 10
}

# Enemy damage range
ENEMY_DAMAGE_MIN = 10
ENEMY_DAMAGE_MAX = 30

# Difficulty settings (copied from config)
DIFFICULTY_SETTINGS = {
    "EASY": {
        "enemy_attack_cooldown": (3.0, 5.0),
        "enemy_damage_multiplier": 0.7,
        "player_attack_time": 3.5,
        "enemy_attack_warning": 1.5,
    },
    "MEDIUM": {
        "enemy_attack_cooldown": (2.0, 3.5),
        "enemy_damage_multiplier": 1.0,
        "player_attack_time": 3.0,
        "enemy_attack_warning": 1.0,
    },
    "HARD": {
        "enemy_attack_cooldown": (1.5, 2.5),
        "enemy_damage_multiplier": 1.3,
        "player_attack_time": 2.5,
        "enemy_attack_warning": 0.7,
    }
}

# UI Colors (RGB - will be converted to BGR for OpenCV)
COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'PURPLE': (255, 0, 255),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0)
}
"""Game constants - states, damage values, and difficulty settings."""

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
ENEMY_DAMAGE_MAX = 20

# Combo System - Punch Types
PUNCH_TYPES = {
    'JAB': {'name': 'Jab'},
    'CROSS': {'name': 'Cross'},
    'HOOK': {'name': 'Hook'}
}

# Combo Patterns - Easy
COMBO_EASY = {
    'JAB_JAB': {
        'name': 'Double Jab',
        'sequence': ['JAB', 'JAB'],
        'damage': 20
    },
    'JAB_CROSS': {
        'name': 'Jab Cross',
        'sequence': ['JAB', 'CROSS'],
        'damage': 25
    }
}

# Combo Patterns - Medium
COMBO_MEDIUM = {
    'JAB_JAB_CROSS': {
        'name': 'Jab Jab Cross',
        'sequence': ['JAB', 'JAB', 'CROSS'],
        'damage': 35
    },
    'CROSS_HOOK': {
        'name': 'Cross Hook',
        'sequence': ['CROSS', 'HOOK'],
        'damage': 30
    },
    'JAB_HOOK': {
        'name': 'Jab Hook',
        'sequence': ['JAB', 'HOOK'],
        'damage': 28
    }
}

# Combo Patterns - Hard
COMBO_HARD = {
    'JAB_JAB_CROSS_HOOK': {
        'name': 'Four Punch Combo',
        'sequence': ['JAB', 'JAB', 'CROSS', 'HOOK'],
        'damage': 50
    },
    'JAB_HOOK_CROSS': {
        'name': 'Jab Hook Cross',
        'sequence': ['JAB', 'HOOK', 'CROSS'],
        'damage': 42
    },
    'CROSS_CROSS': {
        'name': 'Double Cross',
        'sequence': ['CROSS', 'CROSS'],
        'damage': 38
    }
}

# Difficulty settings (copied from config)
DIFFICULTY_SETTINGS = {
    "EASY": {
        "enemy_attack_cooldown": (3.0, 5.0),
        "enemy_damage_multiplier": 0.7,
        "player_attack_time": 3.5,
        "enemy_attack_warning": 1.5,
        "player_damage_ranges": {
            "JAB": (12, 13),
            "HOOK": (12, 14),
            "CROSS": (12, 15)
        }
    },
    "MEDIUM": {
        "enemy_attack_cooldown": (2.0, 3.5),
        "enemy_damage_multiplier": 1.0,
        "player_attack_time": 3.0,
        "enemy_attack_warning": 1.0,
        "player_damage_ranges": {
            "JAB": (8, 10),
            "HOOK": (8, 11),
            "CROSS": (8, 12)
        }
    },
    "HARD": {
        "enemy_attack_cooldown": (1.5, 2.5),
        "enemy_damage_multiplier": 1.3,
        "player_attack_time": 2.5,
        "enemy_attack_warning": 0.7,
        "player_damage_ranges": {
            "JAB": (5, 6),
            "HOOK": (5, 7),
            "CROSS": (5, 8)
        }
    }
}
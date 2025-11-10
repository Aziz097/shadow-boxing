import random
import time
from core import config, constants

class AIController:
    def __init__(self, game_config, enemy):
        self.config = game_config
        self.enemy = enemy
        self.last_attack_time = 0
        self.attack_pattern = None
        
    def should_attack(self, current_time, player_state):
        """Determine if enemy should attack"""
        # Don't attack if player is in player attack phase
        if player_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            return False
        
        # Don't attack during rest period
        if player_state.current_state == constants.GAME_STATES['REST']:
            return False
        
        # Don't attack if recently attacked
        difficulty = self.config.get_difficulty_settings()
        min_cooldown, max_cooldown = difficulty["enemy_attack_cooldown"]
        cooldown = random.uniform(min_cooldown, max_cooldown)
        
        return current_time - self.last_attack_time >= cooldown
    
    def select_target(self, face_landmarks):
        """Select a target landmark on player's face"""
        if not face_landmarks:
            return None
        
        # Target landmarks: 0-10 (nose to shoulders)
        target_index = random.choice(constants.ENEMY_TARGET_LANDMARKS)
        
        if target_index < len(face_landmarks):
            landmark = face_landmarks[target_index]
            return (
                int(landmark.x * self.config.CAMERA_WIDTH),
                int(landmark.y * self.config.CAMERA_HEIGHT)
            )
        
        return None
    
    def init_attack(self, current_time, face_landmarks):
        """Initialize enemy attack"""
        target = self.select_target(face_landmarks)
        if target:
            self.enemy.start_attack(target, current_time)
            self.last_attack_time = current_time
            return True
        return False
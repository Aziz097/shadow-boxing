"""
Enemy Attack System
Manages enemy attack with target icon and glove animation
Warning times: Easy 1.2s, Medium 1.0s, Hard 0.8s
"""
import time
import random
from core import constants

class EnemyAttackSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.is_warning = False
        self.is_attacking = False
        self.warning_start_time = 0
        self.attack_start_time = 0
        self.target_position = None
        self.glove_position = None
        self.glove_progress = 0
        self.attack_damage = 0
        self.warning_duration = 1.0  # Will be set based on difficulty
        
    def start_attack(self, face_bbox, current_time):
        """Start enemy attack sequence with random target on player face"""
        if face_bbox is None:
            return False
        
        face_x, face_y, face_w, face_h = face_bbox
        
        # Random target position within face area (mata, hidung, bibir, dll)
        # Avoid edges, target middle 60% of face
        margin_x = int(face_w * 0.2)
        margin_y = int(face_h * 0.2)
        
        target_x = face_x + margin_x + random.randint(0, face_w - 2*margin_x)
        target_y = face_y + margin_y + random.randint(0, face_h - 2*margin_y)
        
        self.target_position = (target_x, target_y)
        self.is_warning = True
        self.is_attacking = False
        self.warning_start_time = current_time
        self.glove_position = None
        self.glove_progress = 0
        
        # Set warning duration based on difficulty
        difficulty = self.config.get_difficulty_settings()
        difficulty_name = self.config.DEFAULT_DIFFICULTY
        
        if difficulty_name == "EASY":
            self.warning_duration = 1.2
        elif difficulty_name == "MEDIUM":
            self.warning_duration = 1.0
        else:  # HARD
            self.warning_duration = 0.8
        
        # Calculate damage
        base_damage = random.randint(constants.ENEMY_DAMAGE_MIN, constants.ENEMY_DAMAGE_MAX)
        self.attack_damage = int(base_damage * difficulty["enemy_damage_multiplier"])
        
        return True
    
    def update(self, current_time, is_defending):
        """Update attack state with glove animation from bottom to target"""
        attack_duration = 0.5  # 500ms for glove animation
        
        # Warning phase -> Attack phase transition
        if self.is_warning:
            if current_time - self.warning_start_time >= self.warning_duration:
                self.is_warning = False
                self.is_attacking = True
                self.attack_start_time = current_time
                # Glove starts from bottom center of screen
                self.glove_position = [self.config.CAMERA_WIDTH // 2, self.config.CAMERA_HEIGHT]
                print(f"[ENEMY ATTACK] Starting glove animation from bottom ({self.glove_position}) to target ({self.target_position})")
        
        # Attack animation - linear interpolation from bottom to target
        if self.is_attacking:
            elapsed = current_time - self.attack_start_time
            self.glove_progress = min(1.0, elapsed / attack_duration)
            
            # Interpolate glove position
            if self.target_position:
                start_x = self.config.CAMERA_WIDTH // 2
                start_y = self.config.CAMERA_HEIGHT
                target_x, target_y = self.target_position
                
                current_x = int(start_x + (target_x - start_x) * self.glove_progress)
                current_y = int(start_y + (target_y - start_y) * self.glove_progress)
                self.glove_position = [current_x, current_y]
            
            # Attack complete - apply damage
            if elapsed >= attack_duration:
                self.is_attacking = False
                
                # Calculate final damage (reduced if defending)
                final_damage = self.attack_damage
                if is_defending:
                    final_damage = int(final_damage * 0.2)  # 80% damage reduction
                
                return {
                    'damage': final_damage,
                    'position': self.target_position,
                    'was_defended': is_defending
                }
        
        return None
    
    def is_active(self):
        """Check if attack is in progress"""
        return self.is_warning or self.is_attacking
    
    def get_target_position(self):
        """Get target icon position - available during both warning and attack"""
        if self.is_warning or self.is_attacking:
            return self.target_position
        return None
    
    def get_glove_position(self):
        """Get current glove position for rendering"""
        if self.is_attacking:
            return self.glove_position
        return None
    
    def reset(self):
        """Reset attack system"""
        self.is_warning = False
        self.is_attacking = False
        self.target_position = None
        self.glove_position = None
        self.glove_progress = 0
        self.attack_damage = 0

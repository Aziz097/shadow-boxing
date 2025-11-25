"""Enemy attack system - manages attack warnings, targeting, and combo attacks."""

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
        
        # Combo attack properties
        self.combo_count = 0  # Current attack in combo
        self.combo_max = 0  # Total attacks in this combo (3-4)
        self.combo_delay = 0.4  # Delay between attacks in combo (400ms)
        self.combo_end_time = 0  # When to start next attack in combo
        self.was_defended_during_attack = False  # Track if player defended during attack animation
        
    def start_attack(self, face_bbox, current_time, pose_landmarks=None):
        """Start enemy attack sequence with random target on player face or head (pose fallback)"""
        if face_bbox is None and pose_landmarks is None:
            return False
        
        # Use face bbox if available, otherwise fallback to pose landmarks
        if face_bbox is not None:
            face_x, face_y, face_w, face_h = face_bbox
            
            # Random target position within face area (mata, hidung, bibir, dll)
            # Avoid edges, target middle 60% of face
            margin_x = int(face_w * 0.2)
            margin_y = int(face_h * 0.2)
            
            target_x = face_x + margin_x + random.randint(0, face_w - 2*margin_x)
            target_y = face_y + margin_y + random.randint(0, face_h - 2*margin_y)
        else:
            # Fallback to pose landmarks (head area)
            # Use pose landmarks 0-10 (head area) for random target
            target_landmarks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            random_idx = random.choice(target_landmarks)
            
            if random_idx < len(pose_landmarks):
                landmark = pose_landmarks[random_idx]
                target_x = int(landmark.x * self.config.CAMERA_WIDTH)
                target_y = int(landmark.y * self.config.CAMERA_HEIGHT)
            else:
                # Ultimate fallback: center of screen
                target_x = self.config.CAMERA_WIDTH // 2
                target_y = self.config.CAMERA_HEIGHT // 2
        
        self.target_position = (target_x, target_y)
        self.is_warning = True
        self.is_attacking = False
        self.warning_start_time = current_time
        self.glove_position = None
        self.glove_progress = 0
        
        # Initialize combo attack (2-3 attacks to fit in 4s max)
        # Total duration: warning + attacks×(0.5s attack + 0.4s delay)
        # Max: 1.2s + 3×0.9s = 3.9s
        self.combo_count = 0
        self.combo_max = random.randint(2, 3)
        
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
    
    def update(self, current_time, is_defending, face_bbox=None):
        """Update attack state with glove animation from bottom to target"""
        attack_duration = 0.5  # 500ms for glove animation
        
        # Warning phase -> Attack phase transition
        if self.is_warning:
            if current_time - self.warning_start_time >= self.warning_duration:
                self.is_warning = False
                self.is_attacking = True
                self.attack_start_time = current_time
                self.combo_count = 1  # Start first attack in combo
                self.was_defended_during_attack = False
                self.glove_position = [self.config.CAMERA_WIDTH // 2, self.config.CAMERA_HEIGHT]
        
        # Attack animation - linear interpolation from bottom to target
        if self.is_attacking:
            # Track if player is defending during attack animation
            if is_defending:
                self.was_defended_during_attack = True
            
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
                
                # Check if player dodged - both target AND glove must be in CURRENT face bbox
                player_dodged = False
                if self.target_position and self.glove_position:
                    target_x, target_y = self.target_position
                    glove_x, glove_y = self.glove_position
                    
                    # Check if face_bbox exists at hit moment
                    if face_bbox:
                        face_x, face_y, face_w, face_h = face_bbox
                        
                        # Check if target is still in current face area
                        target_in_face = (face_x <= target_x <= face_x + face_w and 
                                         face_y <= target_y <= face_y + face_h)
                        
                        # Check if glove is in current face area
                        glove_in_face = (face_x <= glove_x <= face_x + face_w and 
                                        face_y <= glove_y <= face_y + face_h)
                        
                        # Player dodged if either target or glove is outside current face
                        if not target_in_face or not glove_in_face:
                            player_dodged = True
                    else:
                        player_dodged = True
                
                # Calculate final damage and play appropriate sound
                if player_dodged:
                    final_damage = 0  # Complete dodge
                    # Sound will be played in game_state when registering attack result
                elif self.was_defended_during_attack:
                    final_damage = int(self.attack_damage * 0.2)
                    # Sound will be played in game_state when registering attack result
                else:
                    final_damage = self.attack_damage
                    # Sound will be played in game_state when registering attack result
                
                # Check if combo continues
                if self.combo_count < self.combo_max:
                    # Start next attack in combo after delay
                    self.combo_end_time = current_time + self.combo_delay
                    self.combo_count += 1
                    
                    # Generate new target for next attack
                    # Priority: face_bbox > pose landmarks fallback
                    if face_bbox:
                        face_x, face_y, face_w, face_h = face_bbox
                        margin_x = int(face_w * 0.2)
                        margin_y = int(face_h * 0.2)
                        target_x = face_x + margin_x + random.randint(0, face_w - 2*margin_x)
                        target_y = face_y + margin_y + random.randint(0, face_h - 2*margin_y)
                        self.target_position = (target_x, target_y)
                    else:
                        pass
                    
                    # Return damage but don't end combo
                    return {
                        'damage': final_damage,
                        'position': self.target_position,
                        'was_defended': self.was_defended_during_attack,
                        'was_dodged': player_dodged,
                        'combo_continues': True
                    }
                else:
                    return {
                        'damage': final_damage,
                        'position': self.target_position,
                        'was_defended': self.was_defended_during_attack,
                        'was_dodged': player_dodged,
                        'combo_continues': False
                    }
        
        # Check if it's time to start next attack in combo
        if not self.is_attacking and not self.is_warning and self.combo_count > 0 and self.combo_count <= self.combo_max:
            if current_time >= self.combo_end_time:
                # Start next attack in combo
                self.is_attacking = True
                self.attack_start_time = current_time
                self.glove_position = [self.config.CAMERA_WIDTH // 2, self.config.CAMERA_HEIGHT]
                self.glove_progress = 0
                self.was_defended_during_attack = False
        
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
        self.combo_count = 0
        self.combo_max = 0
        self.combo_end_time = 0
        self.was_defended_during_attack = False

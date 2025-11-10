import random
import time
from core import constants, config

class Enemy:
    def __init__(self, game_config):
        self.config = game_config
        self.health = constants.ENEMY_MAX_HEALTH
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.attack_progress = 0
        self.glove_position = None
        self.target_landmark = None
        self.is_attacking = False
        self.attack_end_time = 0
        self.warning_active = False
        self.warning_start_time = 0
        self.attack_damage = 0
        
    def take_damage(self, damage):
        """Apply damage to enemy"""
        self.health = max(0, self.health - damage)
        return self.health
    
    def start_attack(self, target_landmark, current_time):
        """Start enemy attack sequence"""
        self.target_landmark = target_landmark
        self.warning_active = True
        self.warning_start_time = current_time
        self.is_attacking = False
        
        # Set attack damage based on difficulty
        difficulty = self.config.get_difficulty_settings()
        base_damage = random.randint(constants.ENEMY_DAMAGE_MIN, constants.ENEMY_DAMAGE_MAX)
        self.attack_damage = int(base_damage * difficulty["enemy_damage_multiplier"])
    
    def update(self, current_time, game_state):
        """Update enemy state"""
        difficulty = self.config.get_difficulty_settings()
        
        # Handle attack warning phase
        if self.warning_active:
            warning_duration = difficulty["enemy_attack_warning"]
            if current_time - self.warning_start_time >= warning_duration:
                self.warning_active = False
                self.is_attacking = True
                self.attack_start_time = current_time
                
                # Set glove starting position (bottom of screen)
                self.glove_position = (
                    self.target_landmark[0], 
                    self.config.CAMERA_HEIGHT + 50  # Start below screen
                )
        
        # Handle active attack
        if self.is_attacking:
            attack_duration = 0.5  # Time for glove to reach target
            elapsed = current_time - self.attack_start_time
            self.attack_progress = min(1.0, elapsed / attack_duration)
            
            # Check if attack is complete
            if elapsed >= attack_duration:
                self.is_attacking = False
                self.attack_end_time = current_time
                self.glove_position = None
    
    def get_attack_damage(self):
        """Get the damage of the current attack"""
        return self.attack_damage
    
    def is_in_warning_phase(self):
        """Check if enemy is in warning phase"""
        return self.warning_active
    
    def is_attacking_active(self):
        """Check if enemy is currently attacking"""
        return self.is_attacking
    
    def is_alive(self):
        """Check if enemy is still alive"""
        return self.health > 0
    
    def get_target_position(self):
        """Get the target position for the attack"""
        if self.target_landmark:
            return self.target_landmark
        return None
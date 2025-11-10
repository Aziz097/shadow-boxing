"""
Enemy Module
Manages enemy AI state, health, and attacks
"""
import random
import time
import config


class Enemy:
    """Enemy/System opponent."""
    
    def __init__(self, difficulty: str = "MEDIUM"):
        """Initialize enemy."""
        self.max_health = config.ENEMY_MAX_HEALTH
        self.current_health = self.max_health
        self.difficulty = difficulty
        self.difficulty_settings = config.DIFFICULTY_SETTINGS[difficulty]
        
        # Attack state
        self.is_attacking = False
        self.attack_target_landmark = None
        self.attack_start_time = 0
        self.attack_warning_time = 0
        self.last_attack_time = 0
        
        # Stats
        self.total_attacks = 0
        self.successful_hits = 0
        self.total_damage_dealt = 0
        
    def take_damage(self, damage: int):
        """Take damage."""
        self.current_health = max(0, self.current_health - damage)
    
    def reset_health(self):
        """Reset health to maximum."""
        self.current_health = self.max_health
    
    def is_alive(self) -> bool:
        """Check if enemy is alive."""
        return self.current_health > 0
    
    def get_health_percentage(self) -> float:
        """Get health as percentage (0-1)."""
        return self.current_health / self.max_health
    
    def can_attack(self, current_time: float) -> bool:
        """Check if enemy can initiate attack."""
        if self.is_attacking:
            return False
        
        cooldown_min, cooldown_max = self.difficulty_settings['enemy_attack_cooldown']
        cooldown = random.uniform(cooldown_min, cooldown_max)
        
        return current_time - self.last_attack_time >= cooldown
    
    def start_attack(self, current_time: float):
        """Start attack sequence."""
        self.is_attacking = True
        self.attack_warning_time = current_time
        self.attack_target_landmark = random.choice(config.ENEMY_TARGET_LANDMARKS)
        self.total_attacks += 1
    
    def is_in_warning_phase(self, current_time: float) -> bool:
        """Check if in warning phase."""
        if not self.is_attacking:
            return False
        
        warning_duration = self.difficulty_settings['enemy_attack_warning']
        return current_time - self.attack_warning_time < warning_duration
    
    def execute_attack(self, current_time: float, player_is_defending: bool) -> int:
        """
        Execute attack and return damage.
        
        Args:
            current_time: Current time
            player_is_defending: Whether player is defending
            
        Returns:
            Damage dealt (0 if blocked)
        """
        if player_is_defending:
            damage = 0
        else:
            base_damage = random.randint(config.ENEMY_DAMAGE_MIN, config.ENEMY_DAMAGE_MAX)
            damage = int(base_damage * self.difficulty_settings['enemy_damage_multiplier'])
            self.successful_hits += 1
            self.total_damage_dealt += damage
        
        self.is_attacking = False
        self.last_attack_time = current_time
        
        return damage
    
    def get_stats(self) -> dict:
        """Get enemy statistics."""
        hit_rate = (self.successful_hits / self.total_attacks * 100) if self.total_attacks > 0 else 0
        
        return {
            'health': self.current_health,
            'total_attacks': self.total_attacks,
            'successful_hits': self.successful_hits,
            'hit_rate': hit_rate,
            'damage_dealt': self.total_damage_dealt
        }

"""
Player Module
Manages player state, health, and detection integration
"""
import time
from typing import Optional, Tuple
import config


class Player:
    """Player character with health and state management."""
    
    def __init__(self):
        """Initialize player."""
        self.max_health = config.PLAYER_MAX_HEALTH
        self.current_health = self.max_health
        self.is_defending = False
        self.is_punching = False
        self.last_punch_time = 0
        self.punch_cooldown = config.PUNCH_COOLDOWN
        
        # Combo tracking
        self.combo_hits = 0
        self.combo_start_time = 0
        self.combo_window = config.PLAYER_ATTACK_DURATION
        
        # Stats
        self.total_punches = 0
        self.total_hits = 0
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        self.successful_blocks = 0
        
    def take_damage(self, damage: int) -> bool:
        """
        Take damage if not defending.
        
        Args:
            damage: Amount of damage
            
        Returns:
            True if damage was taken, False if blocked
        """
        if self.is_defending:
            self.successful_blocks += 1
            return False
        
        self.current_health = max(0, self.current_health - damage)
        self.total_damage_taken += damage
        return True
    
    def heal(self, amount: int):
        """Heal player."""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def reset_health(self):
        """Reset health to maximum."""
        self.current_health = self.max_health
    
    def can_punch(self, current_time: float) -> bool:
        """Check if player can punch (not in cooldown)."""
        return current_time - self.last_punch_time >= self.punch_cooldown
    
    def register_punch(self, current_time: float):
        """Register a punch."""
        self.is_punching = True
        self.last_punch_time = current_time
        self.total_punches += 1
    
    def register_hit(self, current_time: float):
        """Register a successful hit on target."""
        self.total_hits += 1
        
        # Combo tracking
        if self.combo_hits == 0:
            self.combo_start_time = current_time
        
        self.combo_hits += 1
    
    def get_combo_count(self, current_time: float) -> int:
        """
        Get current combo count (resets after window expires).
        
        Args:
            current_time: Current time
            
        Returns:
            Current combo count
        """
        if current_time - self.combo_start_time > self.combo_window:
            self.combo_hits = 0
        
        return self.combo_hits
    
    def reset_combo(self):
        """Reset combo counter."""
        self.combo_hits = 0
        self.combo_start_time = 0
    
    def is_alive(self) -> bool:
        """Check if player is alive."""
        return self.current_health > 0
    
    def get_health_percentage(self) -> float:
        """Get health as percentage (0-1)."""
        return self.current_health / self.max_health
    
    def get_stats(self) -> dict:
        """Get player statistics."""
        accuracy = (self.total_hits / self.total_punches * 100) if self.total_punches > 0 else 0
        
        return {
            'health': self.current_health,
            'total_punches': self.total_punches,
            'total_hits': self.total_hits,
            'accuracy': accuracy,
            'damage_dealt': self.total_damage_dealt,
            'damage_taken': self.total_damage_taken,
            'successful_blocks': self.successful_blocks
        }

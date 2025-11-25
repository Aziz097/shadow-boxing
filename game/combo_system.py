"""Combo system - manages punch combos, timing evaluation, and sequence tracking."""

import time
import random
from core import constants

class ComboSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.current_combo = None
        self.combo_sequence = []
        self.combo_progress = 0
        self.last_hit_time = 0
        self.combo_complete = False
        
    def start_new_combo(self, difficulty="MEDIUM"):
        """Select and start a new combo based on difficulty"""
        # Select combo based on difficulty
        if difficulty == "EASY":
            available_combos = constants.COMBO_EASY
        elif difficulty == "HARD":
            available_combos = constants.COMBO_HARD
        else:  # MEDIUM
            available_combos = constants.COMBO_MEDIUM
        
        # Pick random combo
        combo_key = random.choice(list(available_combos.keys()))
        self.current_combo = available_combos[combo_key]
        self.combo_sequence = self.current_combo['sequence']
        self.combo_progress = 0
        self.last_hit_time = time.time()
        self.combo_complete = False
        
        return self.current_combo
    
    def register_hit(self, hit_time):
        """Register a hit in the combo sequence"""
        self.last_hit_time = hit_time
        self.combo_progress += 1
        
        # Check if combo is complete
        if self.combo_progress >= len(self.combo_sequence):
            self.combo_complete = True
        
        print(f"Combo progress: {self.combo_progress}/{len(self.combo_sequence)}")
        return self.combo_progress
    
    def calculate_damage(self):
        """Calculate total damage based on combo completion"""
        if not self.current_combo:
            return 0
        
        # Return full combo damage if complete
        if self.combo_complete:
            return self.current_combo['damage']
        
        # Partial damage based on progress
        progress_ratio = self.combo_progress / len(self.combo_sequence)
        partial_damage = int(self.current_combo['damage'] * progress_ratio * 0.5)
        return partial_damage
    
    def get_current_punch_type(self):
        """Get the current punch type in sequence"""
        if self.combo_progress < len(self.combo_sequence):
            return self.combo_sequence[self.combo_progress]
        return None
    
    def get_next_punch_type(self):
        """Get the next punch type in sequence"""
        if self.combo_progress + 1 < len(self.combo_sequence):
            return self.combo_sequence[self.combo_progress + 1]
        return None
    
    def is_combo_complete(self):
        """Check if current combo is complete"""
        return self.combo_complete
    
    def get_combo_name(self):
        """Get current combo name"""
        if self.current_combo:
            return self.current_combo['name']
        return None
    
    def get_combo_display(self):
        """Get combo sequence for display with progress indicator"""
        if not self.current_combo:
            return ""
        
        display = []
        for i, punch in enumerate(self.combo_sequence):
            if i < self.combo_progress:
                display.append(f"✓{punch}")  # Completed
            elif i == self.combo_progress:
                display.append(f"→{punch}")  # Current
            else:
                display.append(punch)  # Upcoming
        
        return " ".join(display)
    
    def get_performance_summary(self):
        """Get performance summary with progress"""
        return {
            'hits': self.combo_progress,
            'total': len(self.combo_sequence),
            'complete': self.combo_complete
        }
    
    def reset(self):
        """Reset combo system"""
        self.current_combo = None
        self.combo_sequence = []
        self.combo_progress = 0
        self.last_hit_time = 0
        self.combo_complete = False

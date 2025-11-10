import random
from core import constants, config

class DamageSystem:
    @staticmethod
    def calculate_player_damage(combo_count):
        """Calculate damage player deals to enemy based on combo"""
        if combo_count >= 4:
            return constants.DAMAGE_VALUES['COMBO_4']
        elif combo_count >= 3:
            return constants.DAMAGE_VALUES['COMBO_3']
        elif combo_count >= 2:
            return constants.DAMAGE_VALUES['COMBO_2']
        else:
            return constants.DAMAGE_VALUES['COMBO_1']
    
    @staticmethod
    def calculate_enemy_damage(is_defending, is_dodging, difficulty_settings):
        """Calculate damage enemy deals to player"""
        if is_dodging:
            return 0  # Complete dodge
        
        base_damage = random.randint(constants.ENEMY_DAMAGE_MIN, constants.ENEMY_DAMAGE_MAX)
        damage = base_damage * difficulty_settings["enemy_damage_multiplier"]
        
        if is_defending:
            damage *= 0.2  # 80% damage reduction when defending
        
        return int(damage)
    
    @staticmethod
    def is_critical_hit():
        """Determine if attack is a critical hit"""
        return random.random() < 0.15  # 15% chance for critical hit
    
    @staticmethod
    def apply_critical_multiplier(damage):
        """Apply critical hit multiplier"""
        return int(damage * 1.5)  # 50% extra damage
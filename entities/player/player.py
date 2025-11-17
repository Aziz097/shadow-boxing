import time
from core import constants

class Player:
    def __init__(self, game_config):
        self.config = game_config
        self.health = constants.PLAYER_MAX_HEALTH
        self.combo_count = 0
        self.last_hit_time = 0
        self.defense_active = False
        self.dodge_active = False
        self.score = 0
        self.hitbox_hits = []
        
    def take_damage(self, damage, is_defending, is_dodging):
        """Apply damage to player with defense/dodge modifiers"""
        if is_dodging:
            damage = 0  # Complete dodge
        elif is_defending:
            difficulty = self.config.get_difficulty_settings()
            damage *= (1 - 0.8 * difficulty["enemy_damage_multiplier"])  # 80% reduction
        
        damage = int(max(0, damage))
        self.health = max(0, self.health - damage)
        return damage
    
    def register_hit(self, hitbox_value):
        """Register a successful hit on enemy"""
        current_time = time.time()
        
        # Reset combo if too much time passed
        if current_time - self.last_hit_time > 1.5:  # 1.5 seconds between hits for combo
            self.combo_count = 0
        
        self.combo_count += 1
        self.last_hit_time = current_time
        
        # Calculate damage based on combo
        if self.combo_count >= 4:
            damage = constants.DAMAGE_VALUES['COMBO_4']
        elif self.combo_count >= 3:
            damage = constants.DAMAGE_VALUES['COMBO_3']
        elif self.combo_count >= 2:
            damage = constants.DAMAGE_VALUES['COMBO_2']
        else:
            damage = constants.DAMAGE_VALUES['COMBO_1']
        
        # Add score multiplier for combos
        self.score += damage * min(self.combo_count, 4)
        
        # Store hit for VFX/animation
        self.hitbox_hits.append({
            'time': current_time,
            'damage': damage,
            'combo': self.combo_count
        })
        
        return damage
    
    def reset_combo(self):
        """Reset combo counter"""
        self.combo_count = 0
    
    def activate_defense(self):
        """Activate defense state"""
        self.defense_active = True
    
    def deactivate_defense(self):
        """Deactivate defense state"""
        self.defense_active = False
    
    def activate_dodge(self):
        """Activate dodge state"""
        self.dodge_active = True
        # Dodge provides temporary invincibility
        self.dodge_timer = time.time() + 0.5  # 0.5 seconds of invincibility
    
    def update(self, current_time):
        """Update player state"""
        # Deactivate dodge after timer
        if self.dodge_active and current_time > self.dodge_timer:
            self.dodge_active = False
        
        # Clean up old hits
        self.hitbox_hits = [hit for hit in self.hitbox_hits if current_time - hit['time'] < 1.0]
    
    def is_alive(self):
        """Check if player is still alive"""
        return self.health > 0
"""
Game State Manager untuk Shadow Boxing
Mengelola HP, damage, score, dan status game
"""
import time

class GameState:
    """Manages game state including HP, damage, and scoring"""
    
    def __init__(self, player_max_hp=100, enemy_max_hp=100):
        """Initialize game state"""
        # Health Points
        self.player_max_hp = player_max_hp
        self.enemy_max_hp = enemy_max_hp
        self.player_hp = player_max_hp
        self.enemy_hp = enemy_max_hp
        
        # Damage values (increased for 60s rounds)
        self.enemy_damage = 20  # damage per enemy hit
        self.player_damage = 25  # damage per player punch
        
        # Score tracking
        self.player_punches_landed = 0
        self.player_punches_total = 0
        self.enemy_hits_landed = 0
        self.enemy_hits_total = 0
        self.blocks_successful = 0
        
        # Stats untuk adaptive AI
        self.player_defense_count = 0
        self.player_attack_count = 0
        
        # Combat state
        self.last_hit_time = 0
        self.hit_cooldown = 0.3  # prevent rapid repeated hits
        
        # Game status
        self.game_over = False
        self.winner = None
        
    def enemy_hit_player(self, current_time):
        """Enemy successfully hits player"""
        if current_time - self.last_hit_time < self.hit_cooldown:
            return False  # too soon
            
        self.player_hp = max(0, self.player_hp - self.enemy_damage)
        self.enemy_hits_landed += 1
        self.enemy_hits_total += 1
        self.last_hit_time = current_time
        
        # Check KO
        if self.player_hp <= 0:
            self.game_over = True
            self.winner = "ENEMY"
            
        return True
    
    def player_hit_enemy(self, current_time):
        """Player successfully hits enemy"""
        if current_time - self.last_hit_time < self.hit_cooldown:
            return False
            
        self.enemy_hp = max(0, self.enemy_hp - self.player_damage)
        self.player_punches_landed += 1
        self.player_attack_count += 1
        self.last_hit_time = current_time
        
        # Check KO
        if self.enemy_hp <= 0:
            self.game_over = True
            self.winner = "PLAYER"
            
        return True
    
    def enemy_attack_attempt(self):
        """Record enemy attack attempt"""
        self.enemy_hits_total += 1
    
    def player_punch_attempt(self):
        """Record player punch attempt"""
        self.player_punches_total += 1
        self.player_attack_count += 1
    
    def player_blocked(self):
        """Player successfully blocked an attack"""
        self.blocks_successful += 1
        self.player_defense_count += 1
    
    def get_player_hp_percentage(self):
        """Get player HP as percentage"""
        return (self.player_hp / self.player_max_hp) * 100
    
    def get_enemy_hp_percentage(self):
        """Get enemy HP as percentage"""
        return (self.enemy_hp / self.enemy_max_hp) * 100
    
    def get_player_accuracy(self):
        """Get player punch accuracy percentage"""
        if self.player_punches_total == 0:
            return 0.0
        return (self.player_punches_landed / self.player_punches_total) * 100
    
    def get_enemy_accuracy(self):
        """Get enemy hit accuracy percentage"""
        if self.enemy_hits_total == 0:
            return 0.0
        return (self.enemy_hits_landed / self.enemy_hits_total) * 100
    
    def get_stats_summary(self):
        """Get complete stats summary"""
        return {
            'player_hp': self.player_hp,
            'enemy_hp': self.enemy_hp,
            'player_punches': self.player_punches_landed,
            'player_accuracy': self.get_player_accuracy(),
            'blocks': self.blocks_successful,
            'enemy_hits': self.enemy_hits_landed,
            'enemy_accuracy': self.get_enemy_accuracy()
        }
    
    def reset(self):
        """Reset game state for new round"""
        self.player_hp = self.player_max_hp
        self.enemy_hp = self.enemy_max_hp
        self.player_punches_landed = 0
        self.player_punches_total = 0
        self.enemy_hits_landed = 0
        self.enemy_hits_total = 0
        self.blocks_successful = 0
        self.player_defense_count = 0
        self.player_attack_count = 0
        self.game_over = False
        self.winner = None
        self.last_hit_time = 0

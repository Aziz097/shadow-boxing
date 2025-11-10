import time
import random
from core import constants, config

class RoundManager:
    def __init__(self, game_config):
        self.config = game_config
        self.current_round = 1
        self.round_start_time = 0
        self.round_end_time = 0
        self.rest_start_time = 0
        self.is_rest_period = False
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']  # Start with player attack
        self.phase_start_time = 0
        self.hitboxes = []
        self.hit_hitboxes = []
        self.enemy_target = None
        self.glove_position = None
        self.attack_progress = 0
        
    def start_round(self, current_time):
        """Start a new round"""
        self.current_round = min(self.current_round, self.config.NUM_ROUNDS)
        self.round_start_time = current_time
        self.is_rest_period = False
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
        self.phase_start_time = current_time
        
        # Generate hitboxes for player attack phase
        self._generate_hitboxes()
        
        return f"ROUND_{self.current_round}"
    
    def _generate_hitboxes(self):
        """Generate random hitboxes for player attack phase"""
        self.hitboxes = []
        self.hit_hitboxes = []
        
        num_hitboxes = random.randint(self.config.MIN_HITBOXES, self.config.MAX_HITBOXES)
        
        for _ in range(num_hitboxes):
            # Ensure hitboxes are within screen bounds with margin
            x = random.randint(self.config.HITBOX_MARGIN, self.config.CAMERA_WIDTH - self.config.HITBOX_MARGIN - self.config.HITBOX_SIZE)
            y = random.randint(self.config.HITBOX_MARGIN, self.config.CAMERA_HEIGHT - self.config.HITBOX_MARGIN - self.config.HITBOX_SIZE)
            
            self.hitboxes.append((x, y, self.config.HITBOX_SIZE, self.config.HITBOX_SIZE))
    
    def start_rest_period(self, current_time):
        """Start rest period between rounds"""
        self.is_rest_period = True
        self.rest_start_time = current_time
    
    def next_round(self):
        """Prepare for next round"""
        self.current_round += 1
        self.hitboxes = []
        self.hit_hitboxes = []
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
    
    def update(self, current_time, player, enemy):
        """Update round state"""
        if self.is_rest_period:
            # Check if rest period ended
            if current_time - self.rest_start_time >= self.config.REST_DURATION:
                self.is_rest_period = False
                self.phase_start_time = current_time
                self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
                self._generate_hitboxes()
            return
        
        # Handle round transitions
        round_elapsed = current_time - self.round_start_time
        if round_elapsed >= self.config.ROUND_DURATION:
            if self.current_round < self.config.NUM_ROUNDS:
                self.start_rest_period(current_time)
            return
        
        # Handle phase transitions
        phase_elapsed = current_time - self.phase_start_time
        
        if self.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            # Check if player attack phase ended
            player_attack_time = self.config.get_difficulty_settings()["player_attack_time"]
            if phase_elapsed >= player_attack_time:
                # Calculate combo damage
                combo_count = len(self.hit_hitboxes)
                if combo_count > 0:
                    damage = self._calculate_combo_damage(combo_count)
                    enemy.take_damage(damage)
                
                # Transition to enemy attack warning
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK_WARNING']
                self.phase_start_time = current_time
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK_WARNING']:
            # Enemy is about to attack - show target
            warning_time = self.config.get_difficulty_settings()["enemy_attack_warning"]
            if phase_elapsed >= warning_time:
                # Transition to actual enemy attack
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK']
                self.phase_start_time = current_time
                self.attack_progress = 0
                
                # Set glove starting position
                if self.enemy_target:
                    self.glove_position = (
                        self.enemy_target[0],
                        self.config.CAMERA_HEIGHT + 50  # Start below screen
                    )
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK']:
            # Enemy is attacking - move glove toward target
            attack_duration = 0.5  # 0.5 seconds for attack animation
            self.attack_progress = min(1.0, phase_elapsed / attack_duration)
            
            # Check if attack is complete
            if phase_elapsed >= attack_duration:
                # Apply damage if player didn't defend
                damage = enemy.get_attack_damage()
                # Damage will be applied in main game loop based on player's defense state
                
                # Reset for next phase
                self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
                self.phase_start_time = current_time
                self._generate_hitboxes()
    
    def _calculate_combo_damage(self, combo_count):
        """Calculate damage based on combo count"""
        if combo_count >= 4:
            return constants.DAMAGE_VALUES['COMBO_4']
        elif combo_count >= 3:
            return constants.DAMAGE_VALUES['COMBO_3']
        elif combo_count >= 2:
            return constants.DAMAGE_VALUES['COMBO_2']
        else:
            return constants.DAMAGE_VALUES['COMBO_1']
    
    def get_remaining_time(self, current_time):
        """Get remaining time in current round"""
        if self.is_rest_period:
            elapsed = current_time - self.rest_start_time
            return max(0, self.config.REST_DURATION - elapsed)
        
        elapsed = current_time - self.round_start_time
        return max(0, self.config.ROUND_DURATION - elapsed)
    
    def is_round_over(self):
        """Check if current round is over"""
        return self.current_round > self.config.NUM_ROUNDS
    
    def get_phase_remaining_time(self, current_time):
        """Get remaining time in current phase"""
        elapsed = current_time - self.phase_start_time
        
        if self.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            total_time = self.config.get_difficulty_settings()["player_attack_time"]
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK_WARNING']:
            total_time = self.config.get_difficulty_settings()["enemy_attack_warning"]
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK']:
            total_time = 0.5  # Fixed attack duration
        else:
            total_time = 0
        
        return max(0, total_time - elapsed)
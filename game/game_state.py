import time
from core import constants, config
import random

class GameState:
    def __init__(self, game_config):
        self.config = game_config
        self.current_state = constants.GAME_STATES['MENU']
        self.current_round = 1
        self.player_health = constants.PLAYER_MAX_HEALTH
        self.enemy_health = constants.ENEMY_MAX_HEALTH
        self.round_timer = self.config.ROUND_DURATION
        self.rest_timer = self.config.REST_DURATION
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
        self.combo_count = 0
        self.score = 0
        self.face_bbox = None
        self.enemy_target = None
        self.glove_position = None
        self.attack_progress = 0
        self.defense_active = False
        self.dodge_detected = False
        self.active_hitboxes = []
        self.hit_hitboxes = []
        self.vfx_effects = []
        self.sounds_to_play = []
        
    def start_game(self):
        """Start the game from menu"""
        self.current_state = constants.GAME_STATES['ROUND_SPLASH']
        self.current_round = 1
        self.player_health = constants.PLAYER_MAX_HEALTH
        self.enemy_health = constants.ENEMY_MAX_HEALTH
        self.score = 0
        self.combo_count = 0
        
    def start_round(self, round_num):
        """Start a specific round"""
        self.current_state = constants.GAME_STATES['PLAYING']
        self.current_round = round_num
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
        self.combo_count = 0
        self.active_hitboxes = self._generate_hitboxes()
        self.hit_hitboxes = []
        
    def _generate_hitboxes(self):
        """Generate random hitboxes for player attack phase"""
        hitboxes = []
        num_hitboxes = random.randint(self.config.MIN_HITBOXES, self.config.MAX_HITBOXES)
        
        for _ in range(num_hitboxes):
            # Ensure hitboxes are within screen bounds with margin
            x = random.randint(self.config.HITBOX_MARGIN, self.config.CAMERA_WIDTH - self.config.HITBOX_MARGIN - self.config.HITBOX_SIZE)
            y = random.randint(self.config.HITBOX_MARGIN, self.config.CAMERA_HEIGHT - self.config.HITBOX_MARGIN - self.config.HITBOX_SIZE)
            
            hitboxes.append((x, y, self.config.HITBOX_SIZE, self.config.HITBOX_SIZE))
        
        return hitboxes
    
    def start_rest_period(self):
        """Start rest period between rounds"""
        self.current_state = constants.GAME_STATES['REST']
        self.rest_timer = self.config.REST_DURATION
    
    def game_over(self, player_won):
        """End the game"""
        self.current_state = constants.GAME_STATES['GAME_OVER']
        self.player_won = player_won
    
    def update(self, current_time, vision_system):
        """Update game state"""
        if self.current_state == constants.GAME_STATES['PLAYING']:
            self._update_playing_state(current_time)
        elif self.current_state == constants.GAME_STATES['REST']:
            self._update_rest_period(current_time)
        elif self.current_state == constants.GAME_STATES['ROUND_SPLASH']:
            self._update_round_splash(current_time)
    
    def _update_playing_state(self, current_time):
        """Update during active gameplay"""
        # Update timers
        self.round_timer = max(0, self.config.ROUND_DURATION - (current_time - self.round_start_time))
        
        # Check for round end
        if self.round_timer <= 0:
            if self.current_round < self.config.NUM_ROUNDS:
                self.current_state = constants.GAME_STATES['REST']
                self.rest_timer = self.config.REST_DURATION
                self.rest_start_time = current_time
            else:
                # Game over
                player_won = self.player_health > self.enemy_health
                self.game_over(player_won)
        
        # Update phase timer and transitions
        phase_elapsed = current_time - self.phase_start_time
        difficulty = self.config.get_difficulty_settings()
        
        if self.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            # Player has limited time to hit targets
            if phase_elapsed >= difficulty["player_attack_time"]:
                # Calculate damage from hit hitboxes
                damage = self._calculate_combo_damage(len(self.hit_hitboxes))
                self.enemy_health = max(0, self.enemy_health - damage)
                self.score += damage
                
                # Transition to enemy attack warning
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK_WARNING']
                self.phase_start_time = current_time
                self.enemy_target = self._select_enemy_target()
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK_WARNING']:
            # Show target for enemy attack
            if phase_elapsed >= difficulty["enemy_attack_warning"]:
                # Transition to actual enemy attack
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK']
                self.phase_start_time = current_time
                self.attack_progress = 0
                
                # Set glove starting position below screen
                if self.enemy_target:
                    self.glove_position = (
                        self.enemy_target[0],
                        self.config.CAMERA_HEIGHT + 50
                    )
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK']:
            # Move glove toward target
            attack_duration = 0.5  # 0.5 seconds for attack animation
            self.attack_progress = min(1.0, phase_elapsed / attack_duration)
            
            # Check if attack is complete
            if phase_elapsed >= attack_duration:
                # Apply damage if player didn't defend or dodge
                if not self.defense_active and not self.dodge_detected:
                    damage = random.randint(constants.ENEMY_DAMAGE_MIN, constants.ENEMY_DAMAGE_MAX)
                    difficulty = self.config.get_difficulty_settings()
                    damage = int(damage * difficulty["enemy_damage_multiplier"])
                    self.player_health = max(0, self.player_health - damage)
                
                # Reset for next phase
                self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
                self.phase_start_time = current_time
                self.active_hitboxes = self._generate_hitboxes()
                self.hit_hitboxes = []
                self.combo_count = 0
        
        # Reset dodge detection
        self.dodge_detected = False
    
    def _update_rest_period(self, current_time):
        """Update during rest period"""
        elapsed = current_time - self.rest_start_time
        self.rest_timer = max(0, self.config.REST_DURATION - elapsed)
        
        # End of rest period
        if self.rest_timer <= 0:
            self.current_round += 1
            if self.current_round <= self.config.NUM_ROUNDS:
                self.current_state = constants.GAME_STATES['ROUND_SPLASH']
            else:
                # Final round complete - game over
                player_won = self.player_health > self.enemy_health
                self.game_over(player_won)
    
    def _update_round_splash(self, current_time):
        """Update during round splash screen"""
        if not hasattr(self, 'splash_start_time'):
            self.splash_start_time = current_time
        
        elapsed = current_time - self.splash_start_time
        if elapsed >= self.config.SPLASH_DURATION:
            self.current_state = constants.GAME_STATES['PLAYING']
            self.round_start_time = current_time
            self.phase_start_time = current_time
    
    def _select_enemy_target(self):
        """Select a random target on player's face"""
        # In a real implementation, this would use actual face landmarks
        # For now, we'll use a random position near the face center
        if self.face_bbox:
            x, y, w, h = self.face_bbox
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Add some randomness to the target position
            target_x = face_center_x + random.randint(-30, 30)
            target_y = face_center_y + random.randint(-30, 30)
            
            return (target_x, target_y)
        
        # Fallback to screen center
        return (self.config.CAMERA_WIDTH // 2, self.config.CAMERA_HEIGHT // 3)
    
    def _calculate_combo_damage(self, hit_count):
        """Calculate damage based on number of hits in combo"""
        if hit_count >= 4:
            return constants.DAMAGE_VALUES['COMBO_4']
        elif hit_count >= 3:
            return constants.DAMAGE_VALUES['COMBO_3']
        elif hit_count >= 2:
            return constants.DAMAGE_VALUES['COMBO_2']
        elif hit_count >= 1:
            return constants.DAMAGE_VALUES['COMBO_1']
        return 0
    
    def register_hit(self, hitbox):
        """Register a hit on a hitbox"""
        if hitbox not in self.hit_hitboxes:
            self.hit_hitboxes.append(hitbox)
            self.combo_count += 1
            return self.combo_count
        return 0
    
    def add_vfx(self, x, y, effect_type):
        """Add visual effect"""
        self.vfx_effects.append({
            'x': x,
            'y': y,
            'type': effect_type,
            'time': time.time(),
            'duration': 0.5
        })
    
    def play_sound(self, sound_name):
        """Queue a sound to play"""
        self.sounds_to_play.append(sound_name)
    
    def clean_vfx(self):
        """Remove expired VFX"""
        current_time = time.time()
        self.vfx_effects = [vfx for vfx in self.vfx_effects if current_time - vfx['time'] < vfx['duration']]
    
    def get_active_sounds(self):
        """Get and clear sounds to play"""
        sounds = self.sounds_to_play.copy()
        self.sounds_to_play.clear()
        return sounds
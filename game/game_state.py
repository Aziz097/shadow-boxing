import time
import random
from core import constants, config
from game.hit_box_system import HitBoxSystem
from entities.enemy.enemy_attack_system import EnemyAttackSystem

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
        self.pose_landmarks = None  # Store pose landmarks for fallback
        self.defense_active = False
        self.dodge_detected = False
        self.vfx_effects = []
        self.vfx_hits = []  # For hit VFX
        self.sounds_to_play = []
        self.round_start_time = time.time()
        self.phase_start_time = time.time()
        self.rest_start_time = 0
        self.splash_played = False
        
        # KO effect tracking
        self.ko_effect_active = False
        self.ko_start_time = 0
        self.ko_duration = 2.5  # 2.5 seconds for KO animation
        self.result_shown = False  # Flag to prevent duplicate result screen calls
        
        # Initialize systems
        self.hitbox_system = HitBoxSystem(game_config)
        self.enemy_attack_system = EnemyAttackSystem(game_config)
        
        # Phase duration (3 seconds for player attack)
        self.player_attack_duration = 3.0
        self.enemy_damage_applied = False
        
    def start_game(self):
        """Start the game from menu"""
        self.current_state = constants.GAME_STATES['ROUND_SPLASH']
        self.current_round = 1
        self.player_health = constants.PLAYER_MAX_HEALTH
        self.enemy_health = constants.ENEMY_MAX_HEALTH
        self.score = 0
        self.combo_count = 0
        self.splash_played = False
        self.ko_effect_active = False
        self.ko_sfx_played = False
        self.result_shown = False  # Reset result flag
        
    def start_round(self, round_num):
        """Start a specific round with hitbox generation"""
        self.current_state = constants.GAME_STATES['PLAYING']
        self.current_round = round_num
        self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
        self.combo_count = 0
        self.splash_played = True
        self.round_start_time = time.time()
        self.phase_start_time = time.time()
        
        # Generate hitboxes for player attack (pass face_bbox to avoid face area)
        self.hitbox_system.generate_hitboxes(face_bbox=self.face_bbox)
        
        # Reset enemy attack system
        self.enemy_attack_system.reset()
        self.enemy_damage_applied = False
        
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
        self.rest_start_time = time.time()
    
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
        """Update during active gameplay with phase transitions"""
        # Check if either player is KO'd (trigger KO effect)
        if self.player_health <= 0 and not self.ko_effect_active:
            print(f"[KO] Player knocked out! Starting KO effect...")
            self.ko_effect_active = True
            self.ko_start_time = current_time
            self.ko_sfx_played = False  # Reset for SFX
            self.player_won = False
            return
        
        if self.enemy_health <= 0 and not self.ko_effect_active:
            print(f"[KO] Enemy knocked out! Starting KO effect...")
            self.ko_effect_active = True
            self.ko_start_time = current_time
            self.ko_sfx_played = False  # Reset for SFX
            self.player_won = True
            return
        
        # Check if KO effect finished
        if self.ko_effect_active:
            if current_time - self.ko_start_time >= self.ko_duration:
                print(f"[KO] Effect duration complete")
                # Don't call game_over here - let main.py handle transition
            return
        
        # Update timers
        self.round_timer = max(0, self.config.ROUND_DURATION - (current_time - self.round_start_time))
        
        # Check for round end
        if self.round_timer <= 0:
            if self.current_round < self.config.NUM_ROUNDS:
                self.current_state = constants.GAME_STATES['REST']
                self.rest_timer = self.config.REST_DURATION
                self.rest_start_time = current_time
            else:
                player_won = self.player_health > self.enemy_health
                self.game_over(player_won)
            return
        
        # Phase transitions
        phase_elapsed = current_time - self.phase_start_time
        
        if self.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            # Player attack phase - 3 seconds
            if phase_elapsed >= self.player_attack_duration:
                # Calculate total damage from hit hitboxes
                hit_count = self.hitbox_system.get_hit_count()
                if hit_count > 0:
                    print(f"Player hit {hit_count} targets!")
                
                # Transition to enemy attack warning
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK_WARNING']
                self.phase_start_time = current_time
                self.combo_count = 0  # Reset combo for next phase
                
                # Check if enemy still alive before starting attack
                if self.enemy_health <= 0:
                    print(f"[GAME OVER] Enemy health depleted!")
                    self.game_over(True)  # Player won
                    return
                
                # Start enemy attack
                self.enemy_attack_system.start_attack(self.face_bbox, current_time, self.pose_landmarks)
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK_WARNING']:
            # Warning phase - target icon visible
            # Update enemy attack system to check for warning -> attack transition
            attack_result = self.enemy_attack_system.update(current_time, self.defense_active, self.face_bbox)
            
            if not self.enemy_attack_system.is_warning:
                # Transitioned to attack phase
                self.phase = constants.PHASE_STATES['ENEMY_ATTACK']
                print(f"[DEBUG] Transitioning to ENEMY_ATTACK phase, glove should appear now!")
        
        elif self.phase == constants.PHASE_STATES['ENEMY_ATTACK']:
            # Update enemy attack system
            attack_result = self.enemy_attack_system.update(current_time, self.defense_active, self.face_bbox)
            
            if attack_result:
                # Attack completed - apply damage
                damage = attack_result['damage']
                self.player_health = max(0, self.player_health - damage)  # Prevent negative health
                
                if attack_result['was_defended']:
                    print(f"Enemy attack DEFENDED! Damage reduced to {damage}")
                else:
                    print(f"Enemy attack HIT! Damage: {damage}")
                
                # Check if combo continues or ends
                if attack_result.get('combo_continues', False):
                    # Combo continues - stay in ENEMY_ATTACK phase
                    print(f"[COMBO] Waiting for next attack...")
                else:
                    # Combo complete - check if player still alive
                    if self.player_health <= 0:
                        print(f"[GAME OVER] Player health depleted!")
                        self.game_over(False)  # Player lost
                        return
                    
                    # Reset to player attack phase
                    self.phase = constants.PHASE_STATES['PLAYER_ATTACK']
                    self.phase_start_time = current_time
                    self.hitbox_system.generate_hitboxes(face_bbox=self.face_bbox)  # Pass face_bbox
                    self.hit_hitboxes = {}
                    self.combo_count = 0
                    self.enemy_damage_applied = False
        
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
                self.splash_played = False
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
            self.hit_hitboxes[hitbox] = time.time()  # Simpan waktu hit
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
    
    def is_alive(self):
        """Check if game is still active"""
        return self.current_state not in [constants.GAME_STATES['GAME_OVER']]
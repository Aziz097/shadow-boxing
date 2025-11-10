"""
Game Manager - Main game loop and state management
"""
import cv2
import time
import random
import numpy as np
from typing import List, Tuple, Optional

import config
from config import GameState, PhaseState

from systems.camera_manager import CameraManager
from systems.mediapipe_manager import MediaPipeManager
from systems.audio_manager import AudioManager
from systems.visual_effects import VisualEffectsManager

from player.player import Player
from enemy.enemy import Enemy

from utils.helpers import draw_text, draw_health_bar, is_point_in_rect, get_landmark_coords


class Hitbox:
    """Represents a punch target hitbox."""
    def __init__(self, x: int, y: int, size: int = config.HITBOX_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.hit = False
        self.hit_time = 0
    
    def check_collision(self, point: Tuple[int, int]) -> bool:
        """Check if point collides with hitbox."""
        return is_point_in_rect(point, (self.x, self.y, self.size, self.size))


class GameManager:
    """Main game manager."""
    
    def __init__(self):
        """Initialize game manager."""
        # Systems
        self.camera = CameraManager()
        self.mediapipe = MediaPipeManager()
        self.audio = AudioManager()
        self.vfx = VisualEffectsManager()
        
        # Game state
        self.state = GameState.MENU
        self.phase = PhaseState.PLAYER_ATTACK
        self.difficulty = config.DEFAULT_DIFFICULTY
        
        # Entities
        self.player = Player()
        self.enemy = Enemy(self.difficulty)
        
        # Round management
        self.current_round = 1
        self.round_time_remaining = config.ROUND_DURATION
        self.rest_time_remaining = config.REST_DURATION
        self.splash_time_remaining = config.SPLASH_DURATION
        self.splash_start_time = 0
        self.rest_start_time = 0
        
        # Phase management
        self.phase_start_time = 0
        self.player_attack_duration = config.PLAYER_ATTACK_DURATION
        
        # Hitboxes
        self.hitboxes: List[Hitbox] = []
        self.hitbox_spawn_time = 0
        
        # Defense detection
        self.last_defense_time = 0
        self.defense_memory_duration = config.DEFENSE_MEMORY_DURATION
        
        # Dodge detection
        self.target_initial_pos = None  # Store initial position of attack target
        self.last_dodge_time = 0
        self.dodge_memory_duration = config.DODGE_MEMORY_DURATION
        
        # Game over
        self.winner = None
        
        # Timing
        self.last_frame_time = time.time()
        self.running = True
        
    def initialize(self) -> bool:
        """Initialize all systems."""
        if not self.camera.open():
            return False
        
        print("Game initialized successfully!")
        return True
    
    def generate_hitboxes(self):
        """Generate random hitboxes for player attack phase - only on left and right sides."""
        self.hitboxes.clear()
        
        frame_width, frame_height = self.camera.get_dimensions()
        num_boxes = random.randint(config.MIN_HITBOXES, config.MAX_HITBOXES)
        
        # Define center zone to avoid (body area)
        center_zone_start = frame_width * 0.35  # 35% from left
        center_zone_end = frame_width * 0.65    # 65% from left
        
        for _ in range(num_boxes):
            # Randomly choose left or right side
            if random.random() < 0.5:
                # Left side
                x = random.randint(config.HITBOX_MARGIN, 
                                 int(center_zone_start - config.HITBOX_SIZE))
            else:
                # Right side
                x = random.randint(int(center_zone_end), 
                                 frame_width - config.HITBOX_SIZE - config.HITBOX_MARGIN)
            
            y = random.randint(config.HITBOX_MARGIN, 
                             frame_height - config.HITBOX_SIZE - config.HITBOX_MARGIN)
            
            self.hitboxes.append(Hitbox(x, y))
        
        self.hitbox_spawn_time = time.time()
        print(f"Generated {num_boxes} hitboxes (left/right only)")
    
    def check_defense(self, current_time: float) -> bool:
        """
        Check if player is defending - simplified and more reliable.
        Returns True if hands are raised to face level.
        """
        hand_landmarks = self.mediapipe.get_hand_landmarks()
        pose_landmarks = self.mediapipe.get_pose_landmarks()
        
        if not hand_landmarks:
            return False
        
        frame_width, frame_height = self.camera.get_dimensions()
        defense_detected = False
        
        # Method 1: Check if hand near face using pose landmarks (nose)
        if pose_landmarks and hand_landmarks:
            nose = pose_landmarks.landmark[0]  # Nose landmark
            nose_x, nose_y = get_landmark_coords(nose, frame_width, frame_height)
            
            for hand_lm in hand_landmarks:
                # Check wrist position relative to nose
                wrist = hand_lm.landmark[0]
                wrist_x, wrist_y = get_landmark_coords(wrist, frame_width, frame_height)
                
                # Calculate distance from wrist to nose
                distance = np.sqrt((wrist_x - nose_x)**2 + (wrist_y - nose_y)**2)
                
                # If wrist is close to nose (within face area)
                if distance < 100:  # pixels - tighter detection
                    defense_detected = True
                    self.last_defense_time = current_time
                    # Only print occasionally to reduce spam
                    if not hasattr(self, '_last_block_print') or current_time - self._last_block_print > 0.5:
                        print(f"BLOCKING!")
                        self._last_block_print = current_time
                    break
        
        # Method 2: Fallback - check if hands are in upper-center area
        if not defense_detected and hand_landmarks:
            for hand_lm in hand_landmarks:
                wrist = hand_lm.landmark[0]
                wrist_x, wrist_y = get_landmark_coords(wrist, frame_width, frame_height)
                
                # Check if wrist in upper-center area (face region)
                center_x = frame_width / 2
                upper_y = frame_height * 0.4
                
                # Distance from center-upper point
                dx = abs(wrist_x - center_x)
                dy = abs(wrist_y - upper_y)
                
                if dx < frame_width * 0.25 and dy < frame_height * 0.2:
                    defense_detected = True
                    self.last_defense_time = current_time
                    break
        
        # Memory: keep defense active for short duration
        if not defense_detected:
            if current_time - self.last_defense_time < self.defense_memory_duration:
                defense_detected = True
        
        return defense_detected
    
    def check_dodge(self, current_time: float) -> bool:
        """
        Check if player dodged enemy attack by moving head/body.
        Returns True if target landmark moved significantly from initial position.
        """
        pose_landmarks = self.mediapipe.get_pose_landmarks()
        
        if not pose_landmarks or self.target_initial_pos is None:
            return False
        
        frame_width, frame_height = self.camera.get_dimensions()
        
        # Get current position of attack target
        target_lm = pose_landmarks.landmark[self.enemy.attack_target_landmark]
        current_x, current_y = get_landmark_coords(target_lm, frame_width, frame_height)
        
        # Calculate distance moved from initial position
        init_x, init_y = self.target_initial_pos
        distance_moved = np.sqrt((current_x - init_x)**2 + (current_y - init_y)**2)
        
        # Successful dodge if moved beyond threshold
        if distance_moved > config.DODGE_DISTANCE_THRESHOLD:
            self.last_dodge_time = current_time
            if not hasattr(self, '_last_dodge_print') or current_time - self._last_dodge_print > 0.5:
                print(f"DODGED! Moved {distance_moved:.1f}px")
                self._last_dodge_print = current_time
            return True
        
        # Memory: keep dodge active for short duration
        if current_time - self.last_dodge_time < self.dodge_memory_duration:
            return True
        
        return False
    
    def check_hitbox_collisions(self, hand_landmarks, frame_width: int, frame_height: int):
        """Check if hand hits any hitbox - uses hand landmarks only (not body)."""
        current_time = time.time()
        
        for hand_lm in hand_landmarks:
            # Check multiple hand points for better detection
            check_points = [
                hand_lm.landmark[0],   # Wrist
                hand_lm.landmark[5],   # Index finger knuckle
                hand_lm.landmark[9],   # Middle finger knuckle
                hand_lm.landmark[13],  # Ring finger knuckle
                hand_lm.landmark[17],  # Pinky knuckle
                hand_lm.landmark[8],   # Index fingertip
                hand_lm.landmark[12],  # Middle fingertip
            ]
            
            for point in check_points:
                punch_x, punch_y = get_landmark_coords(point, frame_width, frame_height)
                
                for hitbox in self.hitboxes:
                    if not hitbox.hit and hitbox.check_collision((punch_x, punch_y)):
                        hitbox.hit = True
                        hitbox.hit_time = time.time()
                        self.player.register_hit(time.time())
                        
                        # ALWAYS play punch sound
                        self.audio.play_punch_sound()
                        
                        print(f"HIT! Hitbox at ({hitbox.x}, {hitbox.y})")
                        return True
        return False
    
    def calculate_combo_damage(self) -> Tuple[int, int]:
        """Calculate damage based on combo hits."""
        combo = self.player.combo_hits
        
        if combo >= 4:
            return config.DAMAGE_COMBO_4, combo
        elif combo == 3:
            return config.DAMAGE_COMBO_3, combo
        elif combo == 2:
            return config.DAMAGE_COMBO_2, combo
        elif combo == 1:
            return config.DAMAGE_COMBO_1, combo
        
        return 0, 0
    
    def update_game(self, dt: float):
        """Update game logic."""
        current_time = time.time()
        
        if self.state == GameState.ROUND_SPLASH:
            # Wait for splash duration
            elapsed = current_time - self.splash_start_time
            if elapsed >= config.SPLASH_DURATION:
                self.state = GameState.PLAYING
                self.phase_start_time = time.time()
                print("Starting gameplay!")
            return
        
        if self.state == GameState.REST:
            # Rest period countdown
            self.rest_time_remaining -= dt
            if self.rest_time_remaining <= 0:
                # Start next round
                self.current_round += 1
                self.round_time_remaining = config.ROUND_DURATION
                self.audio.play_round_sound(self.current_round)
                self.state = GameState.ROUND_SPLASH
                self.splash_time_remaining = config.SPLASH_DURATION
                self.splash_start_time = time.time()
                print(f"Starting Round {self.current_round}")
            return
        
        if self.state == GameState.PLAYING:
            # Check for KO during round
            if not self.player.is_alive() or not self.enemy.is_alive():
                self.end_round()
                return
            
            # Update defense status
            self.player.is_defending = self.check_defense(current_time)
            
            # Update round timer
            self.round_time_remaining -= dt
            
            if self.round_time_remaining <= 0:
                # Round ended
                self.end_round()
                return
            
            # Phase management
            if self.phase == PhaseState.PLAYER_ATTACK:
                phase_elapsed = current_time - self.phase_start_time
                
                if len(self.hitboxes) == 0:
                    self.generate_hitboxes()
                
                # Check hitbox collisions
                hand_landmarks = self.mediapipe.get_hand_landmarks()
                if hand_landmarks:
                    frame_width, frame_height = self.camera.get_dimensions()
                    self.check_hitbox_collisions(hand_landmarks, frame_width, frame_height)
                
                # Check if all hit or time expired
                all_hit = all(hb.hit for hb in self.hitboxes)
                time_expired = phase_elapsed >= self.player_attack_duration
                
                if all_hit or time_expired:
                    # Calculate and apply damage
                    damage, combo = self.calculate_combo_damage()
                    if damage > 0:
                        self.enemy.take_damage(damage)
                        self.player.total_damage_dealt += damage
                        # Play combo sound based on final damage
                        if combo >= 4:
                            self.audio.play_sound('strong_punch')
                        elif combo >= 2:
                            self.audio.play_sound('meme_punch')
                        self.vfx.trigger_screen_shake(intensity=5 * combo)
                    
                    self.player.reset_combo()
                    self.transition_to_enemy_attack()
            
            elif self.phase == PhaseState.ENEMY_ATTACK_WARNING:
                # Store initial target position when warning starts
                if self.target_initial_pos is None:
                    pose_landmarks = self.mediapipe.get_pose_landmarks()
                    if pose_landmarks:
                        frame_width, frame_height = self.camera.get_dimensions()
                        target_lm = pose_landmarks.landmark[self.enemy.attack_target_landmark]
                        self.target_initial_pos = get_landmark_coords(target_lm, frame_width, frame_height)
                
                if not self.enemy.is_in_warning_phase(current_time):
                    self.phase = PhaseState.ENEMY_ATTACK
            
            elif self.phase == PhaseState.ENEMY_ATTACK:
                # Check both defense (blocking) and dodge
                is_defending = self.check_defense(current_time)
                is_dodging = self.check_dodge(current_time)
                
                # Attack misses if either blocking OR dodging
                avoided = is_defending or is_dodging
                damage = self.enemy.execute_attack(current_time, avoided)
                
                if damage > 0:
                    self.player.take_damage(damage)
                    self.audio.play_sound('weak_punch')
                    self.vfx.trigger_screen_shake(intensity=15)
                else:
                    # Avoided (blocked or dodged)
                    if is_dodging:
                        print("DODGED!")
                    else:
                        print("BLOCKED!")
                
                # Reset target position for next attack
                self.target_initial_pos = None
                self.transition_to_player_attack()
    
    def transition_to_player_attack(self):
        """Transition to player attack phase."""
        self.phase = PhaseState.PLAYER_ATTACK
        self.phase_start_time = time.time()
        self.hitboxes.clear()
        # Reset dodge tracking
        self.target_initial_pos = None
    
    def transition_to_enemy_attack(self):
        """Transition to enemy attack phase."""
        self.phase = PhaseState.ENEMY_ATTACK_WARNING
        self.enemy.start_attack(time.time())
        # Reset dodge tracking for new attack
        self.target_initial_pos = None
    
    def end_round(self):
        """End current round."""
        self.audio.play_bell()
        print(f"Round {self.current_round} ended!")
        
        # Check for KO
        if not self.player.is_alive():
            self.winner = "ENEMY"
            self.audio.play_ko()
            self.state = GameState.GAME_OVER
            print("PLAYER KO!")
            return
        elif not self.enemy.is_alive():
            self.winner = "PLAYER"
            self.audio.play_ko()
            self.state = GameState.GAME_OVER
            print("ENEMY KO!")
            return
        
        # Continue to next round or end game
        if self.current_round >= config.NUM_ROUNDS:
            # Determine winner by health
            if self.player.current_health > self.enemy.current_health:
                self.winner = "PLAYER"
            elif self.enemy.current_health > self.player.current_health:
                self.winner = "ENEMY"
            else:
                self.winner = "DRAW"
            self.state = GameState.GAME_OVER
            print(f"Game over! Winner: {self.winner}")
        else:
            # Go to rest period
            self.state = GameState.REST
            self.rest_time_remaining = config.REST_DURATION
            self.rest_start_time = time.time()
            print(f"Rest period before round {self.current_round + 1}")
    
    def render_game(self, frame: np.ndarray):
        """Render game elements."""
        # Resize to full window size
        frame = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        frame_width, frame_height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        
        # Get camera dimensions for scaling hitboxes
        cam_width, cam_height = self.camera.get_dimensions()
        scale_x = frame_width / cam_width
        scale_y = frame_height / cam_height
        
        # Draw hand landmarks (ALWAYS show)
        hand_landmarks = self.mediapipe.get_hand_landmarks()
        if hand_landmarks:
            self.mediapipe.draw_hand_landmarks(frame)
        
        # Draw pose landmarks
        pose_landmarks = self.mediapipe.get_pose_landmarks()
        if pose_landmarks:
            self.mediapipe.draw_pose_landmarks(frame)
        
        # Draw helm overlay
        if pose_landmarks:
            self.vfx.draw_helm_overlay(frame, pose_landmarks, frame_width, frame_height)
        
        # Draw hitboxes (player attack phase) - scaled
        if self.phase == PhaseState.PLAYER_ATTACK:
            for hitbox in self.hitboxes:
                scaled_x = int(hitbox.x * scale_x)
                scaled_y = int(hitbox.y * scale_y)
                scaled_size = int(hitbox.size * max(scale_x, scale_y))
                self.vfx.draw_hitbox(frame, (scaled_x, scaled_y), scaled_size, hit=hitbox.hit)
        
        # Draw enemy attack warning
        if self.phase == PhaseState.ENEMY_ATTACK_WARNING and pose_landmarks:
            target_lm = pose_landmarks.landmark[self.enemy.attack_target_landmark]
            target_x = int(target_lm.x * frame_width)
            target_y = int(target_lm.y * frame_height)
            progress = (time.time() - self.enemy.attack_warning_time) / self.enemy.difficulty_settings['enemy_attack_warning']
            self.vfx.draw_target_warning(frame, (target_x, target_y), progress)
        
        # Draw HUD
        self.render_hud(frame)
        
        # Apply screen shake
        frame = self.vfx.apply_screen_shake(frame, self.last_frame_time)
        
        return frame
    
    def render_hud(self, frame: np.ndarray):
        """Render HUD elements."""
        frame_width, frame_height = self.camera.get_dimensions()
        
        # Player health (bottom left)
        draw_text(frame, "PLAYER", (20, frame_height - 60), font_scale=0.8, color=(0, 255, 0))
        draw_health_bar(frame, (20, frame_height - 40), self.player.current_health, 
                       self.player.max_health, width=250, height=25)
        
        # Enemy health (top right)
        draw_text(frame, "ENEMY", (frame_width - 280, 30), font_scale=0.8, color=(0, 0, 255))
        draw_health_bar(frame, (frame_width - 280, 50), self.enemy.current_health,
                       self.enemy.max_health, width=250, height=25)
        
        # Round and timer (top center)
        timer_text = f"ROUND {self.current_round} - {int(self.round_time_remaining)}s"
        text_size = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
        timer_x = (frame_width - text_size[0]) // 2
        draw_text(frame, timer_text, (timer_x, 50), font_scale=1.2, thickness=3, color=(255, 255, 0))
        
        # Phase indicator with instructions
        if self.phase == PhaseState.PLAYER_ATTACK:
            phase_text = "PUNCH THE TARGETS!"
            phase_color = (0, 255, 0)
            # Show combo counter
            combo = self.player.get_combo_count(time.time())
            if combo > 0:
                combo_text = f"COMBO: {combo}/{len(self.hitboxes)}"
                draw_text(frame, combo_text, (frame_width // 2 - 100, frame_height - 100), 
                         font_scale=1.0, color=(0, 215, 255), thickness=2)
        elif self.phase == PhaseState.ENEMY_ATTACK_WARNING:
            phase_text = "DODGE OR BLOCK!"
            phase_color = (0, 165, 255)  # Orange
        else:
            phase_text = "DODGE OR BLOCK!"
            phase_color = (0, 0, 255)
        
        draw_text(frame, phase_text, (frame_width // 2 - 150, frame_height - 50), 
                 font_scale=1.0, color=phase_color, thickness=2)
        
        # Defense/Dodge status indicator
        current_time = time.time()
        if self.player.is_defending:
            draw_text(frame, "BLOCKING!", (20, 100), font_scale=1.5, color=(0, 255, 255), thickness=3)
        elif current_time - self.last_dodge_time < self.dodge_memory_duration:
            draw_text(frame, "DODGED!", (20, 100), font_scale=1.5, color=(255, 128, 0), thickness=3)
    
    def render_menu(self, frame: np.ndarray):
        """Render menu screen with instructions."""
        frame_width, frame_height = self.camera.get_dimensions()
        
        # Resize frame to window size
        frame = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        frame_width, frame_height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        
        # Show landmarks even in menu
        hand_landmarks = self.mediapipe.get_hand_landmarks()
        if hand_landmarks:
            self.mediapipe.draw_hand_landmarks(frame)
        
        pose_landmarks = self.mediapipe.get_pose_landmarks()
        if pose_landmarks:
            self.mediapipe.draw_pose_landmarks(frame)
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)
        
        # Title
        title = "SHADOW BOXING"
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 5)[0]
        title_x = (frame_width - title_size[0]) // 2
        draw_text(frame, title, (title_x, 120), font_scale=2.5, thickness=5, color=(255, 255, 0))
        
        # Instructions
        instructions = [
            "",
            "HOW TO PLAY:",
            "",
            "ATTACK PHASE:",
            "- Punch the targets on LEFT & RIGHT",
            "- Hit all targets for max damage!",
            "- Combo: 4 hits = 25%, 3 hits = 20%",
            "",
            "DEFENSE PHASE:",
            "- Red target shows enemy attack",
            "- BLOCK: Cover face with hands",
            "- DODGE: Move your head/body away!",
            "",
            "CONTROLS:",
            "SPACE - Start Game",
            "ESC - Pause | Q - Quit",
            "",
            "Press SPACE to begin!",
        ]
        
        y = 220
        for line in instructions:
            if line.startswith("HOW TO") or line.startswith("ATTACK") or line.startswith("DEFENSE") or line.startswith("CONTROLS"):
                color = (0, 255, 255)
                scale = 1.0
            elif line == "" or line.startswith("Press"):
                color = (255, 255, 255)
                scale = 0.9
            else:
                color = (200, 200, 200)
                scale = 0.8
            
            if line:
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)[0]
                text_x = (frame_width - text_size[0]) // 2
                draw_text(frame, line, (text_x, y), font_scale=scale, thickness=2, color=color)
            y += 50
        
        return frame
    
    def render_splash(self, frame: np.ndarray):
        """Render round splash screen."""
        frame = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        frame_width, frame_height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        
        # Dark overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.2, overlay, 0.8, 0)
        
        # Round text
        round_text = f"ROUND {self.current_round}"
        text_size = cv2.getTextSize(round_text, cv2.FONT_HERSHEY_SIMPLEX, 4.0, 8)[0]
        text_x = (frame_width - text_size[0]) // 2
        text_y = frame_height // 2
        draw_text(frame, round_text, (text_x, text_y), font_scale=4.0, thickness=8, color=(255, 255, 0))
        
        # "FIGHT!" text
        fight_text = "FIGHT!"
        fight_size = cv2.getTextSize(fight_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)[0]
        fight_x = (frame_width - fight_size[0]) // 2
        draw_text(frame, fight_text, (fight_x, text_y + 100), font_scale=2.0, thickness=4, color=(0, 255, 0))
        
        return frame
    
    def render_rest(self, frame: np.ndarray):
        """Render rest period screen."""
        frame = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        frame_width, frame_height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        
        # Show landmarks during rest
        hand_landmarks = self.mediapipe.get_hand_landmarks()
        if hand_landmarks:
            self.mediapipe.draw_hand_landmarks(frame)
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.5, overlay, 0.5, 0)
        
        # Rest text
        rest_text = "REST PERIOD"
        text_size = cv2.getTextSize(rest_text, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 6)[0]
        text_x = (frame_width - text_size[0]) // 2
        draw_text(frame, rest_text, (text_x, frame_height // 2 - 100), font_scale=3.0, thickness=6, color=(0, 255, 255))
        
        # Countdown
        countdown_text = f"{int(self.rest_time_remaining)}s"
        count_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 5.0, 10)[0]
        count_x = (frame_width - count_size[0]) // 2
        draw_text(frame, countdown_text, (count_x, frame_height // 2 + 50), font_scale=5.0, thickness=10, color=(255, 255, 255))
        
        # Next round info
        next_text = f"Next: ROUND {self.current_round + 1}"
        next_size = cv2.getTextSize(next_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        next_x = (frame_width - next_size[0]) // 2
        draw_text(frame, next_text, (next_x, frame_height // 2 + 200), font_scale=1.5, thickness=3, color=(255, 255, 0))
        
        # Current stats
        stats_y = frame_height - 200
        draw_text(frame, f"Player Health: {int(self.player.current_health)}%", 
                 (100, stats_y), font_scale=1.0, thickness=2, color=(0, 255, 0))
        draw_text(frame, f"Enemy Health: {int(self.enemy.current_health)}%", 
                 (frame_width - 400, stats_y), font_scale=1.0, thickness=2, color=(0, 0, 255))
        
        return frame
    
    def render_game_over(self, frame: np.ndarray):
        """Render game over screen with winner."""
        frame = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        frame_width, frame_height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        
        # Dark overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.2, overlay, 0.8, 0)
        
        # Game Over text
        game_over_text = "GAME OVER"
        text_size = cv2.getTextSize(game_over_text, cv2.FONT_HERSHEY_SIMPLEX, 3.5, 7)[0]
        text_x = (frame_width - text_size[0]) // 2
        draw_text(frame, game_over_text, (text_x, 150), font_scale=3.5, thickness=7, color=(255, 255, 255))
        
        # Winner announcement
        if self.winner == "PLAYER":
            winner_text = "YOU WIN!"
            winner_color = (0, 255, 0)
        elif self.winner == "ENEMY":
            winner_text = "YOU LOSE!"
            winner_color = (0, 0, 255)
        else:
            winner_text = "DRAW!"
            winner_color = (255, 255, 0)
        
        winner_size = cv2.getTextSize(winner_text, cv2.FONT_HERSHEY_SIMPLEX, 4.0, 8)[0]
        winner_x = (frame_width - winner_size[0]) // 2
        draw_text(frame, winner_text, (winner_x, frame_height // 2), font_scale=4.0, thickness=8, color=winner_color)
        
        # Final stats
        stats_y = frame_height // 2 + 150
        draw_text(frame, "FINAL STATS:", (frame_width // 2 - 150, stats_y), 
                 font_scale=1.5, thickness=3, color=(255, 255, 255))
        
        stats_y += 80
        draw_text(frame, f"Player Health: {int(self.player.current_health)}%", 
                 (frame_width // 2 - 200, stats_y), font_scale=1.2, thickness=2, color=(0, 255, 0))
        
        stats_y += 60
        draw_text(frame, f"Enemy Health: {int(self.enemy.current_health)}%", 
                 (frame_width // 2 - 200, stats_y), font_scale=1.2, thickness=2, color=(0, 0, 255))
        
        stats_y += 60
        player_stats = self.player.get_stats()
        draw_text(frame, f"Your Accuracy: {player_stats['accuracy']:.1f}%", 
                 (frame_width // 2 - 200, stats_y), font_scale=1.0, thickness=2, color=(255, 255, 255))
        
        # Instructions
        stats_y += 100
        draw_text(frame, "Press SPACE to play again | Q to quit", 
                 (frame_width // 2 - 350, stats_y), font_scale=1.0, thickness=2, color=(200, 200, 200))
        
        return frame
    
    def run(self):
        """Main game loop."""
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Read frame
            success, frame = self.camera.read_frame()
            if not success:
                continue
            
            # Process with MediaPipe (always process for landmarks)
            rgb_frame = self.camera.get_rgb_frame(frame)
            self.mediapipe.process_frame(rgb_frame)
            
            # Update and render based on state
            if self.state == GameState.MENU:
                frame = self.render_menu(frame)
            elif self.state == GameState.ROUND_SPLASH:
                self.update_game(dt)  # Update for splash timer
                frame = self.render_splash(frame)
            elif self.state == GameState.REST:
                self.update_game(dt)  # Update for rest timer
                frame = self.render_rest(frame)
            elif self.state == GameState.PLAYING:
                self.update_game(dt)
                frame = self.render_game(frame)
            elif self.state == GameState.GAME_OVER:
                frame = self.render_game_over(frame)
            
            # Display
            cv2.imshow("Shadow Boxing Game", frame)
            
            # Handle input
            key = cv2.waitKey(1) & 0xFF
            if key == config.KEY_QUIT or key == ord('q'):
                self.running = False
            elif key == config.KEY_START:
                if self.state == GameState.MENU:
                    self.start_game()
                elif self.state == GameState.GAME_OVER:
                    # Restart game
                    self.state = GameState.MENU
            elif key == config.KEY_PAUSE:
                self.toggle_pause()
        
        self.cleanup()
    
    def start_game(self):
        """Start new game."""
        print("Starting game...")
        self.current_round = 1
        self.player.reset_health()
        self.enemy.reset_health()
        self.round_time_remaining = config.ROUND_DURATION
        self.phase_start_time = time.time()
        self.phase = PhaseState.PLAYER_ATTACK
        
        # Play round sound and show splash
        self.audio.play_round_sound(1)
        self.state = GameState.ROUND_SPLASH
        self.splash_time_remaining = config.SPLASH_DURATION
        self.splash_start_time = time.time()
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
    
    def cleanup(self):
        """Cleanup resources."""
        self.camera.release()
        self.mediapipe.close()
        self.audio.cleanup()
        cv2.destroyAllWindows()

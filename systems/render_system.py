import cv2
import numpy as np
import pygame
import os
import time
import math
from core import constants
import mediapipe as mp

class RenderSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.screen = None
        self._initialize_display()
        
        # Load assets with error handling
        self._load_assets()
        
        # Font initialization
        self.font_path = os.path.join(self.config.FONT_DIR, "PressStart2P.ttf")
        self.font = {
            'large': self._load_font(72),
            'medium': self._load_font(48),
            'small': self._load_font(32),
            'timer': self._load_font(96)
        }
        
        # VFX particles
        self.particles = []
    
    def _initialize_display(self):
        """Initialize pygame display"""
        pygame.init()
        # Use DOUBLEBUF for better performance
        flags = pygame.DOUBLEBUF
        if self.config.FULLSCREEN:
            flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), flags)
        else:
            self.screen = pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Shadow Boxing")
    
    def _load_assets(self):
        """Load critical visual assets only, defer non-critical assets"""
        
        # Load only critical assets at startup
        self.helm_image = self._load_asset("boxing-helm.png", (120, 120))
        self.ko_sprite = self._load_asset("ko.png", (500, 300))  # KO sprite for knockout effect
        
        # Lazy load flags for non-critical assets
        self._punch_bags_loaded = False
        self._attack_assets_loaded = False
        
        # Placeholders
        self.punch_bag_red = None
        self.punch_bag_blue = None
        self.punch_bag_black = None
        self.glove_image = None
        self.target_icon = None
    
    def _ensure_punch_bags_loaded(self):
        """Lazy load punch bag assets when needed"""
        if not self._punch_bags_loaded:
            self.punch_bag_red = self._load_asset("punch-bag-red.png", (150, 180))
            self.punch_bag_blue = self._load_asset("punch-bag-blue.png", (150, 180))
            self.punch_bag_black = self._load_asset("punch-bag-black.png", (150, 180))
            
            # Ensure we have at least placeholder images
            if self.punch_bag_red is None:
                self.punch_bag_red = self._create_placeholder_bag((150, 180), (0, 0, 255))
            if self.punch_bag_blue is None:
                self.punch_bag_blue = self._create_placeholder_bag((150, 180), (255, 0, 0))
            if self.punch_bag_black is None:
                self.punch_bag_black = self._create_placeholder_bag((150, 180), (50, 50, 50))
            
            self._punch_bags_loaded = True
    
    def _ensure_attack_assets_loaded(self):
        """Lazy load attack assets when needed"""
        if not self._attack_assets_loaded:
            self.glove_image = self._load_asset("boxing_glove.png", (80, 80))
            self.target_icon = self._load_asset("target-icon.png", (60, 60))
            self._attack_assets_loaded = True
    
    def _load_asset(self, filename, size=None):
        """Load asset with proper alpha channel handling"""
        asset_path = os.path.join(self.config.SPRITES_DIR, filename)
        if not os.path.exists(asset_path):
            print(f"Warning: Asset not found at {asset_path}")
            return None
        
        try:
            # Load with alpha channel
            img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Warning: Failed to load image at {asset_path}")
                return None
            
            # Ensure image has 4 channels (RGBA)
            if img.shape[2] == 3:  # BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            elif img.shape[2] == 4:  # BGRA
                pass
            else:
                print(f"Warning: Unsupported image format for {filename}")
                return None
            
            if size:
                img = cv2.resize(img, size)
            return img
        except Exception as e:
            print(f"Error loading {asset_path}: {str(e)}")
            return None
    
    def _create_placeholder_bag(self, size, color):
        """Create placeholder punch bag if asset missing"""
        width, height = size
        bag = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Draw bag body (ellipse)
        center = (width//2, height//2)
        axes = (width//2 - 10, height//2 - 20)
        cv2.ellipse(bag, center, axes, 0, 0, 360, (*color, 255), -1)
        cv2.ellipse(bag, center, axes, 0, 0, 360, (255, 255, 255, 255), 2)
        
        # Draw chain
        chain_top = (width//2, 20)
        chain_bottom = (width//2, height//3)
        cv2.line(bag, chain_top, chain_bottom, (200, 200, 200, 255), 3)
        
        # Add shine effect
        shine_center = (width//2 + 30, height//2 - 20)
        cv2.ellipse(bag, shine_center, (15, 20), 0, 0, 360, (255, 255, 255, 100), -1)
        
        return bag
    
    def _load_font(self, size):
        """Load font with fallback"""
        try:
            if os.path.exists(self.font_path):
                return pygame.font.Font(self.font_path, size)
            else:
                print(f"Warning: Font not found at {self.font_path}, using default")
                return pygame.font.SysFont("Arial", size)
        except:
            print(f"Warning: Failed to load font, using default")
            return pygame.font.SysFont("Arial", size)
    
    def render_frame(self, frame, game_state):
        """Main render function - NO pygame.display.flip() here"""
        # Draw hand skeletons on camera frame BEFORE converting to pygame
        if hasattr(game_state, 'hand_results'):
            frame = self._draw_hand_skeletons(frame, game_state.hand_results)
        
        # Convert OpenCV frame (BGR) to Pygame surface (RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb)
        frame_surface = pygame.transform.rotate(frame_surface, -90)
        frame_surface = pygame.transform.flip(frame_surface, True, False)
        frame_surface = pygame.transform.scale(frame_surface, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        
        # Draw base frame
        self.screen.blit(frame_surface, (0, 0))
        
        # Render game elements based on state
        if game_state.current_state == constants.GAME_STATES['PLAYING']:
            self._render_playing_state(game_state)
            # Render KO effect if active
            if hasattr(game_state, 'ko_effect_active') and game_state.ko_effect_active:
                self._render_ko_effect(game_state)
        elif game_state.current_state == constants.GAME_STATES['ROUND_SPLASH']:
            # Handled by FightOverlay
            pass
        elif game_state.current_state == constants.GAME_STATES['REST']:
            # Render helm BEFORE rest period overlay so text appears in front
            if hasattr(game_state, 'face_results') or hasattr(game_state, 'pose_results'):
                face_results = getattr(game_state, 'face_results', None)
                pose_results = getattr(game_state, 'pose_results', None)
                self._render_player_helm(game_state.face_bbox, face_results, pose_results)
            self._render_rest_period(game_state)
        elif game_state.current_state == constants.GAME_STATES['GAME_OVER']:
            # GAME_OVER rendering handled by result_screen in main.py
            # No rendering here to avoid double rendering
            pass
        elif game_state.current_state == constants.GAME_STATES['MENU']:
            # Render helm in menu as well
            if hasattr(game_state, 'face_bbox') and hasattr(game_state, 'face_results'):
                face_results = getattr(game_state, 'face_results', None)
                pose_results = getattr(game_state, 'pose_results', None)
                self._render_player_helm(game_state.face_bbox, face_results, pose_results)
        
        # DO NOT call pygame.display.flip() here - done in main loop
        # HUD rendering is handled by HUDRenderer in main.py
    
    def _render_playing_state(self, game_state):
        """Render during active gameplay"""
        # Render player helm if face detected (with fallback to pose landmarks)
        if hasattr(game_state, 'face_results') or hasattr(game_state, 'pose_results'):
            face_results = getattr(game_state, 'face_results', None)
            pose_results = getattr(game_state, 'pose_results', None)
            self._render_player_helm(game_state.face_bbox, face_results, pose_results)
        
        # Render based on phase
        if game_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            # Render hit boxes with circle backgrounds
            self._render_hitboxes(game_state)
        elif game_state.phase in [constants.PHASE_STATES['ENEMY_ATTACK_WARNING'], 
                                  constants.PHASE_STATES['ENEMY_ATTACK']]:
            # Render enemy attack (target icon + glove animation)
            self._render_enemy_attack(game_state)
        
        # Render VFX particles
        self._render_particles()
    
    def _draw_hand_skeletons(self, frame, hand_results):
        """Draw hand skeleton lines on camera frame"""
        if not hand_results or not hand_results.multi_hand_landmarks:
            return frame
        
        # Hand connections (MediaPipe hand skeleton)
        HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm connections
        ]
        
        h, w, _ = frame.shape
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Draw connections (lines)
            for connection in HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = hand_landmarks.landmark[start_idx]
                end_point = hand_landmarks.landmark[end_idx]
                
                start_x = int(start_point.x * w)
                start_y = int(start_point.y * h)
                end_x = int(end_point.x * w)
                end_y = int(end_point.y * h)
                
                # Draw line (cyan color for visibility)
                cv2.line(frame, (start_x, start_y), (end_x, end_y), (255, 255, 0), 2)
            
            # Draw landmarks (circles)
            for idx, landmark in enumerate(hand_landmarks.landmark):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                
                # Different colors for different landmarks
                if idx == 0:  # Wrist
                    color = (0, 255, 0)  # Green
                    radius = 5
                elif idx == 9:  # Middle finger MCP (for defense)
                    color = (0, 0, 255)  # Red
                    radius = 6
                else:
                    color = (255, 255, 0)  # Cyan
                    radius = 3
                
                cv2.circle(frame, (x, y), radius, color, -1)
        
        return frame
    
    def _render_player_helm(self, face_bbox, face_results=None, pose_results=None):
        """Render boxing helm following face mesh with proper coverage"""
        if self.helm_image is None:
            return
        
        helm_x = None
        helm_y = None
        helm_size = (120, 120)
        
        # Try to get position from face mesh first - USE OUTER BOUNDARY
        if face_results and face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            
            # Get ALL landmarks to find outer boundary
            all_xs = [lm.x * self.config.CAMERA_WIDTH for lm in landmarks]
            all_ys = [lm.y * self.config.CAMERA_HEIGHT for lm in landmarks]
            
            # Calculate bounding box from outer landmarks
            min_x, max_x = min(all_xs), max(all_xs)
            min_y, max_y = min(all_ys), max(all_ys)
            
            face_width = int(max_x - min_x)
            face_height = int(max_y - min_y)
            
            # Center position
            center_x = int((min_x + max_x) / 2)
            center_y = int((min_y + max_y) / 2)
            
            # Scale helm to proper size (1.2x for comfortable boxing helm coverage)
            helm_width = max(100, int(face_width * 1.3))
            helm_height = max(100, int(face_height * 1.3))
            helm_size = (helm_width, helm_height)
            
            # Position helm centered on face center, moved up by 40px
            helm_x = center_x - helm_width // 2
            helm_y = center_y - helm_height // 2 - 40  # Tarik ke atas 40px
        
        # Fallback to body pose landmarks if face mesh not detected
        elif pose_results and pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            # Use nose landmark (index 0) from pose
            nose = landmarks[0]
            if nose.visibility > 0.5:  # Check if landmark is visible
                center_x = int(nose.x * self.config.CAMERA_WIDTH)
                center_y = int(nose.y * self.config.CAMERA_HEIGHT)
                helm_x = center_x - helm_size[0] // 2
                helm_y = center_y - helm_size[1] // 2
        
        # Fallback to face bbox if available
        elif face_bbox is not None:
            x, y, w, h = face_bbox
            helm_x = x + w // 2 - helm_size[0] // 2
            helm_y = y + h // 2 - helm_size[1] // 2
        
        # Render helm if position determined
        if helm_x is not None and helm_y is not None:
            try:
                # Convert coordinates to screen space
                screen_x = int(helm_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                screen_y = int(helm_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                screen_w = int(helm_size[0] * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                screen_h = int(helm_size[1] * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                
                # Resize and convert helm image
                helm_resized = cv2.resize(self.helm_image, helm_size)
                helm_rgba = cv2.cvtColor(helm_resized, cv2.COLOR_BGRA2RGBA)
                helm_surface = pygame.image.frombuffer(helm_rgba.tobytes(), helm_size, "RGBA")
                helm_surface = pygame.transform.scale(helm_surface, (screen_w, screen_h))
                
                self.screen.blit(helm_surface, (screen_x, screen_y))
            except Exception as e:
                pass  # Silently fail if helm rendering fails

    def _add_debug_overlay(self, frame, hand_results, face_results, pose_results):
        """Add debug visualization on frame - ONLY HAND LANDMARKS"""
        # FPS counter
        cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # MediaPipe status
        if self.last_error:
            cv2.putText(frame, self.last_error, (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "MediaPipe: OK", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # ONLY DRAW HAND LANDMARKS (No face/pose)
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Draw landmarks with connections
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
        
        # Add debug status text
        if hand_results and hand_results.multi_hand_landmarks:
            cv2.putText(frame, f"Hands: {len(hand_results.multi_hand_landmarks)}", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Hands: 0", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def _render_player_attack_phase(self, game_state):
        """Render hitboxes as punch bags during player attack phase"""
        current_time = time.time()
        
        for i, hitbox in enumerate(game_state.active_hitboxes):
            x, y, w, h = hitbox
            
            # Convert to screen coordinates
            screen_x = int(x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            screen_y = int(y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            screen_w = int(w * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            screen_h = int(h * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            
            # Calculate center position for punch bag
            center_x = screen_x + screen_w // 2
            center_y = screen_y + screen_h // 2
            
            # Select punch bag image based on hit status
            if hitbox in game_state.hit_hitboxes:
                bag_image = self.punch_bag_blue  # Blue for hit
                alpha = 200  # Slightly transparent when hit
                glow_color = (0, 255, 255)  # Cyan for hit
            else:
                # Alternate colors for visual interest
                if i % 3 == 0:
                    bag_image = self.punch_bag_red
                elif i % 3 == 1:
                    bag_image = self.punch_bag_black
                else:
                    bag_image = self.punch_bag_blue
                alpha = 255
                glow_color = (255, 0, 0)  # Red for active
            
            # Skip if image not loaded
            if bag_image is None:
                continue
            
            # Get bag dimensions
            bag_height, bag_width = bag_image.shape[:2]
            
            # Calculate position (center the punch bag on hitbox)
            bag_x = center_x - bag_width // 2
            bag_y = center_y - bag_height // 2
            
            try:
                # Convert to Pygame surface
                bag_surface = pygame.image.frombuffer(
                    cv2.cvtColor(bag_image, cv2.COLOR_BGRA2RGBA).tobytes(),
                    bag_image.shape[1::-1],
                    "RGBA"
                )
                bag_surface.set_alpha(alpha)
                
                # Add pulse effect for unhitted bags
                if hitbox not in game_state.hit_hitboxes:
                    pulse_time = (current_time * 2) % 1
                    scale = 1.0 + 0.1 * abs(2 * pulse_time - 1)
                    bag_surface = pygame.transform.scale(
                        bag_surface, 
                        (int(bag_surface.get_width() * scale), int(bag_surface.get_height() * scale))
                    )
                
                self.screen.blit(bag_surface, (bag_x, bag_y))
            except Exception as e:
                print(f"Error rendering punch bag: {str(e)}")
                # Fallback to colored rectangle
                color = glow_color if hitbox not in game_state.hit_hitboxes else (0, 255, 255)
                pygame.draw.rect(self.screen, color, (bag_x, bag_y, bag_width, bag_height), border_radius=20)
    
    def _render_rest_period(self, game_state):
        """Render rest period UI"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 100, 180))
        self.screen.blit(overlay, (0, 0))
        
        rest_text = self.font['large'].render("REST PERIOD", True, (255, 255, 255))
        timer_text = self.font['medium'].render(f"Next round in: {int(game_state.rest_timer)}s", True, (255, 255, 0))
        
        self.screen.blit(rest_text, rest_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 30)))
        self.screen.blit(timer_text, timer_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 30)))
    
    def _render_ko_effect(self, game_state):
        """Render KO effect with ko.png sprite animation"""
        import time
        
        # Calculate animation progress (0.0 to 1.0)
        elapsed = time.time() - game_state.ko_start_time
        progress = min(1.0, elapsed / game_state.ko_duration)
        
        # Semi-transparent red overlay for dramatic effect
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = int(150 * progress)  # Lighter fade to 150 alpha
        overlay.fill((100, 0, 0, alpha))  # Red tint instead of black
        self.screen.blit(overlay, (0, 0))
        
        # Use ko.png sprite if available, otherwise fallback to text
        if self.ko_sprite is not None:
            # Cache scaled sprites for better performance
            if not hasattr(self, '_ko_sprite_cache'):
                self._ko_sprite_cache = {}
            
            # Pulsing scale effect for KO sprite (simplified for performance)
            pulse_scale = 1.0 + 0.15 * abs(math.sin(elapsed * 3))  # Reduced pulse range
            
            # Calculate size with pulse - LARGER base size for better visibility
            base_width = 600
            base_height = 360
            sprite_width = int(base_width * pulse_scale)
            sprite_height = int(base_height * pulse_scale)
            
            # Use cached sprite if size matches, otherwise resize
            cache_key = f"{sprite_width}x{sprite_height}"
            if cache_key not in self._ko_sprite_cache:
                try:
                    ko_surface = cv2.resize(self.ko_sprite, (sprite_width, sprite_height), interpolation=cv2.INTER_LINEAR)
                    ko_rgba = cv2.cvtColor(ko_surface, cv2.COLOR_BGRA2RGBA)
                    self._ko_sprite_cache[cache_key] = pygame.image.frombuffer(ko_rgba.tobytes(), (sprite_width, sprite_height), "RGBA")
                except Exception:
                    pass
                    self._render_ko_text_fallback(elapsed, progress)
                    return
            
            try:
                ko_pygame = self._ko_sprite_cache[cache_key]
                
                # Slight shake effect in first 0.5 seconds
                shake_x = int(15 * math.sin(elapsed * 20)) if progress < 0.2 else 0
                shake_y = int(15 * math.cos(elapsed * 20)) if progress < 0.2 else 0
                
                # Center position with shake
                sprite_x = (self.config.WINDOW_WIDTH - sprite_width) // 2 + shake_x
                sprite_y = (self.config.WINDOW_HEIGHT - sprite_height) // 2 + shake_y
                
                # Apply fade in alpha to sprite - FULL opacity for visibility
                sprite_alpha = 255  # Always full opacity
                ko_pygame.set_alpha(sprite_alpha)
                
                # Add white flash effect in first 0.3 seconds for impact
                if progress < 0.3:
                    flash_alpha = int(200 * (1.0 - progress / 0.3))  # Fade from 200 to 0
                    flash_overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
                    flash_overlay.fill((255, 255, 255, flash_alpha))
                    self.screen.blit(flash_overlay, (0, 0))
                
                self.screen.blit(ko_pygame, (sprite_x, sprite_y))
            except Exception:
                pass
                # Fallback to text if sprite fails
                self._render_ko_text_fallback(elapsed, progress)
        else:
            # Fallback to text rendering
            self._render_ko_text_fallback(elapsed, progress)
    
    def _render_ko_text_fallback(self, elapsed, progress):
        """Fallback text rendering for KO effect"""
        # KO text with pulsing scale effect
        pulse_scale = 1.0 + 0.3 * abs(math.sin(elapsed * 3))  # Pulse between 1.0 and 1.3
        ko_size = int(200 * pulse_scale)
        
        try:
            ko_font = pygame.font.Font(self.font_path, ko_size)
        except:
            ko_font = pygame.font.SysFont("Arial", ko_size, bold=True)
        
        # Gradient effect: red to orange
        color_phase = (elapsed * 2) % 1.0
        red = 255
        green = int(100 + 155 * color_phase)
        ko_color = (red, green, 0)
        
        ko_text = ko_font.render("K.O.", True, ko_color)
        
        # Slight shake effect
        shake_x = int(10 * math.sin(elapsed * 15)) if progress < 0.5 else 0
        shake_y = int(10 * math.cos(elapsed * 15)) if progress < 0.5 else 0
        
        ko_rect = ko_text.get_rect(center=(
            self.config.WINDOW_WIDTH // 2 + shake_x,
            self.config.WINDOW_HEIGHT // 2 + shake_y
        ))
        
        # Shadow effect
        shadow_offset = 5
        shadow_text = ko_font.render("K.O.", True, (50, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(ko_rect.centerx + shadow_offset, ko_rect.centery + shadow_offset))
        self.screen.blit(shadow_text, shadow_rect)
        
        # Main text
        self.screen.blit(ko_text, ko_rect)
    
    def _render_game_over(self, game_state):
        """Render game over screen"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        if game_state.player_health <= 0:
            result_text = "YOU LOSE!"
            color = (255, 0, 0)
        else:
            result_text = "YOU WIN!"
            color = (0, 255, 0)
        
        title = self.font['large'].render(result_text, True, color)
        score = self.font['medium'].render(f"Final Score: {game_state.score}", True, (255, 255, 255))
        restart = self.font['small'].render("Press Enter to restart", True, (200, 200, 200))
        
        self.screen.blit(title, title.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 60)))
        self.screen.blit(score, score.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 20)))
        self.screen.blit(restart, restart.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 50)))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def _render_particles(self):
        """Render and update VFX particles"""
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['life'] -= 0.05
            particle['size'] *= 0.95
            
            if particle['life'] <= 0 or particle['size'] <= 0.5:
                self.particles.remove(particle)
                continue
            
            # Draw particle
            alpha = int(255 * particle['life'])
            size = int(particle['size'])
            color = (*particle['color'], alpha)
            
            try:
                particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (size, size), size)
                self.screen.blit(particle_surface, (int(particle['pos'][0] - size), int(particle['pos'][1] - size)))
            except:
                pass
    
    def _render_hitboxes(self, game_state):
        """Render punch bags dengan circle background 130x130px"""
        if not hasattr(game_state, 'hitbox_system'):
            return
        
        # Lazy load punch bag assets
        self._ensure_punch_bags_loaded()
        
        hitboxes = game_state.hitbox_system.get_all_hitboxes()
        current_time = time.time()
        
        for hitbox in hitboxes:
            x, y = hitbox['x'], hitbox['y']
            size = hitbox['width']
            radius = hitbox['radius']
            center_x, center_y = hitbox['center_x'], hitbox['center_y']
            is_active = hitbox['active']
            hit_time = hitbox['hit_time']
            bag_type = hitbox['type']
            
            # Convert to screen coordinates
            screen_center_x = int(center_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            screen_center_y = int(center_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            screen_radius = int(radius * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            
            # Draw circle background
            if is_active:
                pulse = math.sin(current_time * 3) * 0.1 + 0.9
                circle_color = (int(255 * pulse), int(50 * pulse), int(50 * pulse))
                circle_width = 3
            else:
                elapsed = current_time - hit_time
                fade = max(0, 1 - elapsed * 2)
                circle_color = (0, int(255 * fade), 0)
                circle_width = 2
            
            pygame.draw.circle(self.screen, circle_color, 
                              (screen_center_x, screen_center_y), 
                              screen_radius, circle_width)
            
            # Select punch bag
            if bag_type == 'red':
                bag_image = self.punch_bag_red
            elif bag_type == 'blue':
                bag_image = self.punch_bag_blue
            else:
                bag_image = self.punch_bag_black
            
            if bag_image is None:
                continue
            
            # Render punch bag
            bag_size = int(screen_radius * 1.5)
            bag_x = screen_center_x - bag_size // 2
            bag_y = screen_center_y - bag_size // 2
            
            try:
                bag_resized = cv2.resize(bag_image, (bag_size, bag_size))
                bag_rgba = cv2.cvtColor(bag_resized, cv2.COLOR_BGRA2RGBA)
                bag_surface = pygame.image.frombuffer(bag_rgba.tobytes(), (bag_size, bag_size), "RGBA")
                
                if not is_active:
                    elapsed = current_time - hit_time
                    alpha = max(0, 255 - int(elapsed * 500))
                    bag_surface.set_alpha(alpha)
                
                self.screen.blit(bag_surface, (bag_x, bag_y))
            except:
                pygame.draw.circle(self.screen, circle_color, 
                                  (screen_center_x, screen_center_y), 
                                  screen_radius // 2, 0)
    
    def _render_enemy_attack(self, game_state):
        """Render enemy attack dengan target icon dan glove animation"""
        # Lazy load attack assets
        self._ensure_attack_assets_loaded()
        
        if not hasattr(game_state, 'enemy_attack_system'):
            return
        
        attack_system = game_state.enemy_attack_system
        
        # Check if attack system is active (warning or attacking)
        if not attack_system.is_active():
            return
        
        # Render target icon during warning phase
        if attack_system.is_warning:
            target_pos = attack_system.get_target_position()
            if target_pos:
                target_x, target_y = target_pos
                screen_x = int(target_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                screen_y = int(target_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                
                # Draw crosshair target
                size = 40 + int(math.sin(time.time() * 5) * 5)
                pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), size, 3)
                pygame.draw.line(self.screen, (255, 0, 0), 
                               (screen_x - size - 10, screen_y), (screen_x + size + 10, screen_y), 3)
                pygame.draw.line(self.screen, (255, 0, 0), 
                               (screen_x, screen_y - size - 10), (screen_x, screen_y + size + 10), 3)
        
        # Render glove animation during attack phase
        if attack_system.is_attacking:
            glove_pos = attack_system.get_glove_position()
            target_pos = attack_system.get_target_position()
            
            if glove_pos and target_pos:
                glove_x, glove_y = glove_pos
                target_x, target_y = target_pos
                
                # Convert to screen coordinates
                screen_glove_x = int(glove_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                screen_glove_y = int(glove_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                screen_target_x = int(target_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                screen_target_y = int(target_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                
                if self.glove_image is not None:
                    try:
                        glove_size = 120
                        glove_resized = cv2.resize(self.glove_image, (glove_size, glove_size))
                        glove_rgba = cv2.cvtColor(glove_resized, cv2.COLOR_BGRA2RGBA)
                        glove_surface = pygame.image.frombuffer(glove_rgba.tobytes(), (glove_size, glove_size), "RGBA")
                        
                        # Motion trail
                        progress = attack_system.glove_progress
                        if progress < 0.8:
                            for i in range(3):
                                trail_progress = max(0, progress - (i + 1) * 0.1)
                                trail_x = int(glove_x + (target_x - glove_x) * trail_progress)
                                trail_y = int(glove_y + (target_y - glove_y) * trail_progress)
                                trail_screen_x = int(trail_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
                                trail_screen_y = int(trail_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
                                
                                trail_surface = glove_surface.copy()
                                trail_surface.set_alpha(100 - i * 30)
                                self.screen.blit(trail_surface, (trail_screen_x - glove_size // 2, trail_screen_y - glove_size // 2))
                        
                        self.screen.blit(glove_surface, (screen_glove_x - glove_size // 2, screen_glove_y - glove_size // 2))
                        
                        # Also draw target crosshair during attack
                        size = 30
                        pygame.draw.circle(self.screen, (255, 100, 100), (screen_target_x, screen_target_y), size, 2)
                        pygame.draw.line(self.screen, (255, 100, 100), 
                                       (screen_target_x - size - 5, screen_target_y), (screen_target_x + size + 5, screen_target_y), 2)
                        pygame.draw.line(self.screen, (255, 100, 100), 
                                       (screen_target_x, screen_target_y - size - 5), (screen_target_x, screen_target_y + size + 5), 2)
                    except Exception as e:
                        # Fallback: draw red circle
                        pygame.draw.circle(self.screen, (200, 0, 0), (screen_glove_x, screen_glove_y), 30, 0)
                else:
                    # Fallback: draw red circle
                    pygame.draw.circle(self.screen, (200, 0, 0), (screen_glove_x, screen_glove_y), 30, 0)
    
    def close(self):
        """Clean up resources"""
        pygame.quit()
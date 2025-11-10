import cv2
import numpy as np
import pygame
import os
from core import config, utils, constants
from core.math_utils import distance
import random
import time

class RenderSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.screen = None
        self._initialize_display()
        
        # Load assets
        self.helm_image = utils.load_image(os.path.join(self.config.SPRITES_DIR, "boxing-helm.png"), (120, 120))
        self.glove_image = utils.load_image(os.path.join(self.config.SPRITES_DIR, "boxing_glove.png"), (80, 80))
        self.target_icon = utils.load_image(os.path.join(self.config.SPRITES_DIR, "target-icon.png"), (60, 60))
        self.fight_overlay = utils.load_image(os.path.join(self.config.SPRITES_DIR, "fight.png"), (300, 200))
        
        # Font initialization
        self.font_path = os.path.join(self.config.FONT_DIR, "daydream.otf")
        self.fonts = {
            'large': self._load_font(72),
            'medium': self._load_font(48),
            'small': self._load_font(32)
        }
        
        # VFX particles
        self.particles = []
    
    def _initialize_display(self):
        """Initialize pygame display"""
        pygame.init()
        if self.config.FULLSCREEN:
            self.screen = pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        pygame.display.set_caption("Shadow Boxing")
    
    def _load_font(self, size):
        """Load font with fallback"""
        try:
            return pygame.font.Font(self.font_path, size)
        except:
            print(f"Warning: Failed to load font at {self.font_path}, using default font")
            return pygame.font.SysFont("Arial", size)
    
    def render_frame(self, frame, game_state):
        """Main render function"""
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
        elif game_state.current_state == constants.GAME_STATES['ROUND_SPLASH']:
            self._render_round_splash(game_state)
        elif game_state.current_state == constants.GAME_STATES['REST']:
            self._render_rest_period(game_state)
        elif game_state.current_state == constants.GAME_STATES['GAME_OVER']:
            self._render_game_over(game_state)
        elif game_state.current_state == constants.GAME_STATES['MENU']:
            self._render_menu(game_state)
        
        # Render UI elements (always visible during gameplay)
        if game_state.current_state in [constants.GAME_STATES['PLAYING'], constants.GAME_STATES['ROUND_SPLASH']]:
            self._render_hud(game_state)
        
        # Update display
        pygame.display.flip()
    
    def _render_playing_state(self, game_state):
        """Render during active gameplay"""
        # Render player helm if face detected
        if game_state.face_bbox:
            self._render_player_helm(game_state.face_bbox)
        
        # Render enemy attack phase
        if game_state.phase == constants.PHASE_STATES['ENEMY_ATTACK']:
            self._render_enemy_attack(game_state)
        
        # Render player attack phase (hitboxes)
        if game_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
            self._render_player_attack_phase(game_state)
        
        # Render VFX particles
        self._render_particles()
    
    def _render_player_helm(self, face_bbox):
        """Render boxing helm on player's head"""
        x, y, w, h = face_bbox
        helm_x = x - 20  # Adjust position
        helm_y = y - 60  # Above the face
        
        # Convert to Pygame coordinates
        helm_x = int(helm_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        helm_y = int(helm_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
        
        # Create Pygame surface from OpenCV image
        helm_surface = pygame.surfarray.make_surface(cv2.cvtColor(self.helm_image, cv2.COLOR_BGRA2RGBA))
        self.screen.blit(helm_surface, (helm_x, helm_y))
    
    def _render_enemy_attack(self, game_state):
        """Render enemy glove flying toward target"""
        # Get target position (nose landmark)
        if game_state.enemy_target:
            target_x, target_y = game_state.enemy_target
            
            # Convert to screen coordinates
            target_x = int(target_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            target_y = int(target_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            
            # Render target icon
            target_surface = pygame.surfarray.make_surface(cv2.cvtColor(self.target_icon, cv2.COLOR_BGRA2RGBA))
            self.screen.blit(target_surface, (target_x - 30, target_y - 30))
            
            # Render flying glove
            if game_state.glove_position:
                glove_x, glove_y = game_state.glove_position
                
                # Interpolate position based on attack progress
                progress = min(1.0, game_state.attack_progress)
                current_x = int(glove_x + (target_x - glove_x) * progress)
                current_y = int(glove_y + (target_y - glove_y) * progress)
                
                # Scale glove based on distance
                scale = 1.0 - progress * 0.5
                scaled_glove = pygame.transform.scale(
                    pygame.surfarray.make_surface(cv2.cvtColor(self.glove_image, cv2.COLOR_BGRA2RGBA)),
                    (int(80 * scale), int(80 * scale))
                )
                
                self.screen.blit(scaled_glove, (current_x - 40, current_y - 40))
                
                # Add motion blur particles
                if progress < 0.8:
                    self._add_particles(current_x, current_y, 5, (255, 165, 0))
    
    def _render_player_attack_phase(self, game_state):
        """Render hitboxes during player attack phase"""
        for hitbox in game_state.active_hitboxes:
            x, y, w, h = hitbox
            
            # Convert to screen coordinates
            x = int(x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            y = int(y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            w = int(w * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
            h = int(h * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
            
            # Draw hitbox with glow effect
            color = (0, 255, 0) if hitbox in game_state.hit_hitboxes else (255, 0, 0)
            
            # Outer glow
            for i in range(3):
                alpha = 128 - i * 40
                glow_surface = pygame.Surface((w + i*4, h + i*4), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*color, alpha), (0, 0, w + i*4, h + i*4), border_radius=10)
                self.screen.blit(glow_surface, (x - i*2, y - i*2))
            
            # Inner fill
            pygame.draw.rect(self.screen, (*color, 180), (x, y, w, h), border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), 2, border_radius=10)
    
    def _render_round_splash(self, game_state):
        """Render round splash screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Round text
        round_text = self.fonts['large'].render(f"ROUND {game_state.current_round}", True, (255, 255, 0))
        text_rect = round_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(round_text, text_rect)
        
        # "FIGHT!" text
        fight_surface = pygame.surfarray.make_surface(cv2.cvtColor(self.fight_overlay, cv2.COLOR_BGRA2RGBA))
        fight_rect = fight_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 50))
        self.screen.blit(fight_surface, fight_rect)
    
    def _render_rest_period(self, game_state):
        """Render rest period UI"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 100, 180))
        self.screen.blit(overlay, (0, 0))
        
        rest_text = self.fonts['large'].render("REST PERIOD", True, (255, 255, 255))
        timer_text = self.fonts['medium'].render(f"Next round in: {int(game_state.rest_timer)}s", True, (255, 255, 0))
        
        self.screen.blit(rest_text, rest_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 30)))
        self.screen.blit(timer_text, timer_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 30)))
    
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
        
        title = self.fonts['large'].render(result_text, True, color)
        score = self.fonts['medium'].render(f"Final Score: {game_state.score}", True, (255, 255, 255))
        restart = self.fonts['small'].render("Press SPACE to restart", True, (200, 200, 200))
        
        self.screen.blit(title, title.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 60)))
        self.screen.blit(score, score.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 20)))
        self.screen.blit(restart, restart.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 50)))
    
    def _render_menu(self, game_state):
        """Render main menu"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 220))
        self.screen.blit(overlay, (0, 0))
        
        title = self.fonts['large'].render("SHADOW BOXING", True, (255, 215, 0))
        start = self.fonts['medium'].render("Press SPACE to Start", True, (255, 255, 255))
        difficulty = self.fonts['small'].render(f"Difficulty: {self.config.DEFAULT_DIFFICULTY}", True, (173, 216, 230))
        
        # Draw decorative elements
        pygame.draw.rect(self.screen, (100, 100, 200, 128), (self.config.WINDOW_WIDTH//2 - 300, 100, 600, 500), 2, border_radius=20)
        
        self.screen.blit(title, title.get_rect(center=(self.config.WINDOW_WIDTH//2, 200)))
        self.screen.blit(start, start.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2)))
        self.screen.blit(difficulty, difficulty.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 100)))
    
    def _render_hud(self, game_state):
        """Render heads-up display"""
        # Health bars
        self._draw_health_bar(50, 50, game_state.player_health, constants.PLAYER_MAX_HEALTH, "PLAYER", (0, 100, 255))
        self._draw_health_bar(self.config.WINDOW_WIDTH - 350, 50, game_state.enemy_health, constants.ENEMY_MAX_HEALTH, "ENEMY", (255, 0, 0))
        
        # Timer
        timer_text = self.fonts['medium'].render(f"{int(game_state.round_timer)}", True, (255, 255, 255))
        timer_bg = pygame.Surface((120, 60), pygame.SRCALPHA)
        pygame.draw.rect(timer_bg, (50, 50, 50, 180), (0, 0, 120, 60), border_radius=15)
        self.screen.blit(timer_bg, (self.config.WINDOW_WIDTH//2 - 60, 20))
        self.screen.blit(timer_text, timer_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 50)))
        
        # Combo counter
        if game_state.combo_count > 0:
            combo_text = self.fonts['small'].render(f"COMBO: x{game_state.combo_count}", True, (255, 215, 0))
            self.screen.blit(combo_text, (self.config.WINDOW_WIDTH//2 - combo_text.get_width()//2, 120))
        
        # Phase indicator
        phase_text = {
            constants.PHASE_STATES['PLAYER_ATTACK']: "YOUR TURN - Hit the targets!",
            constants.PHASE_STATES['ENEMY_ATTACK_WARNING']: "ENEMY ATTACKING - DEFEND!",
            constants.PHASE_STATES['ENEMY_ATTACK']: "BLOCK NOW!"
        }.get(game_state.phase, "")
        
        if phase_text:
            phase_surface = pygame.Surface((400, 40), pygame.SRCALPHA)
            pygame.draw.rect(phase_surface, (0, 0, 0, 180), (0, 0, 400, 40), border_radius=10)
            self.screen.blit(phase_surface, (self.config.WINDOW_WIDTH//2 - 200, self.config.WINDOW_HEIGHT - 60))
            
            phase_render = self.fonts['small'].render(phase_text, True, (255, 255, 255))
            self.screen.blit(phase_render, (self.config.WINDOW_WIDTH//2 - phase_render.get_width()//2, self.config.WINDOW_HEIGHT - 50))
    
    def _draw_health_bar(self, x, y, current_health, max_health, label, color):
        """Draw health bar with label"""
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, 300, 30), border_radius=15)
        
        # Health fill
        health_width = int(300 * (current_health / max_health))
        pygame.draw.rect(self.screen, color, (x, y, health_width, 30), border_radius=15)
        
        # Border
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, 300, 30), 2, border_radius=15)
        
        # Label
        label_text = self.fonts['small'].render(f"{label}: {current_health}/{max_health}", True, (255, 255, 255))
        self.screen.blit(label_text, (x + 10, y + 5))
    
    def _add_particles(self, x, y, count, color):
        """Add VFX particles"""
        for _ in range(count):
            self.particles.append({
                'pos': [x + random.uniform(-20, 20), y + random.uniform(-20, 20)],
                'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
                'size': random.uniform(3, 8),
                'color': color,
                'life': 1.0
            })
    
    def _render_particles(self):
        """Render and update VFX particles"""
        current_time = time.time()
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
            
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            self.screen.blit(particle_surface, (int(particle['pos'][0] - size), int(particle['pos'][1] - size)))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    return "SPACE"
        return True
    
    def close(self):
        """Clean up resources"""
        pygame.quit()
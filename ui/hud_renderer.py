from core import config, constants
from core.utils import FontManager
import pygame
import time
import os
import math

class HUDRenderer:
    def __init__(self, game_config, render_system):
        self.config = game_config
        self.render_system = render_system
        self.font_path = self.config.FONT_PATH
        
        # Use FontManager singleton
        self.font_manager = FontManager()
        
        # VFX states
        self.ko_effect_active = False
        self.ko_start_time = 0
        self.fight_effect_active = False
        self.fight_start_time = 0
        
    def _get_font(self, size):
        """Get font using FontManager"""
        return self.font_manager.get_font(self.font_path, size)
    
    def render_hud(self, game_state, screen):
        """Render HUD elements"""
        # Health bars
        self._draw_health_bar(screen, 50, 50, game_state.player_health, constants.PLAYER_MAX_HEALTH, "PLAYER", (0, 100, 255))
        self._draw_health_bar(screen, self.config.WINDOW_WIDTH - 350, 50, game_state.enemy_health, constants.ENEMY_MAX_HEALTH, "ENEMY", (255, 0, 0))
        
        # Timer
        timer_font = self._get_font(48)
        timer_text = timer_font.render(f"{int(game_state.round_timer)}", True, (255, 255, 255))
        timer_bg = pygame.Surface((150, 100), pygame.SRCALPHA)
        pygame.draw.rect(timer_bg, (50, 50, 50, 180), (0, 0, 150, 100), border_radius=20)
        screen.blit(timer_bg, (self.config.WINDOW_WIDTH//2 - 75, 10))
        screen.blit(timer_text, timer_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 60)))
        
        # Combo counter
        if game_state.combo_count > 0:
            combo_font = self._get_font(24)
            combo_text = combo_font.render(f"COMBO x{game_state.combo_count}", True, (255, 215, 0))
            screen.blit(combo_text, (self.config.WINDOW_WIDTH//2 - combo_text.get_width()//2, 150))
        
        # Phase indicator
        phase_text = self._get_phase_text(game_state.phase)
        if phase_text:
            self._draw_phase_indicator(screen, phase_text)
        
        # Score
        score_font = self._get_font(16)
        score_text = score_font.render(f"SCORE {game_state.score}", True, (255, 255, 255))
        screen.blit(score_text, (self.config.WINDOW_WIDTH - score_text.get_width() - 20, self.config.WINDOW_HEIGHT - 40))
    
    def _draw_health_bar(self, screen, x, y, current_health, max_health, label, color):
        """Draw health bar with label"""
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, 300, 40), border_radius=20)
        
        # Health fill
        health_width = int(300 * (current_health / max_health))
        pygame.draw.rect(screen, color, (x, y, health_width, 40), border_radius=20)
        
        # Border
        pygame.draw.rect(screen, (200, 200, 200), (x, y, 300, 40), 2, border_radius=20)
        
        # Label
        label_font = self._get_font(18)
        label_text = label_font.render(f"{label} {current_health} / {max_health}", True, (255, 255, 255))
        screen.blit(label_text, (x + 15, y + 8))
    
    def _get_phase_text(self, phase):
        """Get text for current phase"""
        phase_texts = {
            constants.PHASE_STATES['PLAYER_ATTACK']: "YOUR TURN, Hit the targets!",
            constants.PHASE_STATES['ENEMY_ATTACK_WARNING']: "ENEMY ATTACKING, DEFEND!",
            constants.PHASE_STATES['ENEMY_ATTACK']: "BLOCK NOW!"
        }
        return phase_texts.get(phase, "")
    
    def _draw_phase_indicator(self, screen, text):
        """Draw phase indicator with animation"""
        phase_font = self._get_font(20)
        text_surface = phase_font.render(text, True, (255, 255, 255))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        # Pulsing background
        pulse_time = (time.time() * 3) % 1
        alpha = int(128 + 64 * abs(2 * pulse_time - 1))
        
        bg_surface = pygame.Surface((text_width + 40, text_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, alpha), (0, 0, text_width + 40, text_height + 20), border_radius=15)
        screen.blit(bg_surface, (self.config.WINDOW_WIDTH//2 - bg_surface.get_width()//2, self.config.WINDOW_HEIGHT - 80))
        
        screen.blit(text_surface, (self.config.WINDOW_WIDTH//2 - text_width//2, self.config.WINDOW_HEIGHT - 70))
    
    def show_fight_text(self, screen):
        """Show animated 'FIGHT!' text"""
        self.fight_effect_active = True
        self.fight_start_time = time.time()
    
    def show_ko_text(self, screen, player_won):
        """Show animated 'KO!' text"""
        self.ko_effect_active = True
        self.ko_start_time = time.time()
        self.player_won = player_won
    
    def render_special_effects(self, screen):
        """Render special text effects (FIGHT!, KO!)"""
        current_time = time.time()
        
        # Render FIGHT! effect
        if self.fight_effect_active:
            elapsed = current_time - self.fight_start_time
            if elapsed < 1.5:  # Show for 1.5 seconds
                # Fade in and out
                alpha = 255
                if elapsed < 0.3:
                    alpha = int(255 * (elapsed / 0.3))
                elif elapsed > 1.2:
                    alpha = int(255 * (1 - (elapsed - 1.2) / 0.3))
                
                fight_font = self._get_font(72)
                fight_text = fight_font.render("FIGHT!", True, (255, 215, 0))
                fight_text.set_alpha(alpha)
                
                # Scale effect
                scale = 1.0 + 0.2 * abs(math.sin(elapsed * 10))
                scaled_text = pygame.transform.scale(
                    fight_text, 
                    (int(fight_text.get_width() * scale), int(fight_text.get_height() * scale))
                )
                
                screen.blit(scaled_text, scaled_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2)))
            else:
                self.fight_effect_active = False
        
        # Render KO! effect
        if self.ko_effect_active:
            elapsed = current_time - self.ko_start_time
            if elapsed < 3.0:  # Show for 3 seconds
                # Background shake
                shake_offset = int(5 * math.sin(elapsed * 20))
                
                # Red/black flashing background
                bg_color = (255, 0, 0) if int(elapsed * 5) % 2 == 0 else (0, 0, 0)
                bg_surface = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
                bg_surface.fill(bg_color)
                bg_surface.set_alpha(100)
                screen.blit(bg_surface, (shake_offset, shake_offset))
                
                # KO text
                ko_text = "YOU WIN!" if self.player_won else "YOU LOSE!"
                color = (0, 255, 0) if self.player_won else (255, 0, 0)
                ko_font = self._get_font(72)
                text_surface = ko_font.render(ko_text, True, color)
                
                # Outline effect
                outline_surface = ko_font.render(ko_text, True, (255, 255, 255))
                for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
                    screen.blit(outline_surface, outline_surface.get_rect(center=(self.config.WINDOW_WIDTH//2 + dx, self.config.WINDOW_HEIGHT//2 + dy + shake_offset)))
                
                screen.blit(text_surface, text_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + shake_offset)))
            else:
                self.ko_effect_active = False
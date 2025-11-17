"""Fight overlay - displays round splash screens and FIGHT text."""

import pygame
import time
import math
import os

class FightOverlay:
    def __init__(self, game_config):
        self.config = game_config
        self.active = False
        self.start_time = 0
        self.duration = 2.5  # Total duration: 1.5s round image + 1.0s fight image
        self.phase_duration = 1.5  # Duration for round image
        self.current_round = 1
        
        # Load round images
        self.round_surfaces = {
            1: self._load_round_surface("round-1.png"),
            2: self._load_round_surface("round-2.png"),
            3: self._load_round_surface("final-round.png")
        }
        
        # Load FIGHT image
        self.fight_surface = self._load_round_surface("fight.png")
    
    def _load_round_surface(self, filename):
        """Load round image and convert to Pygame surface"""
        try:
            path = os.path.join(self.config.SPRITES_DIR, filename)
            if not os.path.exists(path):
                print(f"Warning: Round image not found: {path}")
                return self._create_placeholder_surface(filename)
            
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (500, 400))
            return image
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
            return self._create_placeholder_surface(filename)
    
    def _create_placeholder_surface(self, filename):
        """Create placeholder surface if image not found"""
        surface = pygame.Surface((500, 400), pygame.SRCALPHA)
        
        # Different colors for different rounds
        if "round-1" in filename:
            color = (100, 100, 200, 200)
            text = "ROUND 1"
        elif "round-2" in filename:
            color = (100, 200, 100, 200)
            text = "ROUND 2"
        elif "round-3" in filename:
            color = (200, 100, 100, 200)
            text = "ROUND 3"
        elif "fight" in filename.lower():
            color = (200, 50, 50, 200)
            text = "FIGHT!"
        else:
            color = (100, 100, 100, 200)
            text = "READY"
        
        # Draw background
        pygame.draw.rect(surface, color, (0, 0, 500, 400), border_radius=20)
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255, 255), (0, 0, 500, 400), 3, border_radius=20)
        
        # Draw text
        font = pygame.font.Font(None, 80)
        text_surface = font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, text_surface.get_rect(center=(250, 200)))
        
        return surface
    
    def show_round_start(self, round_num):
        """Show round splash screen"""
        self.active = True
        self.start_time = time.time()
        self.current_round = round_num
    
    def is_active(self):
        """Check if overlay is still active"""
        if not self.active:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed < self.duration
    
    def render(self, screen):
        """Render round splash and fight overlay"""
        if not self.active:
            return
        
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            self.active = False
            return
        
        # Create semi-transparent background
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Phase 1: Show round image (first 1.5 seconds)
        if elapsed < self.phase_duration:
            round_surface = self.round_surfaces.get(self.current_round, self.round_surfaces[1])
            if round_surface:
                # Calculate position to center
                x = (self.config.WINDOW_WIDTH - round_surface.get_width()) // 2
                y = (self.config.WINDOW_HEIGHT - round_surface.get_height()) // 2
                
                # Pulse effect
                pulse_time = elapsed * 2
                scale = 1.0 + 0.1 * abs(math.sin(pulse_time * math.pi))
                if scale != 1.0:
                    scaled_surface = pygame.transform.scale(
                        round_surface,
                        (int(round_surface.get_width() * scale), int(round_surface.get_height() * scale))
                    )
                    scaled_rect = scaled_surface.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2))
                    screen.blit(scaled_surface, scaled_rect)
                else:
                    screen.blit(round_surface, (x, y))
        
        # Phase 2: Show FIGHT image (next 1.0 seconds)
        elif self.fight_surface and elapsed < self.duration:
            # Calculate timing within this phase
            phase_time = elapsed - self.phase_duration
            total_phase_time = self.duration - self.phase_duration
            
            # Fade in FIGHT image
            fade_progress = min(1.0, phase_time / 0.3)  # Fade in over 0.3 seconds
            alpha = int(255 * fade_progress)
            
            # Shake effect intensity
            shake_progress = min(1.0, phase_time / 0.5)
            shake_intensity = int(5 * shake_progress)
            
            # Create copy with alpha
            fight_surface = self.fight_surface.copy()
            fight_surface.set_alpha(alpha)
            
            # Calculate position with shake
            base_x = (self.config.WINDOW_WIDTH - fight_surface.get_width()) // 2
            base_y = (self.config.WINDOW_HEIGHT - fight_surface.get_height()) // 2
            shake_offset_x = int(shake_intensity * math.sin(phase_time * 20))
            shake_offset_y = int(shake_intensity * math.cos(phase_time * 20))
            
            # Draw with shake
            screen.blit(fight_surface, (base_x + shake_offset_x, base_y + shake_offset_y))
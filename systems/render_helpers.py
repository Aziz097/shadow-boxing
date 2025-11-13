"""
Render methods untuk Hit Box System dan Enemy Attack System
"""
import pygame
import cv2
import time
import math

def render_hitboxes(self, game_state):
    """Render punch bags dengan circle background 130x130px"""
    if not hasattr(game_state, 'hitbox_system'):
        return
    
    hitboxes = game_state.hitbox_system.get_all_hitboxes()
    current_time = time.time()
    
    for hitbox in hitboxes:
        # Get hitbox properties
        x, y = hitbox['x'], hitbox['y']
        size = hitbox['width']  # 130px
        radius = hitbox['radius']  # 65px
        center_x, center_y = hitbox['center_x'], hitbox['center_y']
        is_active = hitbox['active']
        hit_time = hitbox['hit_time']
        bag_type = hitbox['type']
        
        # Convert to screen coordinates
        screen_x = int(x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        screen_y = int(y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
        screen_size = int(size * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        screen_center_x = int(center_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        screen_center_y = int(center_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
        screen_radius = int(radius * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        
        # Draw circle background
        if is_active:
            # Active - pulsing circle
            pulse = math.sin(current_time * 3) * 0.1 + 0.9
            circle_color = (int(255 * pulse), int(50 * pulse), int(50 * pulse))
            circle_width = 3
        else:
            # Hit - fading circle
            elapsed = current_time - hit_time
            fade = max(0, 1 - elapsed * 2)  # Fade out in 0.5s
            circle_color = (0, int(255 * fade), 0)
            circle_width = 2
        
        pygame.draw.circle(self.screen, circle_color, 
                          (screen_center_x, screen_center_y), 
                          screen_radius, circle_width)
        
        # Select punch bag image
        if bag_type == 'red':
            bag_image = self.punch_bag_red
        elif bag_type == 'blue':
            bag_image = self.punch_bag_blue
        else:
            bag_image = self.punch_bag_black
        
        if bag_image is None:
            continue
        
        # Calculate bag position (center in circle)
        bag_size = int(screen_size * 0.8)  # Bag is 80% of circle size
        bag_x = screen_center_x - bag_size // 2
        bag_y = screen_center_y - bag_size // 2
        
        try:
            # Convert and render punch bag
            bag_resized = cv2.resize(bag_image, (bag_size, bag_size))
            bag_rgba = cv2.cvtColor(bag_resized, cv2.COLOR_BGRA2RGBA)
            bag_surface = pygame.image.frombuffer(bag_rgba.tobytes(), (bag_size, bag_size), "RGBA")
            
            # Apply transparency if hit
            if not is_active:
                elapsed = current_time - hit_time
                alpha = max(0, 255 - int(elapsed * 500))
                bag_surface.set_alpha(alpha)
            
            self.screen.blit(bag_surface, (bag_x, bag_y))
            
            # Add pulse effect for active hitboxes
            if is_active:
                pulse_size = int(screen_radius * (1 + math.sin(current_time * 4) * 0.05))
                pygame.draw.circle(self.screen, (255, 255, 0, 50), 
                                  (screen_center_x, screen_center_y), 
                                  pulse_size, 1)
        
        except Exception as e:
            # Fallback - draw colored circle
            pygame.draw.circle(self.screen, circle_color, 
                              (screen_center_x, screen_center_y), 
                              screen_radius // 2, 0)


def render_enemy_attack(self, game_state):
    """Render enemy attack dengan target icon dan glove animation"""
    if not hasattr(game_state, 'enemy_attack_system'):
        return
    
    attack_system = game_state.enemy_attack_system
    
    # Render target icon during warning phase
    target_pos = attack_system.get_target_position()
    if target_pos and self.target_icon is not None:
        target_x, target_y = target_pos
        
        # Convert to screen coordinates
        screen_x = int(target_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        screen_y = int(target_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
        
        try:
            # Load and render target icon
            icon_size = 60
            target_resized = cv2.resize(self.target_icon, (icon_size, icon_size))
            target_rgba = cv2.cvtColor(target_resized, cv2.COLOR_BGRA2RGBA)
            target_surface = pygame.image.frombuffer(target_rgba.tobytes(), (icon_size, icon_size), "RGBA")
            
            # Pulsing effect
            pulse = math.sin(time.time() * 5) * 0.1 + 0.9
            scaled_size = int(icon_size * pulse)
            target_surface = pygame.transform.scale(target_surface, (scaled_size, scaled_size))
            
            self.screen.blit(target_surface, 
                           (screen_x - scaled_size // 2, screen_y - scaled_size // 2))
        except Exception as e:
            # Fallback - draw red crosshair
            pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), 30, 3)
            pygame.draw.line(self.screen, (255, 0, 0), 
                           (screen_x - 40, screen_y), (screen_x + 40, screen_y), 3)
            pygame.draw.line(self.screen, (255, 0, 0), 
                           (screen_x, screen_y - 40), (screen_x, screen_y + 40), 3)
    
    # Render glove animation during attack phase
    glove_pos = attack_system.get_glove_position()
    if glove_pos and self.glove_image is not None:
        glove_x, glove_y = glove_pos
        
        # Convert to screen coordinates
        screen_x = int(glove_x * self.config.WINDOW_WIDTH / self.config.CAMERA_WIDTH)
        screen_y = int(glove_y * self.config.WINDOW_HEIGHT / self.config.CAMERA_HEIGHT)
        
        try:
            # Render glove with rotation based on direction
            glove_size = 80
            glove_resized = cv2.resize(self.glove_image, (glove_size, glove_size))
            glove_rgba = cv2.cvtColor(glove_resized, cv2.COLOR_BGRA2RGBA)
            glove_surface = pygame.image.frombuffer(glove_rgba.tobytes(), (glove_size, glove_size), "RGBA")
            
            # Add trail effect
            progress = attack_system.glove_progress
            if progress < 0.8:
                # Draw motion blur trail
                for i in range(3):
                    trail_offset = (i + 1) * 15
                    trail_alpha = 100 - i * 30
                    trail_y = screen_y + trail_offset
                    trail_surface = glove_surface.copy()
                    trail_surface.set_alpha(trail_alpha)
                    self.screen.blit(trail_surface, (screen_x - glove_size // 2, trail_y - glove_size // 2))
            
            # Draw main glove
            self.screen.blit(glove_surface, (screen_x - glove_size // 2, screen_y - glove_size // 2))
            
        except Exception as e:
            # Fallback - draw red fist
            pygame.draw.circle(self.screen, (200, 0, 0), (screen_x, screen_y), 30, 0)

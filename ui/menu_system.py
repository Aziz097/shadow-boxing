"""Menu system - handles main menu navigation and input."""

import pygame
import time
import os
import cv2

class MenuSystem:
    def __init__(self, game_config, render_system=None, vision_system=None):
        self.config = game_config
        self.render_system = render_system  
        self.vision_system = vision_system  # Store vision system reference
        self.current_menu = "MAIN"
        self.selected_item = 0
        self.menu_items = {
            "MAIN": ["START GAME", "DIFFICULTY", "HELP", "QUIT"],
            "DIFFICULTY": ["EASY", "MEDIUM", "HARD", "BACK"],
            "HELP": ["BACK"]
        }
        self.last_key_time = 0
        self.key_cooldown = 0.2
        
        # No static background - will use camera feed
        self.background = None
    
    def handle_input(self, keys):
        """Handle menu input with direct key checking"""
        current_time = time.time()
        if current_time - self.last_key_time < self.key_cooldown:
            return None
        
        # Check if any navigation key is pressed
        if keys[pygame.K_UP]:
            self.last_key_time = current_time
            self.selected_item = (self.selected_item - 1) % len(self.menu_items[self.current_menu])
            return "NAVIGATE"
        elif keys[pygame.K_DOWN]:
            self.last_key_time = current_time
            self.selected_item = (self.selected_item + 1) % len(self.menu_items[self.current_menu])
            return "NAVIGATE"
        elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.last_key_time = current_time
            return self._select_item()
        elif keys[pygame.K_ESCAPE] and self.current_menu != "MAIN":
            self.last_key_time = current_time
            self.current_menu = "MAIN"
            self.selected_item = 0
            return "BACK"
        
        return None
    
    def _select_item(self):
        """Handle item selection"""
        item = self.menu_items[self.current_menu][self.selected_item]
        
        if self.current_menu == "MAIN":
            if item == "START GAME":
                return "START"
            elif item == "DIFFICULTY":
                self.current_menu = "DIFFICULTY"
                self.selected_item = 0
            elif item == "HELP":
                self.current_menu = "HELP"
                self.selected_item = 0
            elif item == "QUIT":
                return "QUIT"
        
        elif self.current_menu == "DIFFICULTY":
            if item == "EASY":
                self.config.DEFAULT_DIFFICULTY = "EASY"
            elif item == "MEDIUM":
                self.config.DEFAULT_DIFFICULTY = "MEDIUM"
            elif item == "HARD":
                self.config.DEFAULT_DIFFICULTY = "HARD"
            elif item == "BACK":
                self.current_menu = "MAIN"
                self.selected_item = 0
        
        elif self.current_menu == "HELP":
            if item == "BACK":
                self.current_menu = "MAIN"
                self.selected_item = 0
        
        return None
    
    def render(self, screen, camera_frame=None):
        """Render menu with camera feed as background"""
        # Use camera feed as background
        if camera_frame is not None:
            # Convert OpenCV BGR to pygame RGB and display
            frame_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
            screen.blit(frame_surface, (0, 0))
            
            # Add dark overlay for better text readability
            overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
        else:
            # Fallback to solid color if camera feed unavailable
            screen.fill((20, 20, 40))
        
        # Draw title
        try:
            if hasattr(self.config, 'FONT_PATH') and os.path.exists(self.config.FONT_PATH):
                title_font = pygame.font.Font(self.config.FONT_PATH, 48)
            else:
                title_font = pygame.font.SysFont("Arial", 80)
        except Exception as e:
            print(f"Error loading title font: {str(e)}")
            title_font = pygame.font.SysFont("Arial", 80)
        
        title = title_font.render("SHADOW BOXING", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(self.config.WINDOW_WIDTH//2, 120)))
        
        # Draw menu items
        try:
            menu_font = pygame.font.Font(self.config.FONT_PATH, 28) if hasattr(self.config, 'FONT_PATH') else pygame.font.SysFont("Arial", 48)
        except:
            menu_font = pygame.font.SysFont("Arial", 48)
        
        item_height = 70
        
        for i, item in enumerate(self.menu_items[self.current_menu]):
            color = (255, 255, 255)
            if i == self.selected_item:
                color = (255, 215, 0)  # Gold for selected
            
            # Add difficulty indicator
            display_text = item
            if self.current_menu == "DIFFICULTY" and item == self.config.DEFAULT_DIFFICULTY:
                display_text += " (SELECTED)"
            
            text = menu_font.render(display_text, True, color)
            y_pos = self.config.WINDOW_HEIGHT//2 - (len(self.menu_items[self.current_menu]) * item_height)//2 + i * item_height
            
            # Highlight background for selected item
            if i == self.selected_item:
                highlight = pygame.Surface((text.get_width() + 40, text.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (100, 100, 255, 100), highlight.get_rect(), border_radius=10)
                highlight_rect = highlight.get_rect(center=(self.config.WINDOW_WIDTH//2, y_pos))
                screen.blit(highlight, highlight_rect)
            
            screen.blit(text, text.get_rect(center=(self.config.WINDOW_WIDTH//2, y_pos)))
        
        # Draw instructions
        if self.current_menu == "MAIN":
            instructions = [
                "USE ARROW KEYS TO NAVIGATE",
                "PRESS ENTER OR SPACE TO SELECT",
                "PRESS Q OR ESC TO QUIT"
            ]
        elif self.current_menu == "DIFFICULTY":
            instructions = [
                "EASY: Slower enemy, more time to attack",
                "MEDIUM: Balanced gameplay (recommended)",
                "HARD: Fast enemy, less time to attack"
            ]
        elif self.current_menu == "HELP":
            instructions = [
                "HOW TO PLAY:",
                "- HIT TARGETS DURING YOUR TURN",
                "- DEFEND BY COVERING YOUR FACE WITH BOTH HANDS",
                "- DODGE BY MOVING HEAD QUICKLY SIDE TO SIDE"
            ]
        
        try:
            instr_font = pygame.font.Font(self.config.FONT_PATH, 14) if hasattr(self.config, 'FONT_PATH') else pygame.font.SysFont("Arial", 24)
        except:
            instr_font = pygame.font.SysFont("Arial", 24)
        
        for i, line in enumerate(instructions):
            text = instr_font.render(line, True, (200, 200, 200))
            screen.blit(text, text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 120 + i * 30)))
import pygame
import time

class ResultScreen:
    def __init__(self, game_config):
        self.config = game_config
        self.active = False
        self.player_won = False
        self.score = 0
        self.start_time = 0
    
    def show(self, player_won, score):
        """Show result screen"""
        self.active = True
        self.player_won = player_won
        self.score = score
        self.start_time = time.time()
    
    def handle_input(self, key):
        """Handle input on result screen"""
        if key == pygame.K_SPACE or key == pygame.K_RETURN:
            return "RESTART"
        elif key == pygame.K_ESCAPE or key == pygame.K_q:
            return "QUIT"
        return None
    
    def render(self, screen):
        """Render result screen"""
        if not self.active:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Result text
        result_text = "VICTORY!" if self.player_won else "DEFEAT!"
        result_color = (0, 255, 0) if self.player_won else (255, 0, 0)
        
        try:
            title_font = pygame.font.Font(self.config.FONT_PATH, 60)
        except:
            title_font = pygame.font.SysFont("Arial", 100)
        
        title = title_font.render(result_text, True, result_color)
        screen.blit(title, title.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 100)))
        
        # Score
        try:
            score_font = pygame.font.Font(self.config.FONT_PATH, 36)
        except:
            score_font = pygame.font.SysFont("Arial", 60)
        
        score_text = score_font.render(f"FINAL SCORE {self.score}", True, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 20)))
        
        # Instructions
        try:
            instr_font = pygame.font.Font(self.config.FONT_PATH, 22)
        except:
            instr_font = pygame.font.SysFont("Arial", 36)
        
        restart_text = instr_font.render("PRESS ENTER TO RESTART", True, (255, 255, 255))
        quit_text = instr_font.render("PRESS Q TO QUIT", True, (200, 200, 200))
        
        screen.blit(restart_text, restart_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 100)))
        screen.blit(quit_text, quit_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT - 60)))
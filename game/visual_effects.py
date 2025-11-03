"""
Visual Effects Manager untuk Shadow Boxing
Mengelola semua efek visual: telegraph warnings, motion trails, damage indicators, UI elements
"""
import cv2
import numpy as np
import time

class VisualEffects:
    """Manages all visual effects and UI rendering"""
    
    def __init__(self):
        """Initialize visual effects manager"""
        self.damage_indicators = []  # List of active damage indicators
        self.screen_shake = 0  # Screen shake intensity
        self.hit_flash_time = 0  # Time of last hit for flash effect
        self.hit_flash_duration = 0.1
        
    def draw_telegraph_warning(self, frame, enemy_ai, current_time):
        """
        Draw telegraph warning indicator
        
        Args:
            frame: Video frame
            enemy_ai: EnemyAI instance
            current_time: Current timestamp
        """
        if not enemy_ai.is_telegraphing():
            return frame
        
        h, w = frame.shape[:2]
        
        # Pulse effect
        pulse = abs(np.sin(current_time * 10)) * 0.5 + 0.5
        
        # Warning text
        text = f"!!! {enemy_ai.attack_type} ATTACK !!!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 4
        
        # Get text size
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Position at top center
        x = (w - text_w) // 2
        y = 80
        
        # Warning color (yellow to red based on pulse)
        color = (0, int(255 * (1 - pulse)), int(255 * pulse))
        
        # Draw with glow effect
        cv2.putText(frame, text, (x, y), font, font_scale, (0, 0, 0), thickness + 4)
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
        
        # Direction indicator
        if enemy_ai.attack_target:
            tx, ty = enemy_ai.attack_target
            # Draw arrow pointing to target
            arrow_start = (w // 2, 120)
            arrow_end = (tx, ty)
            cv2.arrowedLine(frame, arrow_start, arrow_end, color, 3, tipLength=0.3)
        
        # Progress bar for telegraph
        progress = min(1.0, (current_time - enemy_ai.telegraph_start_time) / enemy_ai.telegraph_duration)
        bar_width = 300
        bar_height = 20
        bar_x = (w - bar_width) // 2
        bar_y = 120
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        # Progress
        progress_w = int(bar_width * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_w, bar_y + bar_height), color, -1)
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        return frame
    
    def draw_enemy_punch(self, frame, enemy_ai, current_time):
        """
        Draw enemy punch with motion trail
        
        Args:
            frame: Video frame
            enemy_ai: EnemyAI instance
            current_time: Current timestamp
        """
        hand_pos = enemy_ai.get_hand_position(current_time)
        
        if hand_pos:
            x, y = hand_pos
            
            # Main punch circle
            if enemy_ai.is_attacking():
                color = (0, 0, 255)  # red
                size = 35
            else:
                color = (0, 255, 255)  # yellow for telegraph
                size = 25
            
            # Glow effect
            cv2.circle(frame, (x, y), size + 10, color, 2)
            cv2.circle(frame, (x, y), size, color, -1)
            
            # Inner highlight
            cv2.circle(frame, (x - 5, y - 5), size // 3, (255, 255, 255), -1)
            
            # Motion trail (if attacking)
            if enemy_ai.is_attacking() and enemy_ai.attack_target:
                tx, ty = enemy_ai.attack_target
                # Draw motion lines
                for i in range(3):
                    alpha = 0.3 - i * 0.1
                    trail_x = int(x + (tx - x) * 0.1 * i)
                    trail_y = int(y + (ty - y) * 0.1 * i)
                    overlay = frame.copy()
                    cv2.circle(overlay, (trail_x, trail_y), size - i * 5, color, -1)
                    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def draw_hp_bars(self, frame, game_state):
        """
        Draw HP bars for player and enemy
        
        Args:
            frame: Video frame
            game_state: GameState instance
        """
        h, w = frame.shape[:2]
        
        # Bar dimensions
        bar_width = 300
        bar_height = 30
        margin = 20
        
        # Player HP (bottom left)
        player_hp_pct = game_state.get_player_hp_percentage()
        self._draw_hp_bar(
            frame,
            x=margin,
            y=h - margin - bar_height,
            width=bar_width,
            height=bar_height,
            hp_percentage=player_hp_pct,
            label="PLAYER",
            color=(0, 255, 0)
        )
        
        # Enemy HP (top right)
        enemy_hp_pct = game_state.get_enemy_hp_percentage()
        self._draw_hp_bar(
            frame,
            x=w - margin - bar_width,
            y=margin,
            width=bar_width,
            height=bar_height,
            hp_percentage=enemy_hp_pct,
            label="ENEMY",
            color=(255, 0, 0)
        )
        
        return frame
    
    def _draw_hp_bar(self, frame, x, y, width, height, hp_percentage, label, color):
        """Helper function to draw a single HP bar"""
        # Background
        cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
        
        # HP fill
        hp_width = int(width * (hp_percentage / 100))
        
        # Color gradient based on HP
        if hp_percentage > 60:
            bar_color = color
        elif hp_percentage > 30:
            bar_color = (0, 255, 255)  # yellow
        else:
            bar_color = (0, 0, 255)  # red
        
        cv2.rectangle(frame, (x, y), (x + hp_width, y + height), bar_color, -1)
        
        # Border
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)
        
        # Label and HP text
        font = cv2.FONT_HERSHEY_SIMPLEX
        label_text = f"{label}: {int(hp_percentage)}%"
        cv2.putText(frame, label_text, (x + 5, y - 5), font, 0.6, (255, 255, 255), 2)
    
    def draw_stamina_bar(self, frame, enemy_ai):
        """Draw enemy stamina bar"""
        h, w = frame.shape[:2]
        
        stamina_pct = enemy_ai.get_stamina_percentage()
        
        # Position below enemy HP
        bar_width = 300
        bar_height = 15
        x = w - 20 - bar_width
        y = 80
        
        # Background
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (30, 30, 30), -1)
        
        # Stamina fill
        stamina_width = int(bar_width * (stamina_pct / 100))
        cv2.rectangle(frame, (x, y), (x + stamina_width, y + bar_height), (255, 255, 0), -1)
        
        # Border
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (150, 150, 150), 1)
        
        # Label
        cv2.putText(frame, "STAMINA", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return frame
    
    def draw_round_info(self, frame, round_manager, current_time):
        """Draw round information"""
        h, w = frame.shape[:2]
        
        # Status text
        status_text = round_manager.get_status_text(current_time)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Position at top center
        (text_w, text_h), _ = cv2.getTextSize(status_text, font, 1.0, 3)
        x = (w - text_w) // 2
        y = 40
        
        # Background box
        padding = 10
        cv2.rectangle(frame, 
                     (x - padding, y - text_h - padding),
                     (x + text_w + padding, y + padding),
                     (0, 0, 0), -1)
        
        # Text
        cv2.putText(frame, status_text, (x, y), font, 1.0, (255, 255, 255), 3)
        
        return frame
    
    def draw_stats_overlay(self, frame, game_state):
        """Draw statistics overlay"""
        h, w = frame.shape[:2]
        
        stats = game_state.get_stats_summary()
        
        # Position at bottom right
        x = w - 250
        y = h - 150
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x - 10, y - 30), (x + 240, y + 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Stats text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        
        cv2.putText(frame, "=== STATS ===", (x, y), font, font_scale, (0, 255, 255), 1)
        cv2.putText(frame, f"Punches: {stats['player_punches']}", (x, y + 25), font, font_scale, color, 1)
        cv2.putText(frame, f"Accuracy: {stats['player_accuracy']:.1f}%", (x, y + 45), font, font_scale, color, 1)
        cv2.putText(frame, f"Blocks: {stats['blocks']}", (x, y + 65), font, font_scale, color, 1)
        cv2.putText(frame, f"Hits Taken: {stats['enemy_hits']}", (x, y + 85), font, font_scale, color, 1)
        
        return frame
    
    def draw_combo_indicator(self, frame, enemy_ai):
        """Draw combo indicator when enemy is doing combo"""
        if not enemy_ai.in_combo:
            return frame
        
        h, w = frame.shape[:2]
        
        text = f"COMBO x{enemy_ai.combo_count + 1}/{enemy_ai.max_combo}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        (text_w, text_h), _ = cv2.getTextSize(text, font, 1.2, 4)
        x = (w - text_w) // 2
        y = h // 2
        
        # Pulsing effect
        pulse = abs(np.sin(time.time() * 15))
        color = (0, int(100 + 155 * pulse), 255)
        
        cv2.putText(frame, text, (x, y), font, 1.2, (0, 0, 0), 7)
        cv2.putText(frame, text, (x, y), font, 1.2, color, 4)
        
        return frame
    
    def draw_vulnerable_indicator(self, frame, enemy_ai):
        """Draw indicator when enemy is vulnerable"""
        if not enemy_ai.is_vulnerable():
            return frame
        
        h, w = frame.shape[:2]
        
        text = "*** COUNTER ATTACK! ***"
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        (text_w, text_h), _ = cv2.getTextSize(text, font, 1.0, 3)
        x = (w - text_w) // 2
        y = h - 100
        
        # Blinking effect
        if int(time.time() * 5) % 2 == 0:
            cv2.putText(frame, text, (x, y), font, 1.0, (0, 255, 0), 3)
        
        return frame
    
    def draw_hit_flash(self, frame, current_time):
        """Draw red flash effect when hit"""
        if current_time - self.hit_flash_time < self.hit_flash_duration:
            # Red overlay
            overlay = frame.copy()
            overlay[:] = (0, 0, 150)  # red tint
            alpha = 1.0 - (current_time - self.hit_flash_time) / self.hit_flash_duration
            cv2.addWeighted(overlay, alpha * 0.3, frame, 1 - alpha * 0.3, 0, frame)
        
        return frame
    
    def trigger_hit_flash(self):
        """Trigger hit flash effect"""
        self.hit_flash_time = time.time()
    
    def draw_game_over(self, frame, game_state):
        """Draw game over screen"""
        if not game_state.game_over:
            return frame
        
        h, w = frame.shape[:2]
        
        # Dark overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Game over text
        text = "KNOCKOUT!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_w, text_h), _ = cv2.getTextSize(text, font, 3.0, 7)
        x = (w - text_w) // 2
        y = h // 2 - 50
        
        cv2.putText(frame, text, (x, y), font, 3.0, (0, 0, 255), 7)
        
        # Winner
        winner_text = f"{game_state.winner} WINS!"
        (text_w, text_h), _ = cv2.getTextSize(winner_text, font, 2.0, 5)
        x = (w - text_w) // 2
        y = h // 2 + 50
        
        color = (0, 255, 0) if game_state.winner == "PLAYER" else (0, 0, 255)
        cv2.putText(frame, winner_text, (x, y), font, 2.0, color, 5)
        
        return frame

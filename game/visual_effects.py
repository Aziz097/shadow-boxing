"""
Visual Effects Manager untuk Shadow Boxing
Mengelola semua efek visual: telegraph warnings, motion trails, damage indicators, UI elements
Modern UI with rounded corners and soft colors
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
        
        # Round start notification
        self.round_start_notification = None  # {'time': float, 'text': str}
        self.notification_duration = 2.0  # seconds
        
        # Modern soft color palette
        self.colors = {
            'player': (120, 255, 120),      # Soft green
            'enemy': (120, 120, 255),       # Soft red/pink
            'warning': (100, 200, 255),     # Soft orange
            'vulnerable': (120, 255, 200),  # Soft cyan
            'bg_dark': (40, 40, 45),        # Dark background
            'bg_light': (60, 60, 70),       # Light background
            'text': (240, 240, 245),        # Soft white
            'accent': (200, 150, 255),      # Soft purple
        }
    
    def draw_rounded_rectangle(self, frame, x1, y1, x2, y2, radius, color, thickness=-1):
        """Draw rectangle with rounded corners"""
        # Create mask for rounded rectangle
        if thickness == -1:  # Filled
            cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y2), color, -1)
            cv2.rectangle(frame, (x1, y1 + radius), (x2, y2 - radius), color, -1)
            cv2.circle(frame, (x1 + radius, y1 + radius), radius, color, -1)
            cv2.circle(frame, (x2 - radius, y1 + radius), radius, color, -1)
            cv2.circle(frame, (x1 + radius, y2 - radius), radius, color, -1)
            cv2.circle(frame, (x2 - radius, y2 - radius), radius, color, -1)
        else:  # Outline
            # Draw lines
            cv2.line(frame, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
            cv2.line(frame, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
            cv2.line(frame, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
            cv2.line(frame, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
            # Draw corners
            cv2.ellipse(frame, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
            cv2.ellipse(frame, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
            cv2.ellipse(frame, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
            cv2.ellipse(frame, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)
        
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
        Draw modern HP bars with rounded corners
        
        Args:
            frame: Video frame
            game_state: GameState instance
        """
        h, w = frame.shape[:2]
        
        # Bar dimensions - wider and thinner for modern look
        bar_width = 350
        bar_height = 25
        margin = 30
        radius = 12
        
        # Player HP (bottom left)
        player_hp_pct = game_state.get_player_hp_percentage()
        px = margin
        py = h - margin - bar_height - 40
        
        # Background
        self.draw_rounded_rectangle(frame, px, py, px + bar_width, py + bar_height, 
                                    radius, self.colors['bg_light'], -1)
        
        # HP fill
        fill_width = int(bar_width * (player_hp_pct / 100))
        if fill_width > 0:
            self.draw_rounded_rectangle(frame, px + 2, py + 2, px + fill_width - 2, py + bar_height - 2,
                                        radius - 2, self.colors['player'], -1)
        
        # Label
        cv2.putText(frame, "YOU", (px, py - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, self.colors['text'], 2)
        # HP text
        hp_text = f"{int(game_state.player_hp)}"
        (tw, th), _ = cv2.getTextSize(hp_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, hp_text, (px + bar_width - tw, py - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['player'], 2)
        
        # Enemy HP (top right)
        enemy_hp_pct = game_state.get_enemy_hp_percentage()
        ex = w - margin - bar_width
        ey = margin + 40
        
        # Background
        self.draw_rounded_rectangle(frame, ex, ey, ex + bar_width, ey + bar_height,
                                    radius, self.colors['bg_light'], -1)
        
        # HP fill
        fill_width = int(bar_width * (enemy_hp_pct / 100))
        if fill_width > 0:
            self.draw_rounded_rectangle(frame, ex + 2, ey + 2, ex + fill_width - 2, ey + bar_height - 2,
                                        radius - 2, self.colors['enemy'], -1)
        
        # Label
        cv2.putText(frame, "ENEMY", (ex, ey - 10), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, self.colors['text'], 2)
        # HP text
        hp_text = f"{int(game_state.enemy_hp)}"
        (tw, th), _ = cv2.getTextSize(hp_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, hp_text, (ex + bar_width - tw, ey - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['enemy'], 2)
        
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
        """Draw modern round information with score"""
        h, w = frame.shape[:2]
        
        # Top center info panel
        panel_width = 400
        panel_height = 80
        px = (w - panel_width) // 2
        py = 15
        radius = 15
        
        # Semi-transparent background
        overlay = frame.copy()
        self.draw_rounded_rectangle(overlay, px, py, px + panel_width, py + panel_height,
                                    radius, self.colors['bg_dark'], -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Round number
        round_text = f"ROUND {round_manager.current_round}/{round_manager.total_rounds}"
        (tw, th), _ = cv2.getTextSize(round_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        tx = px + (panel_width - tw) // 2
        cv2.putText(frame, round_text, (tx, py + 30), cv2.FONT_HERSHEY_SIMPLEX,
                   0.8, self.colors['accent'], 2)
        
        # Score display
        score_text = f"{round_manager.player_round_wins}  -  {round_manager.enemy_round_wins}"
        (tw, th), _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
        tx = px + (panel_width - tw) // 2
        cv2.putText(frame, score_text, (tx, py + 65), cv2.FONT_HERSHEY_SIMPLEX,
                   1.2, self.colors['text'], 3)
        
        # Timer
        if round_manager.state == "FIGHTING":
            remaining = round_manager.get_remaining_time(current_time)
            timer_text = f"{int(remaining)}s"
            timer_color = self.colors['warning'] if remaining < 10 else self.colors['text']
        elif round_manager.state == "REST":
            remaining = round_manager.get_rest_remaining(current_time)
            timer_text = f"REST: {int(remaining)}s"
            timer_color = self.colors['vulnerable']
        else:
            timer_text = "READY"
            timer_color = self.colors['text']
            
        # Timer background
        timer_width = 100
        timer_height = 30
        timer_x = px + (panel_width - timer_width) // 2
        timer_y = py + panel_height + 10
        
        overlay2 = frame.copy()
        self.draw_rounded_rectangle(overlay2, timer_x, timer_y, timer_x + timer_width, timer_y + timer_height,
                                    10, self.colors['bg_light'], -1)
        cv2.addWeighted(overlay2, 0.9, frame, 0.1, 0, frame)
        
        (tw, th), _ = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        tx = timer_x + (timer_width - tw) // 2
        ty = timer_y + (timer_height + th) // 2
        cv2.putText(frame, timer_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, timer_color, 2)
        
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
        """Draw modern vulnerable indicator with rounded panel"""
        if not enemy_ai.is_vulnerable():
            return frame
        
        h, w = frame.shape[:2]
        
        # Modern panel design
        panel_width = 500
        panel_height = 120
        px = (w - panel_width) // 2
        py = int(h * 0.45)
        radius = 20
        
        # Pulsing animation
        pulse = abs(np.sin(time.time() * 6)) * 0.3 + 0.7
        
        # Background with pulse
        overlay = frame.copy()
        bg_color = tuple([int(c * pulse) for c in self.colors['vulnerable']])
        self.draw_rounded_rectangle(overlay, px, py, px + panel_width, py + panel_height,
                                    radius, bg_color, -1)
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        # Border
        self.draw_rounded_rectangle(frame, px, py, px + panel_width, py + panel_height,
                                    radius, self.colors['vulnerable'], 3)
        
        # MAIN TEXT
        text = "HIT NOW!"
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.2, 4)
        tx = px + (panel_width - text_w) // 2
        ty = py + 55
        
        # Shadow
        cv2.putText(frame, text, (tx + 3, ty + 3), cv2.FONT_HERSHEY_SIMPLEX, 
                   2.2, (0, 0, 0), 6)
        # Main text
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                   2.2, self.colors['text'], 4)
        
        # Subtitle
        subtitle = "⚡ PUNCH THE ENEMY ⚡"
        (sub_w, sub_h), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        sub_x = px + (panel_width - sub_w) // 2
        sub_y = py + 95
        cv2.putText(frame, subtitle, (sub_x, sub_y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.8, self.colors['text'], 2)
        
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
        
        # Restart instruction
        restart_text = "Press SPACE to restart"
        (text_w, text_h), _ = cv2.getTextSize(restart_text, font, 0.8, 2)
        x = (w - text_w) // 2
        y = h // 2 + 120
        cv2.putText(frame, restart_text, (x, y), font, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def show_round_start(self, round_number):
        """Trigger round start notification"""
        self.round_start_notification = {
            'time': time.time(),
            'text': f"ROUND {round_number} START!"
        }
    
    def draw_round_notification(self, frame, current_time):
        """Draw round start notification banner"""
        if not self.round_start_notification:
            return frame
        
        # Check if notification expired
        elapsed = current_time - self.round_start_notification['time']
        if elapsed > self.notification_duration:
            self.round_start_notification = None
            return frame
        
        h, w = frame.shape[:2]
        
        # Animation: slide in from top
        progress = min(1.0, elapsed / 0.3)  # 0.3s slide animation
        fade_out = 1.0 if elapsed < (self.notification_duration - 0.5) else (self.notification_duration - elapsed) * 2
        alpha = min(progress, fade_out)
        
        # Panel dimensions
        panel_width = 600
        panel_height = 100
        px = (w - panel_width) // 2
        py = int(h * 0.3 - 50 + (1 - progress) * -100)  # Slide from top
        radius = 20
        
        # Background
        overlay = frame.copy()
        bg_color = self.colors['accent']
        self.draw_rounded_rectangle(overlay, px, py, px + panel_width, py + panel_height,
                                    radius, bg_color, -1)
        cv2.addWeighted(overlay, alpha * 0.95, frame, 1 - alpha * 0.95, 0, frame)
        
        # Border glow
        for i in range(3):
            self.draw_rounded_rectangle(frame, px - i*2, py - i*2, 
                                        px + panel_width + i*2, py + panel_height + i*2,
                                        radius + i*2, bg_color, 2)
        
        # Text
        text = self.round_start_notification['text']
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 5)
        tx = px + (panel_width - tw) // 2
        ty = py + (panel_height + th) // 2
        
        # Shadow
        cv2.putText(frame, text, (tx + 4, ty + 4), cv2.FONT_HERSHEY_SIMPLEX,
                   2.5, (0, 0, 0), 7)
        # Main text
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                   2.5, self.colors['text'], 5)
        
        return frame

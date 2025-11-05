"""Visual Effects Manager for Shadow Boxing."""
import time
from typing import Dict, Optional, Tuple

import cv2
import numpy as np


ColorTuple = Tuple[int, int, int]
RoundNotification = Dict[str, object]  # {'time': float, 'text': str}


class VisualEffects:
    """Manages all visual effects and UI rendering."""
    
    HIT_FLASH_DURATION = 0.1
    NOTIFICATION_DURATION = 2.0
    HP_BAR_WIDTH = 300
    HP_BAR_HEIGHT = 20
    TELEGRAPH_BAR_WIDTH = 300
    TELEGRAPH_BAR_HEIGHT = 8
    ROUND_PANEL_WIDTH = 350
    ROUND_PANEL_HEIGHT = 70
    VULNERABLE_PANEL_WIDTH = 400
    VULNERABLE_PANEL_HEIGHT = 80
    
    def __init__(self):
        self.damage_indicators: list = []
        self.screen_shake = 0
        self.hit_flash_time = 0.0
        self.round_start_notification: Optional[RoundNotification] = None
        
        self.colors: Dict[str, ColorTuple] = {
            'player': (100, 200, 100),
            'enemy': (80, 80, 200),
            'warning': (100, 180, 255),
            'vulnerable': (100, 220, 180),
            'bg_dark': (30, 30, 35),
            'bg_light': (50, 50, 55),
            'text': (255, 255, 255),
            'accent': (180, 130, 230),
            'border': (200, 200, 200),
        }
    
    def draw_rounded_rectangle(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int, 
                              radius: int, color: ColorTuple, thickness: int = -1) -> None:
        """Draw simple rectangle."""
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    def draw_telegraph_warning(self, frame: np.ndarray, enemy_ai, current_time: float) -> np.ndarray:
        """Draw telegraph warning indicator."""
        if not enemy_ai.is_telegraphing():
            return frame
        
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        text = f"!!! {enemy_ai.attack_type} ATTACK !!!"
        (text_w, text_h), _ = cv2.getTextSize(text, font, 1.2, 2)
        
        x = (w - text_w) // 2
        y = 80
        color = (0, 255, 255)
        
        cv2.putText(frame, text, (x, y), font, 1.2, (0, 0, 0), 4)
        cv2.putText(frame, text, (x, y), font, 1.2, color, 2)
        
        progress = min(1.0, (current_time - enemy_ai.telegraph_start_time) / enemy_ai.telegraph_duration)
        bar_x = (w - self.TELEGRAPH_BAR_WIDTH) // 2
        bar_y = 100
        
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + self.TELEGRAPH_BAR_WIDTH, bar_y + self.TELEGRAPH_BAR_HEIGHT), 
                     (50, 50, 50), -1)
        
        progress_w = int(self.TELEGRAPH_BAR_WIDTH * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_w, bar_y + self.TELEGRAPH_BAR_HEIGHT), 
                     color, -1)
        
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + self.TELEGRAPH_BAR_WIDTH, bar_y + self.TELEGRAPH_BAR_HEIGHT), 
                     (200, 200, 200), 1)
        
        return frame
    
    def draw_enemy_punch(self, frame: np.ndarray, enemy_ai, current_time: float) -> np.ndarray:
        """Draw enemy punch circle."""
        hand_pos = enemy_ai.get_hand_position(current_time)
        
        if hand_pos:
            x, y = hand_pos
            
            if enemy_ai.is_attacking():
                color = (0, 0, 255)
                size = 30
            else:
                color = (0, 255, 255)
                size = 20
            
            cv2.circle(frame, (x, y), size, color, -1)
            cv2.circle(frame, (x, y), size, (255, 255, 255), 2)
        
        return frame
    
    def draw_hp_bars(self, frame: np.ndarray, game_state) -> np.ndarray:
        """Draw clean HP bars."""
        h, w = frame.shape[:2]
        margin = 30
        
        player_hp_pct = game_state.get_player_hp_percentage()
        px = margin
        py = h - margin - self.HP_BAR_HEIGHT - 40
        
        cv2.rectangle(frame, (px, py), (px + self.HP_BAR_WIDTH, py + self.HP_BAR_HEIGHT), 
                     self.colors['bg_light'], -1)
        
        fill_width = int(self.HP_BAR_WIDTH * (player_hp_pct / 100))
        if fill_width > 0:
            cv2.rectangle(frame, (px, py), (px + fill_width, py + self.HP_BAR_HEIGHT),
                         self.colors['player'], -1)
        
        cv2.rectangle(frame, (px, py), (px + self.HP_BAR_WIDTH, py + self.HP_BAR_HEIGHT),
                     self.colors['border'], 2)
        
        cv2.putText(frame, "YOU", (px, py - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, self.colors['text'], 2)
        
        hp_text = f"{int(game_state.player_hp)}"
        (tw, th), _ = cv2.getTextSize(hp_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, hp_text, (px + self.HP_BAR_WIDTH - tw, py - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['text'], 2)
        
        enemy_hp_pct = game_state.get_enemy_hp_percentage()
        ex = w - margin - self.HP_BAR_WIDTH
        ey = margin + 40
        
        cv2.rectangle(frame, (ex, ey), (ex + self.HP_BAR_WIDTH, ey + self.HP_BAR_HEIGHT),
                     self.colors['bg_light'], -1)
        
        fill_width = int(self.HP_BAR_WIDTH * (enemy_hp_pct / 100))
        if fill_width > 0:
            cv2.rectangle(frame, (ex, ey), (ex + fill_width, ey + self.HP_BAR_HEIGHT),
                         self.colors['enemy'], -1)
        
        cv2.rectangle(frame, (ex, ey), (ex + self.HP_BAR_WIDTH, ey + self.HP_BAR_HEIGHT),
                     self.colors['border'], 2)
        
        cv2.putText(frame, "ENEMY", (ex, ey - 10), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, self.colors['text'], 2)
        
        hp_text = f"{int(game_state.enemy_hp)}"
        (tw, th), _ = cv2.getTextSize(hp_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, hp_text, (ex + self.HP_BAR_WIDTH - tw, ey - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['text'], 2)
        
        return frame
    
    def _draw_hp_bar(self, frame: np.ndarray, x: int, y: int, width: int, height: int, 
                    hp_percentage: float, label: str, color: ColorTuple) -> None:
        """Helper to draw a single HP bar."""
        cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
        
        hp_width = int(width * (hp_percentage / 100))
        
        if hp_percentage > 60:
            bar_color = color
        elif hp_percentage > 30:
            bar_color = (0, 255, 255)
        else:
            bar_color = (0, 0, 255)
        
        cv2.rectangle(frame, (x, y), (x + hp_width, y + height), bar_color, -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)
        
        label_text = f"{label}: {int(hp_percentage)}%"
        cv2.putText(frame, label_text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def draw_stamina_bar(self, frame: np.ndarray, enemy_ai) -> np.ndarray:
        """Draw enemy stamina bar."""
        h, w = frame.shape[:2]
        stamina_pct = enemy_ai.get_stamina_percentage()
        
        bar_width = 300
        bar_height = 15
        x = w - 20 - bar_width
        y = 80
        
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (30, 30, 30), -1)
        
        stamina_width = int(bar_width * (stamina_pct / 100))
        cv2.rectangle(frame, (x, y), (x + stamina_width, y + bar_height), (255, 255, 0), -1)
        
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (150, 150, 150), 1)
        cv2.putText(frame, "STAMINA", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return frame
    
    def draw_round_info(self, frame: np.ndarray, round_manager, current_time: float) -> np.ndarray:
        """Draw clean round information with score."""
        h, w = frame.shape[:2]
        
        px = (w - self.ROUND_PANEL_WIDTH) // 2
        py = 15
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (px, py), (px + self.ROUND_PANEL_WIDTH, py + self.ROUND_PANEL_HEIGHT),
                     self.colors['bg_dark'], -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        cv2.rectangle(frame, (px, py), (px + self.ROUND_PANEL_WIDTH, py + self.ROUND_PANEL_HEIGHT),
                     self.colors['border'], 2)
        
        round_text = f"ROUND {round_manager.current_round}/{round_manager.total_rounds}"
        (tw, th), _ = cv2.getTextSize(round_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        tx = px + (self.ROUND_PANEL_WIDTH - tw) // 2
        cv2.putText(frame, round_text, (tx, py + 25), cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, self.colors['text'], 2)
        
        score_text = f"{round_manager.player_round_wins}  -  {round_manager.enemy_round_wins}"
        (tw, th), _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        tx = px + (self.ROUND_PANEL_WIDTH - tw) // 2
        cv2.putText(frame, score_text, (tx, py + 55), cv2.FONT_HERSHEY_SIMPLEX,
                   1.0, self.colors['text'], 2)
        
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
            
        timer_y = py + self.ROUND_PANEL_HEIGHT + 25
        (tw, th), _ = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        tx = px + (self.ROUND_PANEL_WIDTH - tw) // 2
        cv2.putText(frame, timer_text, (tx, timer_y), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, timer_color, 2)
        
        return frame
    
    def draw_stats_overlay(self, frame: np.ndarray, game_state) -> np.ndarray:
        """Draw statistics overlay."""
        h, w = frame.shape[:2]
        stats = game_state.get_stats_summary()
        
        x = w - 250
        y = h - 150
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (x - 10, y - 30), (x + 240, y + 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        
        cv2.putText(frame, "=== STATS ===", (x, y), font, font_scale, (0, 255, 255), 1)
        cv2.putText(frame, f"Punches: {stats['player_punches']}", (x, y + 25), font, font_scale, color, 1)
        cv2.putText(frame, f"Accuracy: {stats['player_accuracy']:.1f}%", (x, y + 45), font, font_scale, color, 1)
        cv2.putText(frame, f"Blocks: {stats['blocks']}", (x, y + 65), font, font_scale, color, 1)
        cv2.putText(frame, f"Hits Taken: {stats['enemy_hits']}", (x, y + 85), font, font_scale, color, 1)
        
        return frame
    
    def draw_combo_indicator(self, frame: np.ndarray, enemy_ai) -> np.ndarray:
        """Draw combo indicator when enemy is doing combo."""
        if not enemy_ai.in_combo:
            return frame
        
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        text = f"COMBO x{enemy_ai.combo_count + 1}/{enemy_ai.max_combo}"
        (text_w, text_h), _ = cv2.getTextSize(text, font, 1.0, 3)
        x = (w - text_w) // 2
        y = h // 2
        
        color = (0, 150, 255)
        
        cv2.putText(frame, text, (x, y), font, 1.0, (0, 0, 0), 5)
        cv2.putText(frame, text, (x, y), font, 1.0, color, 3)
        
        return frame
    
    def draw_vulnerable_indicator(self, frame: np.ndarray, enemy_ai) -> np.ndarray:
        """Draw clean vulnerable indicator."""
        if not enemy_ai.is_vulnerable():
            return frame
        
        h, w = frame.shape[:2]
        
        px = (w - self.VULNERABLE_PANEL_WIDTH) // 2
        py = int(h * 0.45)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (px, py), (px + self.VULNERABLE_PANEL_WIDTH, py + self.VULNERABLE_PANEL_HEIGHT),
                     self.colors['vulnerable'], -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        cv2.rectangle(frame, (px, py), (px + self.VULNERABLE_PANEL_WIDTH, py + self.VULNERABLE_PANEL_HEIGHT),
                     (255, 255, 255), 2)
        
        text = "HIT NOW!"
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 3)
        tx = px + (self.VULNERABLE_PANEL_WIDTH - text_w) // 2
        ty = py + 45
        
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 5)
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
        
        return frame
    
    def draw_hit_flash(self, frame: np.ndarray, current_time: float) -> np.ndarray:
        """Draw red flash effect when hit."""
        if current_time - self.hit_flash_time < self.HIT_FLASH_DURATION:
            overlay = frame.copy()
            overlay[:] = (0, 0, 150)
            alpha = 1.0 - (current_time - self.hit_flash_time) / self.HIT_FLASH_DURATION
            cv2.addWeighted(overlay, alpha * 0.3, frame, 1 - alpha * 0.3, 0, frame)
        
        return frame
    
    def trigger_hit_flash(self) -> None:
        """Trigger hit flash effect."""
        self.hit_flash_time = time.time()
    
    def draw_game_over(self, frame: np.ndarray, game_state) -> np.ndarray:
        """Draw game over screen."""
        if not game_state.game_over:
            return frame
        
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        text = "KNOCKOUT!"
        (text_w, text_h), _ = cv2.getTextSize(text, font, 3.0, 7)
        x = (w - text_w) // 2
        y = h // 2 - 50
        cv2.putText(frame, text, (x, y), font, 3.0, (0, 0, 255), 7)
        
        winner_text = f"{game_state.winner} WINS!"
        (text_w, text_h), _ = cv2.getTextSize(winner_text, font, 2.0, 5)
        x = (w - text_w) // 2
        y = h // 2 + 50
        
        color = (0, 255, 0) if game_state.winner == "PLAYER" else (0, 0, 255)
        cv2.putText(frame, winner_text, (x, y), font, 2.0, color, 5)
        
        restart_text = "Press SPACE to restart"
        (text_w, text_h), _ = cv2.getTextSize(restart_text, font, 0.8, 2)
        x = (w - text_w) // 2
        y = h // 2 + 120
        cv2.putText(frame, restart_text, (x, y), font, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def show_round_start(self, round_number: int) -> None:
        """Trigger round start notification."""
        self.round_start_notification = {
            'time': time.time(),
            'text': f"ROUND {round_number} START!"
        }
    
    def draw_round_notification(self, frame: np.ndarray, current_time: float) -> np.ndarray:
        """Draw round start notification banner."""
        if not self.round_start_notification:
            return frame
        
        elapsed = current_time - self.round_start_notification['time']
        if elapsed > self.NOTIFICATION_DURATION:
            self.round_start_notification = None
            return frame
        
        h, w = frame.shape[:2]
        
        fade_out = 1.0 if elapsed < (self.NOTIFICATION_DURATION - 0.5) else (self.NOTIFICATION_DURATION - elapsed) * 2
        alpha = min(1.0, fade_out)
        
        panel_width = 500
        panel_height = 80
        px = (w - panel_width) // 2
        py = int(h * 0.3)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (px, py), (px + panel_width, py + panel_height),
                     self.colors['accent'], -1)
        cv2.addWeighted(overlay, alpha * 0.9, frame, 1 - alpha * 0.9, 0, frame)
        
        cv2.rectangle(frame, (px, py), (px + panel_width, py + panel_height), (255, 255, 255), 3)
        
        text = self.round_start_notification['text']
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)
        tx = px + (panel_width - tw) // 2
        ty = py + (panel_height + th) // 2
        
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 6)
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4)
        
        return frame

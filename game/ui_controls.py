"""UI Controls Guide for Shadow Boxing."""
from typing import Dict, List, Tuple

import cv2
import numpy as np


ColorTuple = Tuple[int, int, int]
ControlItem = Dict[str, str]


class ControlsGuide:
    """Displays keyboard controls guide overlay."""
    
    PANEL_WIDTH = 380
    ITEM_HEIGHT = 45
    PADDING = 15
    KEY_HEIGHT = 30
    MIN_KEY_WIDTH = 80
    
    def __init__(self):
        self.visible = True
        self.controls: List[ControlItem] = [
            {'key': 'SPACE', 'action': 'Start Round / Restart'},
            {'key': 'Q', 'action': 'Quit Game'},
            {'key': 'D', 'action': 'Change Difficulty'},
            {'key': 'S', 'action': 'Toggle Sound'},
            {'key': 'H', 'action': 'Toggle This Guide'},
        ]
        
        self.colors: Dict[str, ColorTuple] = {
            'bg': (30, 30, 35),
            'key_bg': (70, 70, 75),
            'text': (255, 255, 255),
            'accent': (180, 130, 230),
            'border': (200, 200, 200),
        }
    
    def toggle(self) -> bool:
        """Toggle guide visibility."""
        self.visible = not self.visible
        return self.visible
    
    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Draw controls guide overlay on frame."""
        if not self.visible:
            return frame
        
        h, w = frame.shape[:2]
        
        panel_height = len(self.controls) * self.ITEM_HEIGHT + self.PADDING * 2 + 40
        
        px = w - self.PANEL_WIDTH - 20
        py = h - panel_height - 20
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (px, py), (px + self.PANEL_WIDTH, py + panel_height),
                     self.colors['bg'], -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        cv2.rectangle(frame, (px, py), (px + self.PANEL_WIDTH, py + panel_height),
                     self.colors['border'], 2)
        
        title = "CONTROLS"
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize(title, font, 0.7, 2)
        tx = px + (self.PANEL_WIDTH - tw) // 2
        ty = py + self.PADDING + 20
        cv2.putText(frame, title, (tx, ty), font, 0.7, self.colors['accent'], 2)
        
        y_offset = ty + 15
        
        for control in self.controls:
            y_offset += self.ITEM_HEIGHT
            
            key_text = control['key']
            (kw, kh), _ = cv2.getTextSize(key_text, font, 0.5, 1)
            key_width = max(self.MIN_KEY_WIDTH, kw + 20)
            
            key_x = px + self.PADDING + 10
            key_y = y_offset - self.KEY_HEIGHT + 5
            
            cv2.rectangle(frame, (key_x, key_y), (key_x + key_width, key_y + self.KEY_HEIGHT),
                         self.colors['key_bg'], -1)
            
            cv2.rectangle(frame, (key_x, key_y), (key_x + key_width, key_y + self.KEY_HEIGHT),
                         self.colors['accent'], 2)
            
            ktx = key_x + (key_width - kw) // 2
            kty = key_y + (self.KEY_HEIGHT + kh) // 2
            cv2.putText(frame, key_text, (ktx, kty), font, 0.5, self.colors['text'], 1)
            
            action_text = control['action']
            action_x = key_x + key_width + 15
            action_y = y_offset
            cv2.putText(frame, action_text, (action_x, action_y), font, 0.45, 
                       self.colors['text'], 1)
        
        return frame


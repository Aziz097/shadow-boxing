import time
from core import config, math_utils

class DefenseDetector:
    def __init__(self, game_config):
        self.config = game_config
        self.last_defense_time = 0
        self.defense_active = False
    
    def detect_defense(self, left_hand, right_hand, face_bbox, current_time):
        """Detect defense gesture using hands covering face"""
        # Check for defense cooldown
        if current_time - self.last_defense_time < 0.1:  # 100ms cooldown
            return self.defense_active
        
        if face_bbox is None or left_hand is None or right_hand is None:
            self.defense_active = False
            return False
        
        # Get face center and radius
        face_x, face_y, face_w, face_h = face_bbox
        face_center = (face_x + face_w//2, face_y + face_h//2)
        face_radius = max(face_w, face_h) // 2
        
        # Calculate distance from hands to face center
        left_dist = math_utils.distance(left_hand, face_center)
        right_dist = math_utils.distance(right_hand, face_center)
        
        # Check if both hands are close to face
        if (left_dist < face_radius * 0.8) and (right_dist < face_radius * 0.8):
            self.defense_active = True
            self.last_defense_time = current_time
            return True
        
        self.defense_active = False
        return False
    
    def is_defense_active(self):
        """Check if defense is currently active"""
        return self.defense_active
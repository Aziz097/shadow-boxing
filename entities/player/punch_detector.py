import numpy as np
from core import config, math_utils

class PunchDetector:
    def __init__(self, game_config):
        self.config = game_config
        self.last_punch_time = 0
        self.prev_wrist_positions = {
            'Left': None,
            'Right': None
        }
        self.prev_times = {
            'Left': 0,
            'Right': 0
        }
    
    def detect_punch(self, hand_landmarks, hand_label, current_time):
        """Detect punch using the calibrated algorithm"""
        # Check cooldown
        if current_time - self.last_punch_time < self.config.PUNCH_COOLDOWN:
            return False
        
        # Check if fist
        if not self._is_fist(hand_landmarks):
            return False
        
        # Get wrist position
        wrist_pos = (
            int(hand_landmarks[0].x * self.config.CAMERA_WIDTH),
            int(hand_landmarks[0].y * self.config.CAMERA_HEIGHT)
        )
        
        prev_pos = self.prev_wrist_positions[hand_label]
        prev_time = self.prev_times[hand_label]
        
        # Calculate velocity if we have previous position
        if prev_pos is not None and prev_time > 0:
            time_delta = current_time - prev_time
            if time_delta > 0.001:  # Avoid division by zero
                vel_x = (wrist_pos[0] - prev_pos[0]) / time_delta
                vel_y = (wrist_pos[1] - prev_pos[1]) / time_delta
                velocity = np.sqrt(vel_x**2 + vel_y**2)
                
                # Check if velocity exceeds threshold
                if velocity > self.config.VELOCITY_THRESHOLD:
                    self.last_punch_time = current_time
                    return True
        
        # Update previous position
        self.prev_wrist_positions[hand_label] = wrist_pos
        self.prev_times[hand_label] = current_time
        return False
    
    def _is_fist(self, landmarks):
        """Detect if hand is making a fist using the calibrated algorithm"""
        # Calculate angles for fingers (except thumb)
        angles = []
        for tip_id in [8, 12, 16, 20]:  # Index, middle, ring, pinky tips
            base_id = tip_id - 2  # Base of finger
            mid_id = tip_id - 1   # Middle joint
            
            # Calculate angle at middle joint
            angle = math_utils.calculate_angle(
                (landmarks[tip_id].x, landmarks[tip_id].y),
                (landmarks[mid_id].x, landmarks[mid_id].y),
                (landmarks[base_id].x, landmarks[base_id].y)
            )
            angles.append(angle)
        
        avg_angle = np.mean(angles) if angles else 180
        
        # Calculate distances from fingertips to palm (landmark 9)
        palm = (landmarks[9].x, landmarks[9].y)
        distances = []
        for tip_id in [8, 12, 16, 20]:
            tip = (landmarks[tip_id].x, landmarks[tip_id].y)
            distances.append(math_utils.distance(tip, palm))
        
        avg_dist = np.mean(distances) if distances else 1.0
        
        # Apply calibrated thresholds
        return (avg_angle < self.config.FIST_ANGLE_THRESHOLD and 
                avg_dist < self.config.FIST_DISTANCE_THRESHOLD)
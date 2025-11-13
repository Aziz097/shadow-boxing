"""
Input Processor - Clean Version
Handles fist detection, hit box punching, and defense with landmark 9 (middle_finger_mcp)
"""
import time
import numpy as np
from core import config, constants
from core.math_utils import calculate_angle, distance

class InputProcessor:
    def __init__(self, game_config):
        self.config = game_config
        self.last_punch_time = 0
        self.defense_active = False
        self.hand_states = {
            'Left': {'is_fist': False, 'position': None, 'landmark_9': None},
            'Right': {'is_fist': False, 'position': None, 'landmark_9': None}
        }
    
    def process_input(self, vision_data, game_state):
        """Process input from vision system and update game state"""
        current_time = time.time()
        
        # Reset per-frame states
        self.defense_active = False
        self.hand_states = {
            'Left': {'is_fist': False, 'position': None, 'landmark_9': None},
            'Right': {'is_fist': False, 'position': None, 'landmark_9': None}
        }
        
        # Process hand landmarks
        if vision_data['hands'].multi_hand_landmarks and vision_data['hands'].multi_handedness:
            for idx, hand_landmarks in enumerate(vision_data['hands'].multi_hand_landmarks):
                hand_label = vision_data['hands'].multi_handedness[idx].classification[0].label
                
                landmarks = hand_landmarks.landmark
                
                # Get hand position (wrist - landmark 0)
                hand_pos = (
                    int(landmarks[0].x * self.config.CAMERA_WIDTH),
                    int(landmarks[0].y * self.config.CAMERA_HEIGHT)
                )
                
                # Get landmark 9 position (middle_finger_mcp) for defense
                landmark_9_pos = (
                    int(landmarks[9].x * self.config.CAMERA_WIDTH),
                    int(landmarks[9].y * self.config.CAMERA_HEIGHT)
                )
                
                # Check if fist
                is_fist = self._is_fist(landmarks)
                
                # Store hand state
                self.hand_states[hand_label] = {
                    'is_fist': is_fist,
                    'position': hand_pos,
                    'landmark_9': landmark_9_pos
                }
                
                # Process based on game phase
                if game_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
                    # Player attack - check for punch hits
                    if is_fist and hasattr(game_state, 'hitbox_system'):
                        hit_result = game_state.hitbox_system.check_hit(
                            hand_pos[0], hand_pos[1], is_fist
                        )
                        
                        if hit_result:
                            # Apply damage to enemy
                            game_state.enemy_health -= hit_result['damage']
                            game_state.combo_count = hit_result['combo']
                            game_state.score += hit_result['damage'] * hit_result['combo']
                            
                            # Trigger VFX
                            if not hasattr(game_state, 'vfx_hits'):
                                game_state.vfx_hits = []
                            
                            game_state.vfx_hits.append({
                                'position': hit_result['position'],
                                'damage': hit_result['damage'],
                                'time': current_time
                            })
                            
                            # Play sound
                            if hasattr(game_state, 'play_sound'):
                                if hit_result['combo'] >= 3:
                                    game_state.play_sound("strong_punch")
                                else:
                                    game_state.play_sound("weak_punch")
        
        # Check defense during enemy attack
        if game_state.phase in [constants.PHASE_STATES['ENEMY_ATTACK_WARNING'], 
                               constants.PHASE_STATES['ENEMY_ATTACK']]:
            self._check_defense(game_state)
        
        # Store defense status
        game_state.defense_active = self.defense_active
        
        return None
    
    def _is_fist(self, landmarks):
        """Detect if hand is making a fist"""
        # Calculate angles for fingers (except thumb)
        angles = []
        for tip_id in [8, 12, 16, 20]:  # Index, middle, ring, pinky tips
            base_id = tip_id - 2
            mid_id = tip_id - 1
            
            angle = calculate_angle(
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
            distances.append(distance(tip, palm))
        
        avg_dist = np.mean(distances) if distances else 1.0
        
        # Apply calibrated thresholds
        return (avg_angle < self.config.FIST_ANGLE_THRESHOLD and 
                avg_dist < self.config.FIST_DISTANCE_THRESHOLD)
    
    def _check_defense(self, game_state):
        """Check if both hands' landmark 9 are in face bbox"""
        if game_state.face_bbox is None:
            return
        
        # Get landmark 9 positions from both hands
        left_lm9 = self.hand_states['Left']['landmark_9']
        right_lm9 = self.hand_states['Right']['landmark_9']
        
        if left_lm9 is None or right_lm9 is None:
            return
        
        face_x, face_y, face_w, face_h = game_state.face_bbox
        
        # Check if both landmark 9 are inside face bbox
        left_in_face = (face_x <= left_lm9[0] <= face_x + face_w and 
                       face_y <= left_lm9[1] <= face_y + face_h)
        
        right_in_face = (face_x <= right_lm9[0] <= face_x + face_w and 
                        face_y <= right_lm9[1] <= face_y + face_h)
        
        if left_in_face and right_in_face:
            self.defense_active = True
    
    def get_defense_status(self):
        """Get current defense status"""
        return self.defense_active
    
    def get_hand_states(self):
        """Get current hand states"""
        return self.hand_states

import time
import numpy as np
from core import config, constants
from core.math_utils import calculate_angle, distance, calculate_velocity

class InputProcessor:
    def __init__(self, game_config):
        self.config = game_config
        self.last_punch_time = 0
        self.last_defense_time = 0
        self.defense_active = False
        self.prev_hand_positions = {
            'Left': None,
            'Right': None
        }
        self.prev_hand_times = {
            'Left': 0,
            'Right': 0
        }
        self.hitbox_hits = []  # Track hitbox hits for combo system
    
    def process_input(self, vision_data, game_state):
        """
        Process input from vision system and update game state
        Returns: command (e.g., "RESTART") or None
        """
        # Reset state
        self.defense_active = False
        
        # Process hand landmarks
        if vision_data['hands'].multi_hand_landmarks and vision_data['hands'].multi_handedness:
            for idx, hand_landmarks in enumerate(vision_data['hands'].multi_hand_landmarks):
                hand_label = vision_data['hands'].multi_handedness[idx].classification[0].label
                
                # Get hand position
                hand_pos = self._get_hand_position(hand_landmarks.landmark)
                
                # Check if fist
                is_fist = self._is_fist(hand_landmarks.landmark)
                
                # Process based on current game phase
                if game_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
                    self._process_player_attack(hand_label, hand_pos, is_fist, game_state)
                elif game_state.phase in [constants.PHASE_STATES['ENEMY_ATTACK_WARNING'], 
                                         constants.PHASE_STATES['ENEMY_ATTACK']]:
                    self._process_defense(hand_label, hand_pos, game_state)
        
        # Process face landmarks for defense fallback
        if game_state.phase in [constants.PHASE_STATES['ENEMY_ATTACK_WARNING'], 
                               constants.PHASE_STATES['ENEMY_ATTACK']]:
            self._process_face_defense(vision_data['face'], game_state)
        
        return None
    
    def _get_hand_position(self, landmarks):
        """Get hand position from landmarks"""
        # Use wrist landmark (0) for position
        return (
            int(landmarks[0].x * self.config.CAMERA_WIDTH),
            int(landmarks[0].y * self.config.CAMERA_HEIGHT)
        )
    
    def _is_fist(self, landmarks):
        """Detect if hand is making a fist using the calibrated algorithm"""
        # Calculate angles for fingers (except thumb)
        angles = []
        for tip_id in [8, 12, 16, 20]:  # Index, middle, ring, pinky tips
            base_id = tip_id - 2  # Base of finger
            mid_id = tip_id - 1   # Middle joint
            
            # Calculate angle at middle joint
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
    
    def _process_player_attack(self, hand_label, hand_pos, is_fist, game_state):
        """Process player attack during hitbox phase"""
        if not is_fist:
            return
        
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_punch_time < self.config.PUNCH_COOLDOWN:
            return
        
        # Check if hand is in any active hitbox
        for hitbox in game_state.active_hitboxes:
            if hitbox in game_state.hit_hitboxes:
                continue  # Already hit
            
            if self._is_point_in_hitbox(hand_pos, hitbox):
                # Register hit
                game_state.hit_hitboxes.append(hitbox)
                game_state.combo_count += 1
                self.last_punch_time = current_time
                
                # Add to hit history for scoring
                self.hitbox_hits.append({
                    'time': current_time,
                    'position': hand_pos
                })
                
                # Trigger VFX
                game_state.add_vfx(hand_pos[0], hand_pos[1], "punch_impact")
                
                # Play sound
                if game_state.combo_count >= 3:
                    game_state.play_sound("strong_punch")
                else:
                    game_state.play_sound("weak_punch")
                
                break
    
    def _is_point_in_hitbox(self, point, hitbox):
        """Check if point is inside hitbox"""
        x, y, w, h = hitbox
        px, py = point
        return x <= px <= x + w and y <= py <= y + h
    
    def _process_defense(self, hand_label, hand_pos, game_state):
        """Process defense gestures"""
        current_time = time.time()
        
        # Store hand position for velocity calculation
        if self.prev_hand_positions[hand_label] is not None:
            prev_pos = self.prev_hand_positions[hand_label]
            prev_time = self.prev_hand_times[hand_label]
            
            # Calculate velocity
            velocity_vec, velocity_mag = calculate_velocity(prev_pos, hand_pos, current_time - prev_time)
            
            # Check if hand is moving toward face quickly (dodge)
            if velocity_mag > 600:  # pixels per second
                game_state.dodge_detected = True
        
        # Update hand tracking
        self.prev_hand_positions[hand_label] = hand_pos
        self.prev_hand_times[hand_label] = current_time
    
    def _process_face_defense(self, face_results, game_state):
        """Process defense using face landmarks"""
        if not face_results.multi_face_landmarks:
            return
        
        landmarks = face_results.multi_face_landmarks[0].landmark
        
        # Get face bounding box
        x_coords = [lm.x for lm in landmarks]
        y_coords = [lm.y for lm in landmarks]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        face_bbox = (
            int(x_min * self.config.CAMERA_WIDTH),
            int(y_min * self.config.CAMERA_HEIGHT),
            int((x_max - x_min) * self.config.CAMERA_WIDTH),
            int((y_max - y_min) * self.config.CAMERA_HEIGHT)
        )
        
        # Check hand positions relative to face
        left_hand = self.prev_hand_positions.get('Left')
        right_hand = self.prev_hand_positions.get('Right')
        
        if left_hand and right_hand:
            # Calculate coverage percentage
            face_center = (face_bbox[0] + face_bbox[2]//2, face_bbox[1] + face_bbox[3]//2)
            face_radius = max(face_bbox[2], face_bbox[3]) // 2
            
            left_dist = distance(left_hand, face_center)
            right_dist = distance(right_hand, face_center)
            
            # If both hands are close to face center
            if (left_dist < face_radius * 0.7) and (right_dist < face_radius * 0.7):
                self.defense_active = True
                game_state.defense_active = True
    
    def get_defense_status(self):
        """Get current defense status"""
        return self.defense_active
    
    def reset_hitbox_tracking(self):
        """Reset hitbox tracking for new phase"""
        self.hitbox_hits = []
        self.last_punch_time = 0
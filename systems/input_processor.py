"""Input processor - detects fist punches, hitbox collision, and defense."""

import time
import numpy as np
from core import constants
from core.math_utils import calculate_angle, distance

class InputProcessor:
    def __init__(self, game_config):
        self.config = game_config
        self.last_punch_time = 0
        self.defense_active = False
        self.hand_states = {
            'Left': {'is_fist': False, 'position': None, 'landmark_9': None, 'fingertips': []},
            'Right': {'is_fist': False, 'position': None, 'landmark_9': None, 'fingertips': []}
        }
    
    def process_input(self, vision_data, game_state):
        """Process input from vision system and update game state"""
        current_time = time.time()
        
        # Reset per-frame states
        self.defense_active = False
        self.hand_states = {
            'Left': {'is_fist': False, 'position': None, 'landmark_9': None, 'fingertips': []},
            'Right': {'is_fist': False, 'position': None, 'landmark_9': None, 'fingertips': []}
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
                
                # Get fingertip positions (8=index, 12=middle, 16=ring, 20=pinky)
                fingertips = []
                for tip_id in [8, 12, 16, 20]:
                    tip_pos = (
                        int(landmarks[tip_id].x * self.config.CAMERA_WIDTH),
                        int(landmarks[tip_id].y * self.config.CAMERA_HEIGHT)
                    )
                    fingertips.append(tip_pos)
                
                # Check if fist
                is_fist = self._is_fist(landmarks)
                
                # Print key hand landmarks for debugging (only on hit)
                # Reduced printing to avoid spam - will print on actual hits
                
                # Store hand state
                self.hand_states[hand_label] = {
                    'is_fist': is_fist,
                    'position': hand_pos,
                    'landmark_9': landmark_9_pos,
                    'fingertips': fingertips
                }
                
                # Process based on game phase
                if game_state.phase == constants.PHASE_STATES['PLAYER_ATTACK']:
                    # Player attack - check for punch hits using ANY hand landmark (3-20)
                    if is_fist and hasattr(game_state, 'hitbox_system'):
                        # Check all landmarks from index 3-20 (exclude wrist 0,1,2)
                        hit_result = None
                        for landmark_idx in range(3, 21):
                            lm_x = int(landmarks[landmark_idx].x * self.config.CAMERA_WIDTH)
                            lm_y = int(landmarks[landmark_idx].y * self.config.CAMERA_HEIGHT)
                            
                            hit_result = game_state.hitbox_system.check_hit(lm_x, lm_y, is_fist)
                            if hit_result:
                                break  # Stop checking once we found a hit
                        
                        if hit_result:
                            # Print hand landmarks on successful hit
                            damage = hit_result.get('damage', 0)
                            is_last = hit_result.get('is_last_hit', False)
                            punch_type = hit_result.get('punch_type', 'PUNCH')
                            
                            print(f"\n🤛 {hand_label} FIST HIT - Key landmarks:")
                            print(f"   Wrist[0]: ({hand_pos[0]:4d}, {hand_pos[1]:4d})")
                            print(f"   MCP[9]:   ({landmark_9_pos[0]:4d}, {landmark_9_pos[1]:4d})")
                            for i, tip in enumerate(fingertips):
                                tip_names = ['Index', 'Middle', 'Ring', 'Pinky']
                                print(f"   {tip_names[i]:6s}:  ({tip[0]:4d}, {tip[1]:4d})")
                            
                            # Apply damage immediately to enemy
                            game_state.enemy_health = max(0, game_state.enemy_health - damage)
                            game_state.score += damage
                            
                            bonus_text = " (FINAL HIT +10%!)" if is_last else ""
                            print(f"💥 {punch_type} Hit! {damage} damage{bonus_text}")
                            print(f"   Enemy health: {game_state.enemy_health + damage} → {game_state.enemy_health}")
                            
                            # Register hit to combo system
                            hitbox_id = hit_result.get('hitbox_id')
                            if hitbox_id is not None:
                                game_state.register_hit(hitbox_id)
                            
                            # Spawn next hitbox if not last
                            if not is_last:
                                spawned = game_state.hitbox_system.spawn_next_hitbox()
                                if spawned:
                                    print(f"   → Next target spawned!")
                            
                            # Play player punch sound
                            game_state.play_sound('player-punch')
                            
                            # Trigger VFX
                            if not hasattr(game_state, 'vfx_hits'):
                                game_state.vfx_hits = []
                            
                            game_state.vfx_hits.append({
                                'position': hit_result['position'],
                                'damage': damage,
                                'time': current_time
                            })

        
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
        """Check if fingertips from either hand are near eye area (pose landmarks 1-6)"""
        # Reset defense status
        self.defense_active = False
        
        # Need pose landmarks for eye position detection
        if not hasattr(game_state, 'pose_landmarks') or game_state.pose_landmarks is None:
            return
        
        # Get eye area pose landmarks (1=left_eye_inner, 2=left_eye, 3=left_eye_outer, 4=right_eye_inner, 5=right_eye, 6=right_eye_outer)
        eye_landmarks_idx = [1, 2, 3, 4, 5, 6]
        eye_positions = []
        
        for idx in eye_landmarks_idx:
            if idx < len(game_state.pose_landmarks):
                landmark = game_state.pose_landmarks[idx]
                eye_x = int(landmark.x * self.config.CAMERA_WIDTH)
                eye_y = int(landmark.y * self.config.CAMERA_HEIGHT)
                eye_positions.append((eye_x, eye_y))
        
        if not eye_positions:
            return
        
        # Calculate average eye position
        avg_eye_x = sum(pos[0] for pos in eye_positions) // len(eye_positions)
        avg_eye_y = sum(pos[1] for pos in eye_positions) // len(eye_positions)
        
        # Defense threshold: fingertips within 150px of eye area
        defense_distance_threshold = 150
        
        # Check if any fingertips from either hand are near eyes
        left_fingertips = self.hand_states['Left']['fingertips']
        right_fingertips = self.hand_states['Right']['fingertips']
        
        hands_defending = 0
        
        # Check left hand fingertips
        if left_fingertips:
            for tip_pos in left_fingertips:
                dx = tip_pos[0] - avg_eye_x
                dy = tip_pos[1] - avg_eye_y
                distance = (dx**2 + dy**2)**0.5
                if distance < defense_distance_threshold:
                    hands_defending += 1
                    break
        
        # Check right hand fingertips
        if right_fingertips:
            for tip_pos in right_fingertips:
                dx = tip_pos[0] - avg_eye_x
                dy = tip_pos[1] - avg_eye_y
                distance = (dx**2 + dy**2)**0.5
                if distance < defense_distance_threshold:
                    hands_defending += 1
                    break
        
        # Defense active if at least one hand covering eyes
        if hands_defending >= 1:
            self.defense_active = True
    
    def get_defense_status(self):
        """Get current defense status"""
        return self.defense_active
    
    def get_hand_states(self):
        """Get current hand states"""
        return self.hand_states

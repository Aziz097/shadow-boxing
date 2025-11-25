"""Hitbox system - generates and manages player attack targets."""

import random
import time
import math
from core import constants

class HitBoxSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.active_hitboxes = []
        self.hit_hitboxes = set()
        self.hitbox_radius = 65
        self.sequential_mode = False  # Sequential: next hitbox spawns on hit
        self.current_hitbox_index = 0  # Track which hitbox should be active
        self.last_hit_position = None  # Remember last hitbox position to avoid overlap
        self.face_bbox = None  # Store for spawn_next_hitbox
        self.pose_landmarks = None  # Store for spawn_next_hitbox
        
    def generate_hitboxes(self, count=None, face_bbox=None, combo_sequence=None, pose_landmarks=None):
        """Generate hitboxes - sequential if combo_sequence provided, random otherwise"""
        if combo_sequence:
            # Sequential mode: next spawns only when previous is hit
            self.sequential_mode = True
            count = len(combo_sequence)
            self.current_hitbox_index = 0
            self.last_hit_position = None
        else:
            # Original random mode
            self.sequential_mode = False
            if count is None:
                count = random.randint(self.config.MIN_HITBOXES, self.config.MAX_HITBOXES)
        
        self.active_hitboxes = []
        self.hit_hitboxes = set()
        
        margin = self.config.HITBOX_MARGIN
        size = 130  # 130x130px untuk circle background + punch bag
        
        # Define face exclusion zone (larger than actual face for safety)
        face_zone = None
        if face_bbox:
            face_x, face_y, face_w, face_h = face_bbox
            # Expand face zone by 100px on all sides
            face_zone = {
                'x1': max(0, face_x - 100),
                'y1': max(0, face_y - 100),
                'x2': min(self.config.CAMERA_WIDTH, face_x + face_w + 100),
                'y2': min(self.config.CAMERA_HEIGHT, face_y + face_h + 100)
            }
        
        # Define body exclusion zones (shoulders 11,12 and hips 23,24 with 120px radius)
        body_zones = []
        if pose_landmarks:
            # MediaPipe pose landmarks: 11=left_shoulder, 12=right_shoulder, 23=left_hip, 24=right_hip
            body_landmark_indices = [11, 12, 23, 24]
            for idx in body_landmark_indices:
                if idx < len(pose_landmarks):
                    lm = pose_landmarks[idx]
                    body_x = int(lm.x * self.config.CAMERA_WIDTH)
                    body_y = int(lm.y * self.config.CAMERA_HEIGHT)
                    body_zones.append({'cx': body_x, 'cy': body_y, 'radius': 120})
        
        for i in range(count):
            placed = False
            attempts = 0  # Reset attempts counter per hitbox
            max_attempts = 100  # Per-hitbox attempt limit
            
            # Determine punch type first to decide position zone
            punch_type = "JAB"
            if combo_sequence and i < len(combo_sequence):
                punch_type = combo_sequence[i]
            
            while not placed and attempts < max_attempts:
                attempts += 1
                
                # Position based on punch type:
                # JAB = left side (0 to 50% width)
                # CROSS/HOOK = right side (50% to 100% width)
                if punch_type == "JAB":
                    # Left side for JAB
                    x = random.randint(margin, self.config.CAMERA_WIDTH // 2 - size)
                else:  # CROSS or HOOK
                    # Right side for CROSS/HOOK
                    x = random.randint(self.config.CAMERA_WIDTH // 2, self.config.CAMERA_WIDTH - margin - size)
                
                y = random.randint(margin + 150, self.config.CAMERA_HEIGHT - margin - size)  # Avoid HUD
                
                # Center point for circle
                center_x = x + size // 2
                center_y = y + size // 2
                
                # Check if hitbox is in face exclusion zone
                in_face_zone = False
                if face_zone:
                    # Check if hitbox center is in face zone
                    if (face_zone['x1'] <= center_x <= face_zone['x2'] and 
                        face_zone['y1'] <= center_y <= face_zone['y2']):
                        in_face_zone = True
                        continue  # Skip this position, try again
                
                # Check if hitbox is too close to body landmarks
                in_body_zone = False
                for body_zone in body_zones:
                    dist_to_body = math.sqrt((center_x - body_zone['cx'])**2 + (center_y - body_zone['cy'])**2)
                    if dist_to_body < body_zone['radius']:
                        in_body_zone = True
                        break
                
                if in_body_zone:
                    continue  # Skip this position, try again
                
                # Check if overlaps with existing hitboxes
                overlap = False
                for existing in self.active_hitboxes:
                    ex_center_x = existing['x'] + size // 2
                    ex_center_y = existing['y'] + size // 2
                    
                    # Calculate distance between centers
                    dist = math.sqrt((center_x - ex_center_x)**2 + (center_y - ex_center_y)**2)
                    
                    # Check if circles overlap - REDUCED spacing from 50px to 30px
                    if dist < (self.hitbox_radius * 2 + 30):  # 30px minimum spacing (was 50px)
                        overlap = True
                        break
                
                if not overlap and not in_face_zone and not in_body_zone:
                    # punch_type already determined at start of loop
                    hitbox = {
                        'id': i,
                        'x': x,
                        'y': y,
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': size,
                        'height': size,
                        'radius': self.hitbox_radius,
                        'active': not self.sequential_mode,  # Only first active in sequential mode
                        'visible': not self.sequential_mode,  # Control visibility
                        'hit_time': 0,
                        'type': random.choice(['red', 'blue', 'black']),
                        'punch_type': punch_type,
                        'sequence_index': i
                    }
                    self.active_hitboxes.append(hitbox)
                    placed = True
            
            # FALLBACK: If can't place after max attempts, relax constraints
            if not placed:
                print(f"⚠️ WARNING: Could not place hitbox {i} ({punch_type}) after {max_attempts} attempts")
                print(f"   Trying fallback with reduced exclusion zones...")
                
                # Try again with VERY relaxed constraints
                for fallback_attempt in range(100):
                    # Wider random range for fallback
                    if punch_type == "JAB":
                        x = random.randint(margin, self.config.CAMERA_WIDTH // 2 - size)
                    else:
                        x = random.randint(self.config.CAMERA_WIDTH // 2, self.config.CAMERA_WIDTH - margin - size)
                    
                    y = random.randint(margin + 100, self.config.CAMERA_HEIGHT - margin - size)  # Reduced top margin
                    center_x = x + size // 2
                    center_y = y + size // 2
                    
                    # Only check MINIMAL face zone in fallback (50px instead of 100px)
                    if face_zone:
                        face_zone_mini = {
                            'x1': max(0, face_x - 50),
                            'y1': max(0, face_y - 50),
                            'x2': min(self.config.CAMERA_WIDTH, face_x + face_w + 50),
                            'y2': min(self.config.CAMERA_HEIGHT, face_y + face_h + 50)
                        }
                        if (face_zone_mini['x1'] <= center_x <= face_zone_mini['x2'] and 
                            face_zone_mini['y1'] <= center_y <= face_zone_mini['y2']):
                            continue
                    
                    # Check overlap with REDUCED spacing (20px instead of 50px)
                    overlap = False
                    for existing in self.active_hitboxes:
                        ex_center_x = existing['x'] + size // 2
                        ex_center_y = existing['y'] + size // 2
                        dist = math.sqrt((center_x - ex_center_x)**2 + (center_y - ex_center_y)**2)
                        if dist < (self.hitbox_radius * 2 + 20):  # REDUCED from 50px to 20px
                            overlap = True
                            break
                    
                    if not overlap:
                        hitbox = {
                            'id': i,
                            'x': x,
                            'y': y,
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': size,
                            'height': size,
                            'radius': self.hitbox_radius,
                            'active': not self.sequential_mode,
                            'visible': not self.sequential_mode,
                            'hit_time': 0,
                            'type': random.choice(['red', 'blue', 'black']),
                            'punch_type': punch_type,
                            'sequence_index': i
                        }
                        self.active_hitboxes.append(hitbox)
                        placed = True
                        print(f"   ✓ Fallback placement successful at ({center_x}, {center_y})")
                        break
                
                if not placed:
                    print(f"   ✗ CRITICAL: Still failed after fallback! Using FORCE placement...")
                    # FORCE PLACEMENT: Place without any checks (last resort)
                    if punch_type == "JAB":
                        x = random.randint(margin + 50, self.config.CAMERA_WIDTH // 2 - size - 50)
                    else:
                        x = random.randint(self.config.CAMERA_WIDTH // 2 + 50, self.config.CAMERA_WIDTH - margin - size - 50)
                    
                    y = random.randint(margin + 200, self.config.CAMERA_HEIGHT - margin - size - 50)
                    center_x = x + size // 2
                    center_y = y + size // 2
                    
                    hitbox = {
                        'id': i,
                        'x': x,
                        'y': y,
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': size,
                        'height': size,
                        'radius': self.hitbox_radius,
                        'active': not self.sequential_mode,
                        'visible': not self.sequential_mode,
                        'hit_time': 0,
                        'type': random.choice(['red', 'blue', 'black']),
                        'punch_type': punch_type,
                        'sequence_index': i
                    }
                    self.active_hitboxes.append(hitbox)
                    print(f"   ⚡ FORCE placed at ({center_x}, {center_y})")
        
        # Debug: Print hitbox generation summary
        print(f"\n📦 Hitbox Generation Summary:")
        print(f"   Requested: {count} hitboxes")
        print(f"   Generated: {len(self.active_hitboxes)} hitboxes")
        if combo_sequence:
            print(f"   Combo: {' -> '.join(combo_sequence)}")
        for hb in self.active_hitboxes:
            status = "ACTIVE" if hb['active'] else "INACTIVE"
            print(f"   [{hb['id']}] {hb['punch_type']:5s} at ({hb['center_x']:4d}, {hb['center_y']:4d}) - {status}")
        
        # Store for spawn_next_hitbox
        self.face_bbox = face_bbox
        self.pose_landmarks = pose_landmarks
        
        # In sequential mode, only activate first hitbox
        if self.sequential_mode and self.active_hitboxes:
            self.active_hitboxes[0]['active'] = True
            self.active_hitboxes[0]['visible'] = True
            if self.active_hitboxes[0].get('center_x') and self.active_hitboxes[0].get('center_y'):
                self.last_hit_position = (self.active_hitboxes[0]['center_x'], self.active_hitboxes[0]['center_y'])
    
    def spawn_next_hitbox(self):
        """Spawn next hitbox in sequence after previous is hit"""
        if not self.sequential_mode:
            return False
        
        self.current_hitbox_index += 1
        
        # Check if there's a next hitbox to activate
        if self.current_hitbox_index < len(self.active_hitboxes):
            next_hitbox = self.active_hitboxes[self.current_hitbox_index]
            punch_type = next_hitbox.get('punch_type', 'JAB')
            
            # Build exclusion zones
            face_zone = None
            if self.face_bbox:
                face_x, face_y, face_w, face_h = self.face_bbox
                face_zone = {
                    'x1': max(0, face_x - 100),
                    'y1': max(0, face_y - 100),
                    'x2': min(self.config.CAMERA_WIDTH, face_x + face_w + 100),
                    'y2': min(self.config.CAMERA_HEIGHT, face_y + face_h + 100)
                }
            
            body_zones = []
            if self.pose_landmarks:
                body_landmark_indices = [11, 12, 23, 24]
                for idx in body_landmark_indices:
                    if idx < len(self.pose_landmarks):
                        lm = self.pose_landmarks[idx]
                        body_x = int(lm.x * self.config.CAMERA_WIDTH)
                        body_y = int(lm.y * self.config.CAMERA_HEIGHT)
                        body_zones.append({'cx': body_x, 'cy': body_y, 'radius': 120})
            
            # Regenerate position to avoid previous hit position and exclusion zones
            margin = self.config.HITBOX_MARGIN
            size = 130
            placed = False
            attempts = 0
            
            while attempts < 100 and not placed:
                attempts += 1
                
                # Position based on punch type
                if punch_type == "JAB":
                    # Left side for JAB
                    x = random.randint(margin, self.config.CAMERA_WIDTH // 2 - size)
                else:  # CROSS or HOOK
                    # Right side for CROSS/HOOK
                    x = random.randint(self.config.CAMERA_WIDTH // 2, self.config.CAMERA_WIDTH - margin - size)
                
                y = random.randint(margin + 150, self.config.CAMERA_HEIGHT - margin - size)
                
                center_x = x + size // 2
                center_y = y + size // 2
                
                # Check distance from last hit (must be 150px+ away)
                if self.last_hit_position:
                    dist = math.sqrt((center_x - self.last_hit_position[0])**2 + 
                                   (center_y - self.last_hit_position[1])**2)
                    if dist < 150:
                        continue
                
                # Check face exclusion zone
                if face_zone:
                    if (face_zone['x1'] <= center_x <= face_zone['x2'] and 
                        face_zone['y1'] <= center_y <= face_zone['y2']):
                        continue
                
                # Check body exclusion zones
                in_body_zone = False
                for body_zone in body_zones:
                    dist_to_body = math.sqrt((center_x - body_zone['cx'])**2 + (center_y - body_zone['cy'])**2)
                    if dist_to_body < body_zone['radius']:
                        in_body_zone = True
                        break
                
                if in_body_zone:
                    continue
                
                # Position is valid
                next_hitbox['x'] = x
                next_hitbox['y'] = y
                next_hitbox['center_x'] = center_x
                next_hitbox['center_y'] = center_y
                self.last_hit_position = (center_x, center_y)
                placed = True
            
            if not placed:
                print(f"⚠️ WARNING: spawn_next_hitbox failed for index {self.current_hitbox_index} ({punch_type})")
                print(f"   Using original position: ({next_hitbox['center_x']}, {next_hitbox['center_y']})")
                # Use the original pre-generated position as fallback
                if next_hitbox.get('center_x') and next_hitbox.get('center_y'):
                    self.last_hit_position = (next_hitbox['center_x'], next_hitbox['center_y'])
            else:
                print(f"✓ Spawned hitbox {self.current_hitbox_index} ({punch_type}) at ({center_x}, {center_y})")
            
            next_hitbox['active'] = True
            next_hitbox['visible'] = True
            return True
        
        return False
    
    def check_hit(self, hand_x, hand_y, is_fist):
        """Check if fist punch hits any active hitbox (circle collision)"""
        if not is_fist:
            return None
        
        for hitbox in self.active_hitboxes:
            if not hitbox['active'] or hitbox['id'] in self.hit_hitboxes:
                continue
            
            # Circle collision detection
            dist = math.sqrt((hand_x - hitbox['center_x'])**2 + (hand_y - hitbox['center_y'])**2)
            
            if dist <= hitbox['radius']:
                # Mark as hit
                hitbox['active'] = False
                hitbox['hit_time'] = time.time()
                self.hit_hitboxes.add(hitbox['id'])
                
                # Check if this is the last hitbox in combo
                is_last_hit = (len(self.hit_hitboxes) == len(self.active_hitboxes))
                
                # Get random damage from difficulty settings
                punch_type = hitbox.get('punch_type', 'JAB')
                difficulty = self.config.DEFAULT_DIFFICULTY
                damage_ranges = constants.DIFFICULTY_SETTINGS[difficulty]['player_damage_ranges']
                damage_range = damage_ranges.get(punch_type, (8, 12))
                
                # Random damage within range
                base_damage = random.randint(damage_range[0], damage_range[1])
                
                # Apply 1.1x multiplier for last hit
                damage = base_damage
                if is_last_hit:
                    damage = int(base_damage * 1.1)
                
                return {
                    'hitbox_id': hitbox['id'],
                    'damage': damage,
                    'combo': len(self.hit_hitboxes),
                    'position': (hitbox['center_x'], hitbox['center_y']),
                    'is_last_hit': is_last_hit,
                    'punch_type': punch_type
                }
        
        return None
    
    def _calculate_damage(self, combo_count):
        """Calculate damage based on combo"""
        if combo_count >= 4:
            return constants.DAMAGE_VALUES['COMBO_4']
        elif combo_count >= 3:
            return constants.DAMAGE_VALUES['COMBO_3']
        elif combo_count >= 2:
            return constants.DAMAGE_VALUES['COMBO_2']
        else:
            return constants.DAMAGE_VALUES['COMBO_1']
    
    def get_active_hitboxes(self):
        """Get list of active hitboxes"""
        return [hb for hb in self.active_hitboxes if hb['active']]
    
    def get_all_hitboxes(self):
        """Get all hitboxes including hit ones"""
        return self.active_hitboxes
    
    def get_hit_count(self):
        """Get number of hit hitboxes"""
        return len(self.hit_hitboxes)
    
    def clear(self):
        """Clear all hitboxes"""
        self.active_hitboxes = []
        self.hit_hitboxes = set()
    
    def all_hit(self):
        """Check if all hitboxes are hit"""
        return len(self.hit_hitboxes) == len(self.active_hitboxes)

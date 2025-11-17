"""Hitbox system - generates and manages player attack targets."""

import random
import time
import math
from core import constants

class HitBoxSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.active_hitboxes = []
        self.hit_hitboxes = set()  # Track which hitboxes were hit
        self.hitbox_radius = 65  # Half of 130px for circle collision
        
    def generate_hitboxes(self, count=None, face_bbox=None):
        """Generate random non-overlapping hitboxes in screen area, avoiding face area"""
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
        
        max_attempts = 100  # Prevent infinite loop
        attempts = 0
        
        for i in range(count):
            placed = False
            while not placed and attempts < max_attempts:
                attempts += 1
                
                # Generate random position with margin
                x = random.randint(margin, self.config.CAMERA_WIDTH - margin - size)
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
                
                # Check if overlaps with existing hitboxes
                overlap = False
                for existing in self.active_hitboxes:
                    ex_center_x = existing['x'] + size // 2
                    ex_center_y = existing['y'] + size // 2
                    
                    # Calculate distance between centers
                    dist = math.sqrt((center_x - ex_center_x)**2 + (center_y - ex_center_y)**2)
                    
                    # Check if circles overlap (with some spacing)
                    if dist < (self.hitbox_radius * 2 + 50):  # 50px minimum spacing
                        overlap = True
                        break
                
                if not overlap and not in_face_zone:
                    hitbox = {
                        'id': i,
                        'x': x,
                        'y': y,
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': size,
                        'height': size,
                        'radius': self.hitbox_radius,
                        'active': True,
                        'hit_time': 0,
                        'type': random.choice(['red', 'blue', 'black'])  # Punch bag colors
                    }
                    self.active_hitboxes.append(hitbox)
                    placed = True
    
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
                
                # Calculate damage based on combo
                damage = self._calculate_damage(len(self.hit_hitboxes))
                
                return {
                    'hitbox_id': hitbox['id'],
                    'damage': damage,
                    'combo': len(self.hit_hitboxes),
                    'position': (hitbox['center_x'], hitbox['center_y'])
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

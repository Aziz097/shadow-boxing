"""
Hit Box System for Player Attack Phase
Manages hitbox generation with non-overlapping placement, hit detection, and damage calculation
"""
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
        
    def generate_hitboxes(self, count=None):
        """Generate random non-overlapping hitboxes in screen area"""
        if count is None:
            count = random.randint(self.config.MIN_HITBOXES, self.config.MAX_HITBOXES)
        
        self.active_hitboxes = []
        self.hit_hitboxes = set()
        
        margin = self.config.HITBOX_MARGIN
        size = 130  # 130x130px untuk circle background + punch bag
        
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

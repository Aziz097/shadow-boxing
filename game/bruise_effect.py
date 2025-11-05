"""Bruise Effect System for Shadow Boxing."""
import os
import random
from typing import Dict, List

import cv2
import numpy as np


BruiseData = Dict[str, object]  # {'image': ndarray, 'position': tuple, 'alpha': float, 'time': float, 'landmark_idx': int, 'type': str}


class BruiseEffect:
    """Manages bruise overlay effects on player's face."""
    
    DURATION = 5.0
    FADE_DURATION = 2.0
    INITIAL_ALPHA = 0.8
    EYE_SCALE = 0.15
    NORMAL_SCALE = 0.2
    
    FACE_LANDMARKS = {
        'left_cheek': 234,
        'right_cheek': 454,
        'forehead': 10,
        'left_eye': 33,
        'right_eye': 263,
        'jaw_left': 172,
        'jaw_right': 397,
    }
    
    def __init__(self):
        self.bruises: List[BruiseData] = []
        self.bruise_images: Dict[str, np.ndarray] = {}
        self._load_bruise_images()
        
    def _load_bruise_images(self) -> None:
        """Load bruise PNG images with transparency."""
        base_path = os.path.join(os.getcwd(), 'assets', 'vfx')
        
        bruise_files = {
            'bruise': 'bruise.png',
            'blackeye': 'blackeyebruise.png',
        }
        
        for name, filename in bruise_files.items():
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    self.bruise_images[name] = img
                    print(f"✓ Loaded bruise image: {name} ({img.shape})")
                else:
                    print(f"✗ Failed to load bruise: {path}")
            else:
                print(f"✗ Bruise image not found: {path}")
    
    def add_bruise(self, face_landmarks, frame_width: int, frame_height: int, current_time: float) -> None:
        """Add a new bruise at random face position."""
        if not self.bruise_images:
            return
        
        bruise_type = random.choice(list(self.bruise_images.keys()))
        position_name = random.choice(list(self.FACE_LANDMARKS.keys()))
        landmark_idx = self.FACE_LANDMARKS[position_name]
        
        if landmark_idx >= len(face_landmarks.landmark):
            return
        
        landmark = face_landmarks.landmark[landmark_idx]
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        
        if 'eye' in position_name:
            bruise_img = self.bruise_images.get('blackeye')
            scale = self.EYE_SCALE
        else:
            bruise_img = self.bruise_images.get('bruise')
            scale = self.NORMAL_SCALE
        
        if bruise_img is None:
            bruise_img = list(self.bruise_images.values())[0]
        
        h, w = bruise_img.shape[:2]
        new_w = int(w * scale)
        new_h = int(h * scale)
        bruise_resized = cv2.resize(bruise_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        bruise_data: BruiseData = {
            'image': bruise_resized,
            'position': (x, y),
            'alpha': self.INITIAL_ALPHA,
            'time': current_time,
            'landmark_idx': landmark_idx,
            'type': bruise_type,
        }
        
        self.bruises.append(bruise_data)
        print(f"Added {bruise_type} bruise at {position_name} (landmark {landmark_idx})")
    
    def update(self, current_time: float) -> None:
        """Update bruise states with fade out over time."""
        active_bruises = []
        
        for bruise in self.bruises:
            elapsed = current_time - bruise['time']
            
            if elapsed < self.DURATION - self.FADE_DURATION:
                bruise['alpha'] = self.INITIAL_ALPHA
                active_bruises.append(bruise)
            elif elapsed < self.DURATION:
                fade_progress = (elapsed - (self.DURATION - self.FADE_DURATION)) / self.FADE_DURATION
                bruise['alpha'] = self.INITIAL_ALPHA * (1.0 - fade_progress)
                active_bruises.append(bruise)
        
        self.bruises = active_bruises
    
    def draw(self, frame: np.ndarray, face_landmarks, frame_width: int, frame_height: int) -> np.ndarray:
        """Draw all active bruises on frame with face tracking."""
        if not self.bruises or face_landmarks is None:
            return frame
        
        for bruise in self.bruises:
            landmark_idx = bruise['landmark_idx']
            if landmark_idx < len(face_landmarks.landmark):
                landmark = face_landmarks.landmark[landmark_idx]
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
            else:
                x, y = bruise['position']
            
            bruise_img = bruise['image']
            h, w = bruise_img.shape[:2]
            
            x1 = max(0, x - w // 2)
            y1 = max(0, y - h // 2)
            x2 = min(frame_width, x1 + w)
            y2 = min(frame_height, y1 + h)
            
            bx1 = 0 if x - w // 2 >= 0 else -(x - w // 2)
            by1 = 0 if y - h // 2 >= 0 else -(y - h // 2)
            bx2 = w if x1 + w <= frame_width else w - (x1 + w - frame_width)
            by2 = h if y1 + h <= frame_height else h - (y1 + h - frame_height)
            
            if bx2 <= bx1 or by2 <= by1:
                continue
            
            roi = frame[y1:y2, x1:x2]
            bruise_region = bruise_img[by1:by2, bx1:bx2]
            
            if bruise_region.shape[2] == 4:
                bruise_bgr = bruise_region[:, :, :3]
                alpha_mask = bruise_region[:, :, 3] / 255.0 * bruise['alpha']
                
                if roi.shape[:2] == bruise_bgr.shape[:2]:
                    for c in range(3):
                        roi[:, :, c] = roi[:, :, c] * (1 - alpha_mask) + bruise_bgr[:, :, c] * alpha_mask
                    frame[y1:y2, x1:x2] = roi
            else:
                if roi.shape[:2] == bruise_region.shape[:2]:
                    cv2.addWeighted(bruise_region, bruise['alpha'], roi, 1 - bruise['alpha'], 0, roi)
                    frame[y1:y2, x1:x2] = roi
        
        return frame
    
    def clear_all(self) -> None:
        """Remove all active bruises."""
        self.bruises.clear()
    
    def get_bruise_count(self) -> int:
        """Get number of active bruises."""
        return len(self.bruises)

"""Procedural Bruise Effect System for Shadow Boxing."""
import random
from typing import Dict, List

import cv2
import numpy as np

BruiseData = Dict[str, object]


class BruiseEffect:
    """Manages procedurally generated bruise overlay effects on player's face."""
    
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

    # -------------------------------------------------
    # 💥 Generate bruise texture directly from code
    # -------------------------------------------------
    def _generate_bruise(self, radius: int, bruise_type: str = 'bruise') -> np.ndarray:
        """Generate a synthetic bruise (circular alpha-blended spot)."""
        size = radius * 2
        bruise = np.zeros((size, size, 4), dtype=np.uint8)

        # Base color range
        if bruise_type == 'blackeye':
            base_color = (40, 20, 80)   # darker purple-blue
        else:
            base_color = (60, 40, 120)  # normal bruise (bluish purple)

        center = (radius, radius)
        max_r = radius * 0.9

        for y in range(size):
            for x in range(size):
                dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
                if dist < max_r:
                    fade = 1.0 - (dist / max_r)
                    alpha = int(255 * (fade ** 2))  # stronger center
                    # Vary color slightly for realism
                    color_variation = random.randint(-10, 10)
                    b, g, r = [np.clip(c + color_variation, 0, 255) for c in base_color]
                    bruise[y, x] = (b, g, r, alpha)

        # Apply Gaussian blur for soft edges
        bruise = cv2.GaussianBlur(bruise, (0, 0), sigmaX=radius * 0.3)
        return bruise

    # -------------------------------------------------
    def add_bruise(self, face_landmarks, frame_width: int, frame_height: int, current_time: float) -> None:
        """Add a new bruise procedurally."""
        bruise_type = random.choice(['bruise', 'blackeye'])
        position_name = random.choice(list(self.FACE_LANDMARKS.keys()))
        landmark_idx = self.FACE_LANDMARKS[position_name]

        if landmark_idx >= len(face_landmarks.landmark):
            return

        landmark = face_landmarks.landmark[landmark_idx]
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)

        # Scale radius relative to face size
        radius = int(frame_width * (self.EYE_SCALE if 'eye' in position_name else self.NORMAL_SCALE))
        radius = max(8, radius)  # minimal visible

        bruise_img = self._generate_bruise(radius, bruise_type)

        bruise_data: BruiseData = {
            'image': bruise_img,
            'position': (x, y),
            'alpha': self.INITIAL_ALPHA,
            'time': current_time,
            'landmark_idx': landmark_idx,
            'type': bruise_type,
        }

        self.bruises.append(bruise_data)
        print(f"Added procedural {bruise_type} bruise at {position_name} (landmark {landmark_idx})")

    # -------------------------------------------------
    def update(self, current_time: float) -> None:
        """Update bruise states with fade out."""
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

    # -------------------------------------------------
    def draw(self, frame: np.ndarray, face_landmarks, frame_width: int, frame_height: int) -> np.ndarray:
        """Draw all active bruises on frame."""
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

            bruise_bgr = bruise_region[:, :, :3]
            alpha_mask = bruise_region[:, :, 3] / 255.0 * bruise['alpha']

            if roi.shape[:2] == bruise_bgr.shape[:2]:
                for c in range(3):
                    roi[:, :, c] = roi[:, :, c] * (1 - alpha_mask) + bruise_bgr[:, :, c] * alpha_mask
                frame[y1:y2, x1:x2] = roi

        return frame

    def clear_all(self) -> None:
        """Remove all active bruises."""
        self.bruises.clear()

    def get_bruise_count(self) -> int:
        """Get number of active bruises."""
        return len(self.bruises)

"""Equipment Renderer for Shadow Boxing."""
import os
from typing import Optional

import cv2
import numpy as np


class EquipmentRenderer:
    """Renders boxing equipment (helm and gloves) using MediaPipe landmarks."""
    
    HELM_WIDTH_SCALE = 1.8
    HELM_HEIGHT_SCALE = 1.6
    HELM_Y_OFFSET = 120
    HELM_Y_RELATIVE_OFFSET = 0.25
    
    GLOVE_SIZE_ATTACKING = 150
    GLOVE_SIZE_TELEGRAPHING = 120
    GLOVE_SIZE_REST = 100
    
    REST_GLOVE_X_OFFSET = 200
    REST_GLOVE_Y = 250
    
    SHADOW_OFFSET = 8
    SHADOW_ALPHA = 0.3
    MOTION_BLUR_TRAILS = 3
    MOTION_BLUR_OFFSET = 20
    
    def __init__(self):
        self.helm_image: Optional[np.ndarray] = None
        self.glove_image: Optional[np.ndarray] = None
        self._load_equipment_images()
        
    def _load_equipment_images(self) -> None:
        """Load equipment PNG images with transparency."""
        base_path = os.path.join(os.getcwd(), 'assets', 'image')
        
        helm_path = os.path.join(base_path, 'boxing-helm.png')
        if os.path.exists(helm_path):
            self.helm_image = cv2.imread(helm_path, cv2.IMREAD_UNCHANGED)
            if self.helm_image is not None:
                print(f"✓ Loaded helm image: {self.helm_image.shape}")
            else:
                print(f"✗ Failed to load helm: {helm_path}")
        else:
            print(f"✗ Helm image not found: {helm_path}")
        
        glove_path = os.path.join(base_path, 'boxing-glove.png')
        if os.path.exists(glove_path):
            self.glove_image = cv2.imread(glove_path, cv2.IMREAD_UNCHANGED)
            if self.glove_image is not None:
                print(f"✓ Loaded glove image: {self.glove_image.shape}")
            else:
                print(f"✗ Failed to load glove: {glove_path}")
        else:
            print(f"✗ Glove image not found: {glove_path}")
    
    def draw_player_helm(self, frame: np.ndarray, face_landmarks, pose_landmarks, 
                        frame_width: int, frame_height: int) -> np.ndarray:
        """Draw boxing helm on player's head."""
        if self.helm_image is None or face_landmarks is None:
            return frame
        
        forehead = face_landmarks.landmark[10]
        chin = face_landmarks.landmark[152]
        left_temple = face_landmarks.landmark[234]
        right_temple = face_landmarks.landmark[454]
        
        forehead_x = int(forehead.x * frame_width)
        forehead_y = int(forehead.y * frame_height)
        chin_x = int(chin.x * frame_width)
        chin_y = int(chin.y * frame_height)
        left_x = int(left_temple.x * frame_width)
        right_x = int(right_temple.x * frame_width)
        
        face_width = abs(right_x - left_x)
        face_height = abs(chin_y - forehead_y)
        
        helm_width = int(face_width * self.HELM_WIDTH_SCALE)
        helm_height = int(face_height * self.HELM_HEIGHT_SCALE)
        
        center_x = (forehead_x + chin_x) // 2
        center_y = forehead_y - int(face_height * self.HELM_Y_RELATIVE_OFFSET) + self.HELM_Y_OFFSET
        
        if helm_width > 0 and helm_height > 0:
            helm_resized = cv2.resize(self.helm_image, (helm_width, helm_height), 
                                     interpolation=cv2.INTER_AREA)
            frame = self._overlay_image(frame, helm_resized, center_x, center_y)
        
        return frame
    
    def draw_enemy_gloves(self, frame: np.ndarray, enemy_ai, current_time: float, 
                         frame_width: int, frame_height: int) -> np.ndarray:
        """Draw boxing gloves for enemy's hands with punch animation."""
        if self.glove_image is None:
            return frame
        
        punch_hand_pos = enemy_ai.get_hand_position(current_time)
        
        if punch_hand_pos:
            px, py = punch_hand_pos
            
            if enemy_ai.is_attacking():
                glove_size = self.GLOVE_SIZE_ATTACKING
                alpha = 1.0
                self._draw_motion_blur(frame, px, py, glove_size, (0, 255, 255))
            elif enemy_ai.is_telegraphing():
                glove_size = self.GLOVE_SIZE_TELEGRAPHING
                alpha = 0.9
            else:
                glove_size = self.GLOVE_SIZE_REST
                alpha = 0.8
            
            glove_resized = cv2.resize(self.glove_image, (glove_size, glove_size),
                                      interpolation=cv2.INTER_AREA)
            self._draw_glove_with_shadow(frame, glove_resized, px, py, alpha)
        
        rest_x = frame_width - self.REST_GLOVE_X_OFFSET
        rest_y = self.REST_GLOVE_Y
        
        glove_rest = cv2.resize(self.glove_image, (self.GLOVE_SIZE_REST, self.GLOVE_SIZE_REST),
                               interpolation=cv2.INTER_AREA)
        self._draw_glove_with_shadow(frame, glove_rest, rest_x, rest_y, alpha=0.7)
        
        return frame
    
    def _draw_glove_with_shadow(self, frame: np.ndarray, glove_img: np.ndarray, 
                               center_x: int, center_y: int, alpha: float = 1.0) -> None:
        """Draw glove with shadow for depth effect."""
        h, w = glove_img.shape[:2]
        
        shadow_overlay = frame.copy()
        shadow_x = center_x + self.SHADOW_OFFSET
        shadow_y = center_y + self.SHADOW_OFFSET
        
        cv2.circle(shadow_overlay, (shadow_x, shadow_y), w // 2, (0, 0, 0), -1)
        cv2.addWeighted(shadow_overlay, alpha * self.SHADOW_ALPHA, frame, 1 - alpha * self.SHADOW_ALPHA, 0, frame)
        
        self._overlay_image(frame, glove_img, center_x, center_y, alpha)
    
    def _draw_motion_blur(self, frame: np.ndarray, x: int, y: int, size: int, color: tuple) -> None:
        """Draw motion blur effect for attacking glove."""
        for i in range(self.MOTION_BLUR_TRAILS):
            offset = -self.MOTION_BLUR_OFFSET * (i + 1)
            alpha = 0.1 - i * 0.03
            overlay = frame.copy()
            cv2.circle(overlay, (x + offset, y), size // 2 - i * 10, color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    def _overlay_image(self, background: np.ndarray, overlay: np.ndarray, 
                      center_x: int, center_y: int, alpha: float = 1.0) -> np.ndarray:
        """Overlay image with alpha channel on background."""
        if overlay is None:
            return background
        
        h, w = overlay.shape[:2]
        bg_h, bg_w = background.shape[:2]
        
        x1 = max(0, center_x - w // 2)
        y1 = max(0, center_y - h // 2)
        x2 = min(bg_w, x1 + w)
        y2 = min(bg_h, y1 + h)
        
        ox1 = 0 if center_x - w // 2 >= 0 else -(center_x - w // 2)
        oy1 = 0 if center_y - h // 2 >= 0 else -(center_y - h // 2)
        ox2 = w if x1 + w <= bg_w else w - (x1 + w - bg_w)
        oy2 = h if y1 + h <= bg_h else h - (y1 + h - bg_h)
        
        if ox2 <= ox1 or oy2 <= oy1 or x2 <= x1 or y2 <= y1:
            return background
        
        roi = background[y1:y2, x1:x2]
        overlay_region = overlay[oy1:oy2, ox1:ox2]
        
        if overlay_region.shape[2] == 4:
            overlay_bgr = overlay_region[:, :, :3]
            overlay_alpha = overlay_region[:, :, 3] / 255.0 * alpha
            
            if roi.shape[:2] == overlay_bgr.shape[:2]:
                for c in range(3):
                    roi[:, :, c] = (roi[:, :, c] * (1 - overlay_alpha) + 
                                   overlay_bgr[:, :, c] * overlay_alpha)
                background[y1:y2, x1:x2] = roi
        else:
            if roi.shape[:2] == overlay_region.shape[:2]:
                cv2.addWeighted(overlay_region, alpha, roi, 1 - alpha, 0, roi)
                background[y1:y2, x1:x2] = roi
        
        return background

"""
Visual Effects Manager
Handles visual overlays like helm filter, particles, screen effects
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import os
import config
from utils.helpers import overlay_image_alpha, get_landmark_coords


class VisualEffectsManager:
    """Manages visual effects and overlays."""
    
    def __init__(self):
        """Initialize visual effects."""
        self.helm_image: Optional[np.ndarray] = None
        self.target_icon: Optional[np.ndarray] = None
        self.punch_bag_image: Optional[np.ndarray] = None
        self.fight_image: Optional[np.ndarray] = None
        
        # Load images with alpha channel
        self._load_images()
        
        # Screen shake effect
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        
    def _load_images(self):
        """Load all visual effect images."""
        # Load helm with alpha
        if os.path.exists(config.HELM_IMAGE):
            self.helm_image = cv2.imread(config.HELM_IMAGE, cv2.IMREAD_UNCHANGED)
            if self.helm_image is not None:
                # Resize helm to appropriate size
                self.helm_image = cv2.resize(self.helm_image, (150, 100))
                print("Loaded helm image")
        
        # Load target icon with alpha
        if os.path.exists(config.TARGET_ICON):
            self.target_icon = cv2.imread(config.TARGET_ICON, cv2.IMREAD_UNCHANGED)
            if self.target_icon is not None:
                self.target_icon = cv2.resize(self.target_icon, (60, 60))
                print("Loaded target icon")
        
        # Load punching bag
        punch_bag_path = os.path.join(config.IMAGE_DIR, "punch-bag-red.png")
        if os.path.exists(punch_bag_path):
            self.punch_bag_image = cv2.imread(punch_bag_path, cv2.IMREAD_UNCHANGED)
            if self.punch_bag_image is not None:
                print("Loaded punching bag image")
        else:
            print(f"Punching bag not found at {punch_bag_path}, will use default visuals")
        
        # Load FIGHT image
        if os.path.exists(config.FIGHT_IMAGE):
            self.fight_image = cv2.imread(config.FIGHT_IMAGE, cv2.IMREAD_UNCHANGED)
            if self.fight_image is not None:
                print("Loaded FIGHT image")
    
    def draw_helm_overlay(self, frame: np.ndarray, pose_landmarks, frame_width: int, frame_height: int):
        """
        Draw boxing helm overlay on face using pose landmarks 7 and 8 (ears).
        
        Args:
            frame: Frame to draw on
            pose_landmarks: Pose landmarks from MediaPipe
            frame_width: Frame width
            frame_height: Frame height
        """
        if self.helm_image is None or pose_landmarks is None:
            return
        
        try:
            # Get ear landmarks (7 = left ear, 8 = right ear)
            left_ear = pose_landmarks.landmark[7]
            right_ear = pose_landmarks.landmark[8]
            
            # Check visibility
            if left_ear.visibility < 0.5 or right_ear.visibility < 0.5:
                return
            
            # Calculate helm position and size based on ear distance
            left_x, left_y = get_landmark_coords(left_ear, frame_width, frame_height)
            right_x, right_y = get_landmark_coords(right_ear, frame_width, frame_height)
            
            # Calculate center between ears
            center_x = (left_x + right_x) // 2
            center_y = (left_y + right_y) // 2
            
            # Calculate helm width based on ear distance
            ear_distance = int(np.sqrt((right_x - left_x)**2 + (right_y - left_y)**2))
            helm_width = int(ear_distance * 2.5)
            helm_height = int(helm_width * 0.67)  # Maintain aspect ratio
            
            # Resize helm
            resized_helm = cv2.resize(self.helm_image, (helm_width, helm_height))
            
            # Position helm (center it between ears, slightly above)
            helm_x = center_x - helm_width // 2
            helm_y = center_y - int(helm_height * 0.6)
            
            # Overlay helm
            overlay_image_alpha(frame, resized_helm, (helm_x, helm_y), alpha=0.8)
            
        except Exception as e:
            print(f"Error drawing helm: {e}")
    
    def draw_target_warning(self, frame: np.ndarray, position: Tuple[int, int], 
                          progress: float = 1.0, pulsate: bool = True):
        """
        Draw red target warning indicator.
        
        Args:
            frame: Frame to draw on
            position: (x, y) position of target
            progress: Attack progress (0-1) for animation
            pulsate: Whether to pulsate the target
        """
        x, y = position
        
        # Pulsating effect
        if pulsate:
            scale = 1.0 + 0.2 * np.sin(progress * np.pi * 4)
        else:
            scale = 1.0
        
        # Draw outer circle (warning)
        radius_outer = int(40 * scale)
        radius_inner = int(30 * scale)
        
        # Red warning circle
        cv2.circle(frame, (x, y), radius_outer, (0, 0, 255), 3)
        cv2.circle(frame, (x, y), radius_inner, (0, 0, 200), 2)
        
        # Draw crosshair
        line_length = int(15 * scale)
        cv2.line(frame, (x - line_length, y), (x + line_length, y), (0, 0, 255), 2)
        cv2.line(frame, (x, y - line_length), (x, y + line_length), (0, 0, 255), 2)
        
        # Optional: overlay target icon if available
        if self.target_icon is not None:
            icon_size = int(60 * scale)
            resized_icon = cv2.resize(self.target_icon, (icon_size, icon_size))
            icon_x = x - icon_size // 2
            icon_y = y - icon_size // 2
            overlay_image_alpha(frame, resized_icon, (icon_x, icon_y), alpha=0.7)
    
    def draw_hitbox(self, frame: np.ndarray, position: Tuple[int, int], 
                   size: int, color: Tuple[int, int, int] = (0, 255, 255),
                   hit: bool = False):
        """
        Draw punch hitbox with punching bag image overlay.
        
        Args:
            frame: Frame to draw on
            position: (x, y) TOP-LEFT corner position
            size: Size of hitbox (width and height)
            color: Color of hitbox (for fallback)
            hit: Whether the hitbox was hit
        """
        x, y = position
        center_x = x + size // 2
        center_y = y + size // 2
        
        if hit:
            # Hit effect - flash and impact
            if self.punch_bag_image is not None:
                # Show punching bag with green flash
                bag_size = int(size * 1.2)
                resized_bag = cv2.resize(self.punch_bag_image, (bag_size, bag_size))
                bag_x = center_x - bag_size // 2
                bag_y = center_y - bag_size // 2
                overlay_image_alpha(frame, resized_bag, (bag_x, bag_y), alpha=0.7)
                
                # Green flash circle
                cv2.circle(frame, (center_x, center_y), size // 2, (0, 255, 0), -1)
            else:
                # Fallback: rectangle flash
                cv2.rectangle(frame, (x, y), (x + size, y + size), (0, 255, 0), -1)
            
            # HIT text
            cv2.putText(frame, "HIT!", (x + 10, center_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        else:
            # Normal hitbox - show punching bag
            if self.punch_bag_image is not None:
                # Pulsating effect
                scale = 1.0 + 0.1 * np.sin(cv2.getTickCount() / cv2.getTickFrequency() * 3)
                bag_size = int(size * scale)
                resized_bag = cv2.resize(self.punch_bag_image, (bag_size, bag_size))
                bag_x = center_x - bag_size // 2
                bag_y = center_y - bag_size // 2
                overlay_image_alpha(frame, resized_bag, (bag_x, bag_y), alpha=0.85)
                
                # Glow effect around bag
                cv2.circle(frame, (center_x, center_y), size // 2 + 5, color, 2)
            else:
                # Fallback: colored rectangle with glow
                cv2.rectangle(frame, (x-2, y-2), (x + size + 2, y + size + 2), color, 3)
                overlay = frame.copy()
                cv2.rectangle(overlay, (x, y), (x + size, y + size), color, -1)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
                cv2.rectangle(frame, (x, y), (x + size, y + size), color, 2)
    
    def trigger_screen_shake(self, intensity: int = 10, duration: float = 0.2):
        """
        Trigger screen shake effect.
        
        Args:
            intensity: Shake intensity in pixels
            duration: Duration in seconds
        """
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
    
    def apply_screen_shake(self, frame: np.ndarray, dt: float) -> np.ndarray:
        """
        Apply screen shake effect to frame.
        
        Args:
            frame: Input frame
            dt: Delta time since last frame
            
        Returns:
            Shaken frame
        """
        if self.screen_shake_duration <= 0:
            return frame
        
        # Decrease shake duration
        self.screen_shake_duration -= dt
        
        # Calculate shake offset
        offset_x = int(np.random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity))
        offset_y = int(np.random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity))
        
        # Create translation matrix
        h, w = frame.shape[:2]
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        
        # Apply translation
        shaken_frame = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        return shaken_frame
    
    def draw_damage_indicator(self, frame: np.ndarray, damage: int, position: Tuple[int, int]):
        """
        Draw floating damage number.
        
        Args:
            frame: Frame to draw on
            damage: Damage amount
            position: (x, y) position
        """
        text = f"-{damage}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        
        # Draw outline
        cv2.putText(frame, text, position, font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # Draw text
        cv2.putText(frame, text, position, font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
    
    def draw_combo_text(self, frame: np.ndarray, combo: int, position: Tuple[int, int]):
        """
        Draw combo text effect.
        
        Args:
            frame: Frame to draw on
            combo: Combo count
            position: (x, y) position
        """
        if combo <= 1:
            return
        
        text = f"COMBO x{combo}!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        
        # Get text size for centering
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = position[0] - text_size[0] // 2
        text_y = position[1]
        
        # Draw with gold color
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (0, 215, 255), thickness, cv2.LINE_AA)

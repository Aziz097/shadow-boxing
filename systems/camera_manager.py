"""
Camera Manager
Handles webcam input and frame processing
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import config


class CameraManager:
    """Manages webcam capture and frame processing."""
    
    def __init__(self, camera_index: int = config.CAMERA_INDEX):
        """
        Initialize camera manager.
        
        Args:
            camera_index: Index of camera device
        """
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        self.frame_width = config.CAMERA_WIDTH
        self.frame_height = config.CAMERA_HEIGHT
        
    def open(self) -> bool:
        """
        Open camera capture.
        
        Returns:
            True if successful, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        # Verify actual dimensions
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.is_opened = True
        print(f"Camera opened: {self.frame_width}x{self.frame_height}")
        return True
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from camera.
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        success, frame = self.cap.read()
        
        if not success:
            return False, None
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        return True, frame
    
    def get_rgb_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert BGR frame to RGB for MediaPipe.
        
        Args:
            frame: BGR frame from OpenCV
            
        Returns:
            RGB frame
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def get_dimensions(self) -> Tuple[int, int]:
        """
        Get frame dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        return self.frame_width, self.frame_height
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print("Camera released")
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()

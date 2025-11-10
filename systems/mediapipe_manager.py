"""
MediaPipe Manager
Handles all MediaPipe detection (hands, pose, face)
"""
import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple
import config


class MediaPipeManager:
    """Manages MediaPipe hand, pose, and face detection."""
    
    def __init__(self):
        """Initialize MediaPipe solutions."""
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create detectors
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.HAND_MAX_NUM,
            min_detection_confidence=config.HAND_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.HAND_MIN_TRACKING_CONFIDENCE
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=config.POSE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.POSE_MIN_TRACKING_CONFIDENCE
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=config.FACE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.FACE_MIN_TRACKING_CONFIDENCE
        )
        
        # Results storage
        self.hand_results = None
        self.pose_results = None
        self.face_results = None
        
    def process_frame(self, rgb_frame: np.ndarray):
        """
        Process frame with all MediaPipe detectors.
        
        Args:
            rgb_frame: RGB frame (not BGR)
        """
        self.hand_results = self.hands.process(rgb_frame)
        self.pose_results = self.pose.process(rgb_frame)
        self.face_results = self.face_mesh.process(rgb_frame)
    
    def get_hand_landmarks(self) -> Optional[List]:
        """
        Get detected hand landmarks.
        
        Returns:
            List of hand landmarks or None
        """
        if self.hand_results and self.hand_results.multi_hand_landmarks:
            return self.hand_results.multi_hand_landmarks
        return None
    
    def get_pose_landmarks(self):
        """
        Get detected pose landmarks.
        
        Returns:
            Pose landmarks or None
        """
        if self.pose_results and self.pose_results.pose_landmarks:
            return self.pose_results.pose_landmarks
        return None
    
    def get_face_landmarks(self):
        """
        Get detected face landmarks.
        
        Returns:
            Face landmarks or None
        """
        if self.face_results and self.face_results.multi_face_landmarks:
            return self.face_results.multi_face_landmarks[0]
        return None
    
    def draw_hand_landmarks(self, frame: np.ndarray):
        """Draw hand landmarks on frame."""
        if self.hand_results and self.hand_results.multi_hand_landmarks:
            for hand_landmarks in self.hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
    
    def draw_pose_landmarks(self, frame: np.ndarray):
        """Draw pose landmarks on frame."""
        if self.pose_results and self.pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                self.pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
    
    def get_landmark_position(self, landmark, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """
        Convert normalized landmark to pixel coordinates.
        
        Args:
            landmark: MediaPipe landmark
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
            
        Returns:
            Tuple of (x, y) pixel coordinates
        """
        return int(landmark.x * frame_width), int(landmark.y * frame_height)
    
    def get_hand_center(self, hand_landmarks, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """
        Get center position of hand.
        
        Args:
            hand_landmarks: Hand landmarks from MediaPipe
            frame_width: Frame width
            frame_height: Frame height
            
        Returns:
            Tuple of (x, y) center coordinates
        """
        x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
        y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
        return int(np.mean(x_coords)), int(np.mean(y_coords))
    
    def get_face_bbox(self, face_landmarks, frame_width: int, frame_height: int) -> Tuple[int, int, int, int]:
        """
        Get bounding box of face.
        
        Args:
            face_landmarks: Face landmarks from MediaPipe
            frame_width: Frame width
            frame_height: Frame height
            
        Returns:
            Tuple of (x_min, y_min, x_max, y_max)
        """
        x_coords = [lm.x * frame_width for lm in face_landmarks.landmark]
        y_coords = [lm.y * frame_height for lm in face_landmarks.landmark]
        return (
            int(min(x_coords)),
            int(min(y_coords)),
            int(max(x_coords)),
            int(max(y_coords))
        )
    
    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()
        self.pose.close()
        self.face_mesh.close()

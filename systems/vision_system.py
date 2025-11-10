import cv2
import mediapipe as mp
import time
from core import config
from core.math_utils import distance

class VisionSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.HAND_MAX_NUM,
            min_detection_confidence=self.config.HAND_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.HAND_MIN_TRACKING_CONFIDENCE
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=self.config.POSE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.POSE_MIN_TRACKING_CONFIDENCE
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=self.config.FACE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.FACE_MIN_DETECTION_CONFIDENCE
        )
        
        # State tracking
        self.last_frame_time = time.time()
        self.fps = 0
        
    def get_frame(self):
        """Get processed frame with landmarks"""
        success, frame = self.cap.read()
        if not success:
            return None
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        
        # Calculate FPS
        current_time = time.time()
        self.fps = 1 / (current_time - self.last_frame_time) if (current_time - self.last_frame_time) > 0 else 0
        self.last_frame_time = current_time
        
        return {
            'frame': frame,
            'hands': hand_results,
            'pose': pose_results,
            'face': face_results,
            'fps': self.fps
        }
    
    def get_face_bbox(self, face_results):
        """Get face bounding box from landmarks"""
        if not face_results.multi_face_landmarks:
            return None
        
        landmarks = face_results.multi_face_landmarks[0].landmark
        frame_width = self.config.CAMERA_WIDTH
        frame_height = self.config.CAMERA_HEIGHT
        
        x_coords = [int(landmark.x * frame_width) for landmark in landmarks]
        y_coords = [int(landmark.y * frame_height) for landmark in landmarks]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def get_body_landmarks(self, pose_results):
        """Get body landmarks for defense fallback"""
        if not pose_results.pose_landmarks:
            return None
        
        return pose_results.pose_landmarks.landmark
    
    def release(self):
        """Release camera resources"""
        self.cap.release()
        self.hands.close()
        self.pose.close()
        self.face_mesh.close()
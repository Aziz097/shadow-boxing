import cv2
import mediapipe as mp
import time

class VisionSystem:
    def __init__(self, game_config):
        self.config = game_config
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        # Set buffer to reduce lag
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.HAND_MAX_NUM,
            min_detection_confidence=self.config.HAND_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.HAND_MIN_TRACKING_CONFIDENCE
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Use lightweight model
            min_detection_confidence=self.config.POSE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.POSE_MIN_TRACKING_CONFIDENCE
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,  # Disable refinement for better performance
            min_detection_confidence=self.config.FACE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.FACE_MIN_TRACKING_CONFIDENCE
        )
        
        # State tracking
        self.last_frame_time = time.time()
        self.fps = 0
        self.debug_mode = False  # Disable debug mode for performance
        self.last_error = None
        self.frame_skip_counter = 0
        self.skip_every_n_frames = 1  # Process every frame for responsiveness
    
    def get_frame(self):
        """Get processed frame with landmarks and debug info"""
        success, frame = self.cap.read()
        if not success:
            return None
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = None
        face_results = None
        pose_results = None
        
        try:
            hand_results = self.hands.process(rgb_frame)
            face_results = self.face_mesh.process(rgb_frame)
            pose_results = self.pose.process(rgb_frame)
            
            # Clear last error if no error occurred
            self.last_error = None
        except Exception as e:
            self.last_error = f"MediaPipe Error: {str(e)}"
            print(self.last_error)
        
        # Calculate FPS
        current_time = time.time()
        self.fps = 1 / (current_time - self.last_frame_time) if (current_time - self.last_frame_time) > 0 else 0
        self.last_frame_time = current_time
        
        # Add debug visualization
        if self.debug_mode:
            frame = self._add_debug_overlay(frame, hand_results, face_results, pose_results)
        
        return {
            'frame': frame,
            'hands': hand_results,
            'face': face_results,
            'pose': pose_results,
            'fps': self.fps,
            'error': self.last_error
        }
    
    def _add_debug_overlay(self, frame, hand_results, face_results, pose_results):
        """Add debug visualization on frame"""
        # FPS counter
        cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # MediaPipe status
        if self.last_error:
            cv2.putText(frame, self.last_error, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "MediaPipe: OK", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw hand landmarks if detected
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Draw landmarks
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    
                    # Draw landmark point
                    cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
                    
                    # Draw index numbers
                    if idx % 4 == 0:  # Show every 4th landmark index
                        cv2.putText(frame, str(idx), (x, y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Draw face landmarks if detected
        if face_results and face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                for idx, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
        
        # Draw pose landmarks if detected
        if pose_results and pose_results.pose_landmarks:
            for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
        
        # Add debug status text
        if hand_results and hand_results.multi_hand_landmarks:
            cv2.putText(frame, f"Hands: {len(hand_results.multi_hand_landmarks)}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Hands: 0", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if face_results and face_results.multi_face_landmarks:
            cv2.putText(frame, "Face: Detected", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Face: Not Detected", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if pose_results and pose_results.pose_landmarks:
            cv2.putText(frame, "Pose: Detected", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Pose: Not Detected", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def get_face_bbox(self, face_results):
        """Get face bounding box from landmarks with debug info"""
        if not face_results or not face_results.multi_face_landmarks:
            return None
        
        landmarks = face_results.multi_face_landmarks[0].landmark
        x_coords = [int(landmark.x * self.config.CAMERA_WIDTH) for landmark in landmarks]
        y_coords = [int(landmark.y * self.config.CAMERA_HEIGHT) for landmark in landmarks]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def get_body_landmarks(self, pose_results):
        """Get body landmarks for defense fallback"""
        if not pose_results or not pose_results.pose_landmarks:
            return None
        
        return pose_results.pose_landmarks.landmark
    
    def release(self):
        """Release camera resources"""
        self.cap.release()
        self.hands.close()
        self.pose.close()
        self.face_mesh.close()
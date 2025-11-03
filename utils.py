"""
Utility functions untuk Shadow Boxing
Helper functions untuk deteksi dan kalkulasi
"""
import numpy as np

def is_fist(hand_landmarks):
    """
    Deteksi kepalan tangan
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        
    Returns:
        bool: True jika tangan dalam posisi kepalan
    """
    landmarks = hand_landmarks.landmark
    
    def angle_between_points(p1, p2, p3):
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        dot = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
        cos_angle = dot / (norm_v1 * norm_v2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cos_angle))
    
    def distance(p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    # Hitung sudut di setiap jari
    angles = []
    for finger_tip in [8, 12, 16, 20]:
        base = landmarks[finger_tip - 2]
        mid = landmarks[finger_tip - 1]
        tip = landmarks[finger_tip]
        angle = angle_between_points(base, mid, tip)
        angles.append(angle)
    
    avg_angle = np.mean(angles)
    
    # Hitung jarak rata-rata ujung jari ke telapak
    palm_ref = landmarks[9]
    distances = [
        distance(landmarks[4], palm_ref),
        distance(landmarks[8], palm_ref),
        distance(landmarks[12], palm_ref),
        distance(landmarks[16], palm_ref),
        distance(landmarks[20], palm_ref)
    ]
    avg_dist = np.mean(distances)
    
    angle_condition = avg_angle < 175
    dist_condition = avg_dist < 0.31
    
    return angle_condition and dist_condition

def get_hand_center(hand_landmarks, frame_width, frame_height):
    """
    Dapatkan titik tengah tangan
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        frame_width: Lebar frame
        frame_height: Tinggi frame
        
    Returns:
        np.array: Koordinat [x, y] titik tengah tangan
    """
    x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
    y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
    return np.array([np.mean(x_coords), np.mean(y_coords)])

def detect_punch_by_velocity(hand_landmarks, current_time, prev_hand_pos, prev_time, 
                             frame_width, frame_height, velocity_threshold=800, 
                             direction_threshold=0.5):
    """
    Deteksi pukulan berdasarkan kecepatan dan arah
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        current_time: Waktu sekarang
        prev_hand_pos: Posisi tangan sebelumnya
        prev_time: Waktu sebelumnya
        frame_width: Lebar frame
        frame_height: Tinggi frame
        velocity_threshold: Threshold kecepatan minimum
        direction_threshold: Threshold arah (cos theta)
        
    Returns:
        tuple: (is_punch, new_hand_pos, current_time)
    """
    hand_pos = get_hand_center(hand_landmarks, frame_width, frame_height)
    
    if prev_hand_pos is not None and prev_time != 0:
        delta_time = current_time - prev_time
        if delta_time > 0:
            velocity = (hand_pos - prev_hand_pos) / delta_time
            speed = np.linalg.norm(velocity)
            
            if speed > velocity_threshold:
                face_center = np.array([frame_width // 2, frame_height // 2])
                to_face = face_center - hand_pos
                
                if np.linalg.norm(to_face) > 0:
                    to_face = to_face / np.linalg.norm(to_face)
                    velocity_norm = velocity / np.linalg.norm(velocity)
                    cos_theta = np.dot(velocity_norm, to_face)
                    
                    if cos_theta > direction_threshold:
                        return True, hand_pos, current_time
    
    return False, hand_pos, current_time

def calculate_distance(p1, p2):
    """
    Hitung jarak Euclidean antara dua titik
    
    Args:
        p1: Tuple (x, y)
        p2: Tuple (x, y)
        
    Returns:
        float: Jarak antara p1 dan p2
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def point_in_rect(point, rect):
    """
    Cek apakah titik berada di dalam rectangle
    
    Args:
        point: Tuple (x, y)
        rect: Tuple (x1, y1, x2, y2)
        
    Returns:
        bool: True jika titik di dalam rectangle
    """
    x, y = point
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2

def lerp(start, end, t):
    """
    Linear interpolation
    
    Args:
        start: Nilai awal
        end: Nilai akhir
        t: Factor interpolasi (0.0 - 1.0)
        
    Returns:
        Nilai terinterpolasi
    """
    return start + (end - start) * t

def ease_in_out(t):
    """
    Easing function untuk animasi smooth
    
    Args:
        t: Progress (0.0 - 1.0)
        
    Returns:
        Eased value
    """
    return t * t * (3.0 - 2.0 * t)

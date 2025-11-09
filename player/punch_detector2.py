import cv2
import mediapipe as mp
import numpy as np
import time
from collections import defaultdict

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # Sekarang support 2 tangan
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Variabel global
last_fist_time = defaultdict(float)  # Per-hand tracking
FIST_MEMORY_DURATION = 0.5
last_punch_time = 0
PUNCH_COOLDOWN = 0
punch_counter = 0

# State tracking per tangan
hand_states = {
    'left': {'prev_pos': None, 'prev_time': 0},
    'right': {'prev_pos': None, 'prev_time': 0}
}
HAND_ASSIGNMENT_THRESHOLD = 150  # Threshold untuk membedakan kiri/kanan

# Konstanta deteksi
VELOCITY_THRESHOLD = 800
DIRECTION_THRESHOLD = 0.5

def is_fist(hand_landmarks):
    """
    Deteksi kepalan dengan kombinasi sudut dan jarak.
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
    Ambil titik tengah tangan (rata-rata koordinat semua landmark).
    """
    x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
    y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
    return np.array([np.mean(x_coords), np.mean(y_coords)])

def detect_punch(hand_landmarks, hand_id, current_time, frame_width, frame_height):
    """
    Deteksi punch per tangan menggunakan state terpisah
    """
    global last_punch_time
    
    hand_state = hand_states[hand_id]
    hand_pos = get_hand_center(hand_landmarks, frame_width, frame_height)

    if hand_state['prev_pos'] is not None and hand_state['prev_time'] != 0:
        delta_time = current_time - hand_state['prev_time']
        if delta_time > 0.001:  # Hindari pembagian nol
            velocity = (hand_pos - hand_state['prev_pos']) / delta_time
            speed = np.linalg.norm(velocity)

            if speed > VELOCITY_THRESHOLD:
                face_center = np.array([frame_width // 2, frame_height // 2])
                to_face = face_center - hand_pos
                
                if np.linalg.norm(to_face) > 0:
                    to_face_norm = to_face / np.linalg.norm(to_face)
                    velocity_norm = velocity / np.linalg.norm(velocity)
                    cos_theta = np.dot(velocity_norm, to_face_norm)
                    
                    if cos_theta > DIRECTION_THRESHOLD:
                        if current_time - last_punch_time > PUNCH_COOLDOWN:
                            last_punch_time = current_time
                            hand_state['prev_pos'] = hand_pos  # Reset posisi setelah punch
                            hand_state['prev_time'] = current_time
                            return True

    # Update state hanya jika tidak ada punch
    hand_state['prev_pos'] = hand_pos
    hand_state['prev_time'] = current_time
    return False

def assign_hand_id(hand_center, frame_width):
    """
    Menentukan ID tangan (kiri/kanan) berdasarkan posisi horizontal
    """
    if hand_center[0] < frame_width // 2:
        return 'left'
    return 'right'

# Buka kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    current_time = time.time()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    fist_detected = False
    punch_detected = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            hand_center = get_hand_center(hand_landmarks, frame_width, frame_height)
            hand_id = assign_hand_id(hand_center, frame_width)
            
            # Cek kepalan
            if is_fist(hand_landmarks):
                fist_detected = True
                last_fist_time[hand_id] = current_time

            # Deteksi punch hanya jika fist terdeteksi
            if fist_detected:
                if detect_punch(hand_landmarks, hand_id, current_time, frame_width, frame_height):
                    punch_detected = True

    else:
        # Reset state ketika tidak ada tangan terdeteksi
        for hand_id in hand_states:
            hand_states[hand_id]['prev_pos'] = None
            hand_states[hand_id]['prev_time'] = 0
        
        # Cek fist memory untuk semua tangan
        for hand_id in last_fist_time:
            if current_time - last_fist_time[hand_id] < FIST_MEMORY_DURATION:
                fist_detected = True
                break

    # Tampilkan status
    status_text = "PUNCH!" if punch_detected else ("FIST!" if fist_detected else "Open Hand")
    color = (0, 0, 255) if punch_detected else ((0, 255, 0) if fist_detected else (255, 255, 255))
    
    cv2.putText(frame, status_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
    if punch_detected:
        punch_counter += 1
    
    cv2.putText(frame, f"Punch Count: {punch_counter}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.imshow('Punch Detector (Multi-Hand)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
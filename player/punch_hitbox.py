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
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Variabel global
last_fist_time = defaultdict(float)
FIST_MEMORY_DURATION = 0.9
last_punch_time_left = 0
last_punch_time_right = 0
PUNCH_COOLDOWN = 0.3
punch_counter_left = 0
punch_counter_right = 0

# State tracking per tangan
hand_states = {
    'left': {'prev_pos': None, 'prev_time': 0},
    'right': {'prev_pos': None, 'prev_time': 0}
}

# Konstanta deteksi
VELOCITY_THRESHOLD = 600
DIRECTION_THRESHOLD = 0.65

# Definisi hit box kiri dan kanan
LEFT_HIT_BOX = {
    'x1': 280,   # Koordinat kiri
    'y1': 100,   # Koordinat atas
    'x2': 400,   # Koordinat kanan
    'y2': 220,   # Koordinat bawah
    'color': (255, 100, 100),  # Biru kemerahan
    'label': "LEFT TARGET"
}

RIGHT_HIT_BOX = {
    'x1': 880,   # Koordinat kiri
    'y1': 100,   # Koordinat atas
    'x2': 1000,  # Koordinat kanan
    'y2': 220,   # Koordinat bawah
    'color': (100, 100, 255),  # Merah kebiruan
    'label': "RIGHT TARGET"
}

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

    angle_condition = avg_angle < 165  # Lebih strict untuk fist
    dist_condition = avg_dist < 0.26   # Lebih strict untuk fist

    return angle_condition and dist_condition

def get_hand_center(hand_landmarks, frame_width, frame_height):
    """
    Ambil titik tengah tangan (rata-rata koordinat semua landmark).
    """
    x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
    y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
    return np.array([np.mean(x_coords), np.mean(y_coords)])

def is_hand_in_hitbox(hand_center, hit_box):
    """
    Cek apakah tangan berada dalam hit box
    """
    x, y = hand_center
    return (hit_box['x1'] <= x <= hit_box['x2']) and (hit_box['y1'] <= y <= hit_box['y2'])

def get_hitbox_center(hit_box):
    """Dapatkan pusat hit box"""
    return np.array([
        (hit_box['x1'] + hit_box['x2']) // 2,
        (hit_box['y1'] + hit_box['y2']) // 2
    ])

def detect_punch(hand_landmarks, hand_id, current_time, frame_width, frame_height):
    """
    Deteksi punch berdasarkan:
    1. Tangan dalam posisi fist
    2. Kecepatan tinggi
    3. Arah gerakan menuju hit box yang sesuai
    4. Tangan memasuki hit box yang sesuai
    """
    global last_punch_time_left, last_punch_time_right
    
    hand_state = hand_states[hand_id]
    hand_pos = get_hand_center(hand_landmarks, frame_width, frame_height)
    
    # Pilih hit box yang sesuai berdasarkan tangan
    hit_box = LEFT_HIT_BOX if hand_id == 'left' else RIGHT_HIT_BOX
    hit_box_center = get_hitbox_center(hit_box)
    
    if hand_state['prev_pos'] is not None and hand_state['prev_time'] != 0:
        delta_time = current_time - hand_state['prev_time']
        if delta_time > 0.001:  # Hindari pembagian nol
            # Hitung kecepatan
            velocity = (hand_pos - hand_state['prev_pos']) / delta_time
            speed = np.linalg.norm(velocity)
            
            # Cek apakah tangan sedang memasuki hit box yang sesuai
            was_outside = not is_hand_in_hitbox(hand_state['prev_pos'], hit_box)
            is_inside = is_hand_in_hitbox(hand_pos, hit_box)
            entering_hitbox = was_outside and is_inside
            
            # Vektor dari posisi tangan sebelumnya ke pusat hit box
            to_hitbox = hit_box_center - hand_state['prev_pos']
            
            # Normalisasi vektor
            if np.linalg.norm(to_hitbox) > 0 and speed > 0:
                to_hitbox_norm = to_hitbox / np.linalg.norm(to_hitbox)
                velocity_norm = velocity / speed
                
                # Hitung cosinus sudut antara arah gerakan dan arah ke hit box
                cos_theta = np.dot(velocity_norm, to_hitbox_norm)
                
                # Tentukan cooldown berdasarkan tangan
                last_punch_time = last_punch_time_left if hand_id == 'left' else last_punch_time_right
                cooldown_passed = (current_time - last_punch_time) > PUNCH_COOLDOWN
                
                # Kondisi deteksi punch:
                if (speed > VELOCITY_THRESHOLD and 
                    cos_theta > DIRECTION_THRESHOLD and 
                    entering_hitbox and
                    cooldown_passed):
                    
                    # Update cooldown untuk tangan spesifik
                    if hand_id == 'left':
                        last_punch_time_left = current_time
                        return 'left'
                    else:
                        last_punch_time_right = current_time
                        return 'right'

    # Update state
    hand_state['prev_pos'] = hand_pos
    hand_state['prev_time'] = current_time
    return None

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
    punch_hand = None  # Menyimpan ID tangan yang melakukan punch

    # Gambar hit box kiri
    cv2.rectangle(frame, 
                 (LEFT_HIT_BOX['x1'], LEFT_HIT_BOX['y1']), 
                 (LEFT_HIT_BOX['x2'], LEFT_HIT_BOX['y2']), 
                 LEFT_HIT_BOX['color'], 
                 3)
    cv2.putText(frame, LEFT_HIT_BOX['label'], 
               (LEFT_HIT_BOX['x1'] + 30, LEFT_HIT_BOX['y1'] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Gambar hit box kanan
    cv2.rectangle(frame, 
                 (RIGHT_HIT_BOX['x1'], RIGHT_HIT_BOX['y1']), 
                 (RIGHT_HIT_BOX['x2'], RIGHT_HIT_BOX['y2']), 
                 RIGHT_HIT_BOX['color'], 
                 3)
    cv2.putText(frame, RIGHT_HIT_BOX['label'], 
               (RIGHT_HIT_BOX['x1'] + 30, RIGHT_HIT_BOX['y1'] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            hand_center = get_hand_center(hand_landmarks, frame_width, frame_height)
            hand_id = assign_hand_id(hand_center, frame_width)
            
            # Visualisasi posisi tangan
            hand_color = (255, 0, 255) if hand_id == 'left' else (0, 255, 255)
            cv2.circle(frame, (int(hand_center[0]), int(hand_center[1])), 10, hand_color, -1)
            cv2.putText(frame, hand_id.upper(), 
                       (int(hand_center[0]) - 40, int(hand_center[1]) - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, hand_color, 2)
            
            # Cek kepalan
            if is_fist(hand_landmarks):
                fist_detected = True
                last_fist_time[hand_id] = current_time
                
                # Beri visualisasi fist
                fist_color = (0, 255, 0) if hand_id == 'left' else (0, 200, 255)
                cv2.circle(frame, (int(hand_center[0]), int(hand_center[1])), 25, fist_color, 2)
                cv2.putText(frame, "FIST", 
                           (int(hand_center[0]) - 35, int(hand_center[1]) + 45),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, fist_color, 2)

            # Deteksi punch hanya jika fist terdeteksi
            if fist_detected:
                punch_result = detect_punch(hand_landmarks, hand_id, current_time, frame_width, frame_height)
                if punch_result:
                    punch_hand = punch_result
                    if punch_hand == 'left':
                        punch_counter_left += 1
                    else:
                        punch_counter_right += 1

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
    status_text = f"{punch_hand.upper()} PUNCH!" if punch_hand else ("FIST DETECTED" if fist_detected else "READY")
    status_color = (0, 0, 255) if punch_hand else ((0, 255, 0) if fist_detected else (255, 255, 255))
    
    # Tampilkan status di layar
    cv2.putText(frame, status_text, (frame_width//2 - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 3)
    
    # Tampilkan counter punch
    cv2.putText(frame, f"LEFT PUNCHES: {punch_counter_left}", 
               (LEFT_HIT_BOX['x1'] + 30, LEFT_HIT_BOX['y2'] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, LEFT_HIT_BOX['color'], 2)
    
    cv2.putText(frame, f"RIGHT PUNCHES: {punch_counter_right}", 
               (RIGHT_HIT_BOX['x1'] + 30, RIGHT_HIT_BOX['y2'] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, RIGHT_HIT_BOX['color'], 2)
    
    # Petunjuk penggunaan
    cv2.putText(frame, "Make a fist and punch the LEFT/RIGHT target boxes", 
               (frame_width//2 - 250, frame_height - 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 255), 2)

    cv2.imshow('Dual Target Punch Detector - Press Q to exit', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
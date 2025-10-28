import cv2
import mediapipe as mp
import numpy as np
import time

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Variabel global
last_fist_time = 0
FIST_MEMORY_DURATION = 0.5
last_punch_time = 0
PUNCH_COOLDOWN = 0.1

puch_countr = 0

# Untuk deteksi velocity
prev_hand_pos = None
prev_time = 0
VELOCITY_THRESHOLD = 800  # sesuaikan
DIRECTION_THRESHOLD = 0.5  # cos theta > 0.7 = arah mendekati wajah

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

def detect_punch_by_velocity(hand_landmarks, current_time, frame_width, frame_height):
    """
    Deteksi pukulan berdasarkan kecepatan dan arah gerakan.
    """
    global prev_hand_pos, prev_time, last_punch_time

    # Ambil posisi tangan sekarang
    hand_pos = get_hand_center(hand_landmarks, frame_width, frame_height)

    if prev_hand_pos is not None and prev_time != 0:
        # Hitung kecepatan (perubahan posisi per detik)
        delta_time = current_time - prev_time
        if delta_time > 0:
            velocity = (hand_pos - prev_hand_pos) / delta_time
            speed = np.linalg.norm(velocity)

            # Jika kecepatan tinggi → cek arah
            if speed > VELOCITY_THRESHOLD:
                # Asumsikan wajah di tengah layar
                face_center = np.array([frame_width // 2, frame_height // 2])

                # Vektor dari tangan ke wajah
                to_face = face_center - hand_pos

                # Normalisasi
                if np.linalg.norm(to_face) > 0:
                    to_face = to_face / np.linalg.norm(to_face)
                    velocity_norm = velocity / np.linalg.norm(velocity)

                    # Hitung cos theta (arah gerakan vs arah ke wajah)
                    cos_theta = np.dot(velocity_norm, to_face)

                    # Jika arah gerakan mendekati wajah (cos theta > 0.7)
                    if cos_theta > DIRECTION_THRESHOLD:
                        if current_time - last_punch_time > PUNCH_COOLDOWN:
                            last_punch_time = current_time
                            return True

    # Update posisi dan waktu
    prev_hand_pos = hand_pos
    prev_time = current_time

    return False

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

    # Flip horizontal agar mirror
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    fist_detected = False
    punch_detected = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Gambar landmark (opsional)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Cek kepalan
            if is_fist(hand_landmarks):
                fist_detected = True
                last_fist_time = current_time

            # Deteksi pukulan berbasis velocity
            if fist_detected:
                if detect_punch_by_velocity(hand_landmarks, current_time, frame_width, frame_height):
                    punch_detected = True

    else:
        # Jika tangan tidak terdeteksi, cek apakah masih dalam masa "memory" untuk fist
        if current_time - last_fist_time < FIST_MEMORY_DURATION:
            fist_detected = True

    # Tampilkan status
    if punch_detected:
        cv2.putText(frame, "PUNCH!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        puch_countr += 1
    elif fist_detected:
        cv2.putText(frame, "FIST!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    else:
        cv2.putText(frame, "Open Hand", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    #tampilkan punch counter
    cv2.putText(frame, f"Punch Count: {puch_countr}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.imshow('Punch Detector (Velocity-Based) - Tekan Q untuk keluar', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
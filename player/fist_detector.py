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

# Variabel global untuk state memory
last_fist_time = 0
FIST_MEMORY_DURATION = 0.5  # detik

def is_fist(hand_landmarks):
    """
    Deteksi kepalan dengan kombinasi sudut dan jarak.
    Lebih stabil untuk berbagai orientasi.
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
    for finger_tip in [8, 12, 16, 20]:  # ujung telunjuk, tengah, manis, kelingking
        base = landmarks[finger_tip - 2]  # pangkal jari
        mid = landmarks[finger_tip - 1]   # tengah jari
        tip = landmarks[finger_tip]       # ujung jari
        angle = angle_between_points(base, mid, tip)
        angles.append(angle)

    avg_angle = np.mean(angles)

    # Hitung jarak rata-rata ujung jari ke telapak (landmark 9)
    palm_ref = landmarks[9]
    distances = [
        distance(landmarks[4], palm_ref),   # jempol
        distance(landmarks[8], palm_ref),   # telunjuk
        distance(landmarks[12], palm_ref),  # tengah
        distance(landmarks[16], palm_ref),  # manis
        distance(landmarks[20], palm_ref)   # kelingking
    ]
    avg_dist = np.mean(distances)

    # Kombinasi logika:
    angle_condition = avg_angle < 175  # sesuai settingmu
    dist_condition = avg_dist < 0.33   # sesuai settingmu
    cv2.putText(frame, f"Angle: {avg_angle:.1f}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Dist: {avg_dist:.3f}", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return angle_condition and dist_condition

# Buka kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    # Flip horizontal agar mirror
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    current_time = time.time()
    fist_detected = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Gambar landmark (opsional)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Cek kepalan
            if is_fist(hand_landmarks):
                fist_detected = True
                last_fist_time = current_time  # update waktu terakhir kepalan

    else:
        # Jika tangan tidak terdeteksi, cek apakah masih dalam masa "memory"
        if current_time - last_fist_time < FIST_MEMORY_DURATION:
            fist_detected = True  # tetap anggap fist

    # Tampilkan status
    if fist_detected:
        cv2.putText(frame, "FIST!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    else:
        cv2.putText(frame, "Open Hand", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    cv2.imshow('Fist Detector - Tekan Q untuk keluar', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
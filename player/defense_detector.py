import cv2
import mediapipe as mp
import numpy as np
import time

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Variabel global untuk state memory
last_defense_time = 0
DEFENSE_MEMORY_DURATION = 0.6

def get_face_bbox(face_landmarks, frame_width, frame_height):
    """
    Dapatkan bounding box wajah dari face landmarks.
    """
    x_coords = [lm.x * frame_width for lm in face_landmarks.landmark]
    y_coords = [lm.y * frame_height for lm in face_landmarks.landmark]
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    return x_min, y_min, x_max, y_max

def is_hand_in_face_bbox(hand_landmarks, face_bbox, frame_width, frame_height):
    """
    Cek apakah tangan berada di dalam bounding box wajah.
    """
    # Ambil titik tengah tangan
    x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
    y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
    hand_x = int(np.mean(x_coords))
    hand_y = int(np.mean(y_coords))

    x_min, y_min, x_max, y_max = face_bbox
    return x_min < hand_x < x_max and y_min < hand_y < y_max

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

    # Deteksi tangan dan wajah
    hand_results = hands.process(rgb)
    face_results = face_mesh.process(rgb)

    defense_detected = False

    if face_results.multi_face_landmarks and hand_results.multi_hand_landmarks:
        # Dapatkan bounding box wajah
        face_landmarks = face_results.multi_face_landmarks[0]
        face_bbox = get_face_bbox(face_landmarks, frame_width, frame_height)

        # Cek setiap tangan
        for hand_landmarks in hand_results.multi_hand_landmarks:
            if is_hand_in_face_bbox(hand_landmarks, face_bbox, frame_width, frame_height):
                defense_detected = True
                last_defense_time = current_time

        # Gambar bounding box wajah (opsional)
        x_min, y_min, x_max, y_max = face_bbox
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    else:
        # Jika wajah tidak terdeteksi, cek apakah tangan di tengah layar
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                x_coords = [lm.x * frame_width for lm in hand_landmarks.landmark]
                y_coords = [lm.y * frame_height for lm in hand_landmarks.landmark]
                hand_x = np.mean(x_coords)
                hand_y = np.mean(y_coords)

                # Cek apakah tangan di tengah layar (asumsi wajah di tengah)
                if (0.3 * frame_width < hand_x < 0.7 * frame_width and
                    0.2 * frame_height < hand_y < 0.6 * frame_height):
                    defense_detected = True
                    last_defense_time = current_time

    # State memory: jika tangan baru saja di depan wajah
    if not defense_detected:
        if current_time - last_defense_time < DEFENSE_MEMORY_DURATION:
            defense_detected = True

    # Tampilkan status
    if defense_detected:
        cv2.putText(frame, "BLOCKING!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
    else:
        cv2.putText(frame, "Open", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    cv2.imshow('Defense Detector - Tekan Q untuk keluar', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
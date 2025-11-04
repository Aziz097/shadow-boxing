import cv2
import mediapipe as mp
import numpy as np
import time
import random

# === Inisialisasi MediaPipe ===
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7)
pose = mp_pose.Pose(min_detection_confidence=0.7)

# === Enemy AI ===
class EnemyAI:
    def __init__(self):
        self.state = "IDLE"
        self.last_action_time = 0
        self.attack_target = None      # (x, y)
        self.attack_type = None        # "CENTER", "LEFT", "RIGHT"
        self.attack_start_time = 0
        self.attack_duration = 0.4
        self.recover_duration = 0.6

    def get_attack_type(self):
        return random.choice(["CENTER", "LEFT", "RIGHT"])

    def update(self, current_time, w, h, face_bbox=None, pose_landmarks=None):
        if self.state == "IDLE":
            if current_time - self.last_action_time > random.uniform(1.5, 2.5):
                self.attack_type = self.get_attack_type()
                
                # Tentukan target berdasarkan ketersediaan data
                if face_bbox:
                    self.attack_target = self._target_from_face(face_bbox, self.attack_type, w, h)
                elif pose_landmarks:
                    self.attack_target = self._target_from_pose(pose_landmarks, self.attack_type, w, h)
                else:
                    self.attack_target = (w // 2, h // 3)

                self.state = "ATTACKING"
                self.attack_start_time = current_time

        elif self.state == "ATTACKING":
            if current_time - self.attack_start_time > self.attack_duration:
                self.state = "RECOVERING"
                self.last_action_time = current_time

        elif self.state == "RECOVERING":
            if current_time - self.last_action_time > self.recover_duration:
                self.state = "IDLE"

    def _target_from_face(self, face_bbox, atk_type, w, h):
        x1, y1, x2, y2 = face_bbox
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        fw = x2 - x1
        if atk_type == "LEFT":
            return (x1, cy)
        elif atk_type == "RIGHT":
            return (x2, cy)
        else:
            return (cx, cy)

    def _target_from_pose(self, pose_landmarks, atk_type, w, h):
        # Gunakan landmark spesifik
        if atk_type == "LEFT":
            lm = pose_landmarks.landmark[3]  # left eye outer
        elif atk_type == "RIGHT":
            lm = pose_landmarks.landmark[4]  # right eye outer
        else:
            lm = pose_landmarks.landmark[0]  # nose

        if lm.visibility > 0.5:
            return (int(lm.x * w), int(lm.y * h))
        else:
            # Fallback: tengah atas
            return (w // 2, h // 3)

    def get_hand_position(self, current_time):
        if self.state == "ATTACKING":
            progress = min(1.0, (current_time - self.attack_start_time) / self.attack_duration)
            start_y = 600
            if self.attack_target:
                tx, ty = self.attack_target
                x = tx
                y = start_y + (ty - start_y) * progress
                return (int(x), int(y))
        return None

    def is_attacking(self):
        return self.state == "ATTACKING"

# === Helper Functions ===
def get_face_bbox(face_landmarks, w, h):
    xs = [lm.x * w for lm in face_landmarks.landmark]
    ys = [lm.y * h for lm in face_landmarks.landmark]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))

def is_defending(hand_landmarks, face_bbox, pose_landmarks, w, h):
    """
    Defense aktif jika tangan dekat dengan area target.
    """
    if not hand_landmarks:
        return False

    # Ambil posisi tangan
    hx = np.mean([lm.x * w for lm in hand_landmarks.landmark])
    hy = np.mean([lm.y * h for lm in hand_landmarks.landmark])

    # Jika face ada → cek overlap bbox
    if face_bbox:
        fx1, fy1, fx2, fy2 = face_bbox
        if fx1 < hx < fx2 and fy1 < hy < fy2:
            return True

    # Jika hanya pose → cek jarak ke landmark 0-6
    if pose_landmarks:
        for i in range(0, 7):  # nose, eyes, ears
            lm = pose_landmarks.landmark[i]
            if lm.visibility > 0.5:
                px, py = lm.x * w, lm.y * h
                dist = np.sqrt((hx - px)**2 + (hy - py)**2)
                if dist < 60:  # radius 60 pixel
                    return True
    return False

def is_hit(enemy_hand_pos, enemy_atk_type, face_bbox, pose_landmarks, w, h):
    """
    Hit valid jika:
    - Face ada → tangan lawan di dalam bbox (expanded)
    - Face tidak ada, tapi pose ada → tangan lawan dekat target landmark
    """
    if not enemy_hand_pos:
        return False

    ex, ey = enemy_hand_pos
    
    # Expanded hit detection radius for better accuracy
    hit_radius = 80  # pixels

    if face_bbox:
        fx1, fy1, fx2, fy2 = face_bbox
        # Expand bbox slightly for more forgiving detection
        fx1 -= 20
        fy1 -= 20
        fx2 += 20
        fy2 += 20
        return fx1 < ex < fx2 and fy1 < ey < fy2

    elif pose_landmarks:
        # Dapatkan target landmark berdasarkan tipe serangan
        if enemy_atk_type == "LEFT":
            target_lm = pose_landmarks.landmark[2]  # left eye
        elif enemy_atk_type == "RIGHT":
            target_lm = pose_landmarks.landmark[5]  # right eye
        else:
            target_lm = pose_landmarks.landmark[0]  # nose

        if target_lm.visibility > 0.5:
            tx = int(target_lm.x * w)
            ty = int(target_lm.y * h)
            dist = np.sqrt((ex - tx)**2 + (ey - ty)**2)
            return dist < hit_radius

    return False

# === Main Loop ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

enemy = EnemyAI()
last_defense_time = 0
DEFENSE_MEMORY = 0.5

while cap.isOpened():
    success, frame = cap.read()
    if not success: continue

    current_time = time.time()
    h, w = frame.shape[:2]
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Deteksi
    hand_results = hands.process(rgb)
    face_results = face_mesh.process(rgb)
    pose_results = pose.process(rgb)

    face_bbox = None
    if face_results.multi_face_landmarks:
        face_bbox = get_face_bbox(face_results.multi_face_landmarks[0], w, h)

    pose_landmarks = pose_results.pose_landmarks if pose_results.pose_landmarks else None

    # Deteksi defense
    defending = False
    if hand_results.multi_hand_landmarks:
        for hand_lm in hand_results.multi_hand_landmarks:
            if is_defending(hand_lm, face_bbox, pose_landmarks, w, h):
                defending = True
                last_defense_time = current_time
                break

    # State memory untuk defense
    if not defending and (current_time - last_defense_time < DEFENSE_MEMORY):
        defending = True

    # Update lawan
    enemy.update(current_time, w, h, face_bbox, pose_landmarks)

    # Deteksi hit
    hit_result = "NONE"
    enemy_hand_pos = enemy.get_hand_position(current_time)
    if enemy.is_attacking() and enemy_hand_pos:
        if is_hit(enemy_hand_pos, enemy.attack_type, face_bbox, pose_landmarks, w, h):
            if defending:
                hit_result = "BLOCKED"
            else:
                hit_result = "HIT!"

    # Visualisasi
    if enemy_hand_pos:
        color = (0, 0, 255)  # merah
        cv2.circle(frame, enemy_hand_pos, 30, color, -1)
        cv2.circle(frame, enemy_hand_pos, 35, (255, 255, 255), 2)

    # Gambar target (opsional, untuk debug)
    if enemy.attack_target:
        cv2.circle(frame, enemy.attack_target, 10, (0, 255, 0), -1)

    # Gambar face bbox
    if face_bbox:
        cv2.rectangle(frame, (face_bbox[0], face_bbox[1]), (face_bbox[2], face_bbox[3]), (0, 255, 0), 2)

    # Status
    if hit_result == "HIT!":
        cv2.putText(frame, "HIT!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    elif hit_result == "BLOCKED":
        cv2.putText(frame, "BLOCKED!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
    else:
        status = "Defending" if defending else "Ready"
        cv2.putText(frame, status, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

    cv2.putText(frame, f"Attack: {enemy.attack_type}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow('Enemy Hit Tester v3 - Tekan Q', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
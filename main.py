"""
Shadow Boxing - Main Game
Game tinju interaktif dengan deteksi gerakan MediaPipe

Controls:
- SPACE: Start round / Continue
- Q: Quit game
- D: Change difficulty (EASY/MEDIUM/HARD)
- S: Toggle sound
"""
import os
import sys
import time

import cv2
import numpy as np

# Reduce verbose logs from MediaPipe/TFLite before importing mediapipe
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import mediapipe as mp

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game components
from game.sound_manager import SoundManager
from game.game_state import GameState
from game.round_manager import RoundManager
from game.visual_effects import VisualEffects
from enemy.enhanced_enemy_ai import EnemyAI

# Import utility functions
from utils import is_fist, get_hand_center

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7)
pose = mp_pose.Pose(min_detection_confidence=0.7)

# === Helper Functions ===
def get_face_bbox(face_landmarks, w, h):
    """Get face bounding box"""
    xs = [lm.x * w for lm in face_landmarks.landmark]
    ys = [lm.y * h for lm in face_landmarks.landmark]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))

def is_defending(hand_landmarks, face_bbox, pose_landmarks, w, h):
    """Check if player is defending"""
    if not hand_landmarks:
        return False
    
    hx = np.mean([lm.x * w for lm in hand_landmarks.landmark])
    hy = np.mean([lm.y * h for lm in hand_landmarks.landmark])
    
    if face_bbox:
        fx1, fy1, fx2, fy2 = face_bbox
        if fx1 < hx < fx2 and fy1 < hy < fy2:
            return True
    
    if pose_landmarks:
        for i in range(0, 7):
            lm = pose_landmarks.landmark[i]
            if lm.visibility > 0.5:
                px, py = lm.x * w, lm.y * h
                dist = np.sqrt((hx - px)**2 + (hy - py)**2)
                if dist < 80:
                    return True
    
    return False

def is_hit(enemy_hand_pos, enemy_atk_type, face_bbox, pose_landmarks, w, h):
    """Check if enemy hit landed"""
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

def check_player_punch_hit(hand_pos, enemy_ai, frame_width, frame_height):
    """Check if player punch hit vulnerable enemy"""
    if not enemy_ai.is_vulnerable() or hand_pos is None:
        return False
    
    # Simple collision check - punch hit if hand near center screen
    # (where enemy head would be)
    x, y = hand_pos
    
    # Enemy head area (top-center of screen)
    enemy_head_x = frame_width // 2
    enemy_head_y = int(frame_height * 0.28)
    dist = np.sqrt((x - enemy_head_x)**2 + (y - enemy_head_y)**2)
    
    # Slightly forgiving radius to account for detection noise
    hit_radius = max(frame_width, frame_height) * 0.08
    return dist < hit_radius  # hit radius

# === Main Game Class ===
class ShadowBoxingGame:
    """Main game controller"""
    
    def __init__(self):
        """Initialize game"""
        # Game components
        self.sound = SoundManager()
        self.game_state = GameState()
        self.round_manager = RoundManager(total_rounds=3, round_duration=60, rest_duration=10)
        self.vfx = VisualEffects()
        self.difficulty = "MEDIUM"
        self.enemy = EnemyAI(difficulty=self.difficulty)
        self.match_over_announced = False
        self.last_round_summary = None
        
        # Defense tracking
        self.last_defense_time = 0
        self.defense_memory = 0.5
        
        # Punch tracking
        self.prev_hand_pos = None
        self.prev_time = 0
        self.last_punch_time = 0
        self.punch_cooldown = 0.3
        self.last_fist_time = 0
        self.fist_memory = 0.5
        
        # Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("\n=== Shadow Boxing Game Initialized ===")
        print(f"Difficulty: {self.difficulty}")
        print("Press SPACE to start first round")
    
    def change_difficulty(self):
        """Cycle through difficulty levels"""
        difficulties = ["EASY", "MEDIUM", "HARD"]
        current_idx = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_idx + 1) % 3]
        self.enemy = EnemyAI(difficulty=self.difficulty)
        print(f"Difficulty changed to: {self.difficulty}")
    
    def detect_player_punch(self, hand_landmarks, current_time, w, h, is_fist_detected):
        """Detect player punch"""
        if not is_fist_detected:
            self.prev_hand_pos = None
            return False
        
        hand_pos = get_hand_center(hand_landmarks, w, h)
        
        if self.prev_hand_pos is not None and self.prev_time != 0:
            delta_time = current_time - self.prev_time
            
            if delta_time > 0:
                velocity = (hand_pos - self.prev_hand_pos) / delta_time
                speed = np.linalg.norm(velocity)
                
                if speed > 800:  # velocity threshold
                    face_center = np.array([w // 2, h // 2])
                    to_face = face_center - hand_pos
                    
                    if np.linalg.norm(to_face) > 0:
                        to_face = to_face / np.linalg.norm(to_face)
                        velocity_norm = velocity / np.linalg.norm(velocity)
                        cos_theta = np.dot(velocity_norm, to_face)
                        
                        if cos_theta > 0.5:
                            if current_time - self.last_punch_time > self.punch_cooldown:
                                self.last_punch_time = current_time
                                self.prev_hand_pos = hand_pos
                                self.prev_time = current_time
                                return True
        
        self.prev_hand_pos = hand_pos
        self.prev_time = current_time
        return False
    
    def run(self):
        """Main game loop"""
        print("\nGame Started!")
        print("Controls: SPACE=Start/Continue, Q=Quit, D=Difficulty, S=Toggle Sound\n")
        
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                continue
            
            current_time = time.time()
            h, w = frame.shape[:2]
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process MediaPipe detections
            hand_results = hands.process(rgb)
            face_results = face_mesh.process(rgb)
            pose_results = pose.process(rgb)
            
            # Get face bbox
            face_bbox = None
            if face_results.multi_face_landmarks:
                face_bbox = get_face_bbox(face_results.multi_face_landmarks[0], w, h)
            
            pose_landmarks = pose_results.pose_landmarks if pose_results.pose_landmarks else None
            
            # === GAME LOGIC ===
            if self.round_manager.is_fighting() and not self.game_state.game_over:
                # Update round timer
                self.round_manager.update(current_time)
                
                # Update enemy AI
                self.enemy.update(current_time, w, h, face_bbox, pose_landmarks, self.game_state)
                
                # Detect player defense
                defending = False
                if hand_results.multi_hand_landmarks:
                    for hand_lm in hand_results.multi_hand_landmarks:
                        if is_defending(hand_lm, face_bbox, pose_landmarks, w, h):
                            defending = True
                            self.last_defense_time = current_time
                            break
                
                # Defense memory
                if not defending and (current_time - self.last_defense_time < self.defense_memory):
                    defending = True
                
                # Detect player fist and punch
                fist_detected = False
                punch_landed = False
                
                if hand_results.multi_hand_landmarks:
                    for hand_lm in hand_results.multi_hand_landmarks:
                        if is_fist(hand_lm):
                            fist_detected = True
                            self.last_fist_time = current_time
                            
                            # Check for punch
                            if self.detect_player_punch(hand_lm, current_time, w, h, True):
                                self.game_state.player_punch_attempt()
                                
                                # Check if hit vulnerable enemy
                                hand_pos = get_hand_center(hand_lm, w, h)
                                if check_player_punch_hit(hand_pos, self.enemy, w, h):
                                    if self.game_state.player_hit_enemy(current_time):
                                        self.sound.play_punch()
                                        punch_landed = True
                                        self.enemy.take_damage()
                                        print(f"Player hit! Enemy HP: {self.game_state.enemy_hp}")
                
                # Fist memory
                if not fist_detected and (current_time - self.last_fist_time < self.fist_memory):
                    fist_detected = True
                
                # Check enemy attack
                enemy_hand_pos = self.enemy.get_hand_position(current_time)
                if self.enemy.is_attacking() and enemy_hand_pos:
                    if is_hit(enemy_hand_pos, self.enemy.attack_type, face_bbox, pose_landmarks, w, h):
                        if defending:
                            self.game_state.player_blocked()
                            self.sound.play_block()
                            print("Blocked!")
                        else:
                            if self.game_state.enemy_hit_player(current_time):
                                self.sound.play_hit()
                                self.vfx.trigger_hit_flash()
                                print(f"Hit taken! Player HP: {self.game_state.player_hp}")
                
                # Check round end
                if self.round_manager.get_remaining_time(current_time) <= 0:
                    # Round over - determine winner
                    player_score = self.game_state.player_punches_landed
                    enemy_score = self.game_state.enemy_hits_landed
                    winner = self.round_manager.get_round_winner(player_score, enemy_score)
                    self.round_manager.end_round(winner)
                    print(f"\nRound {self.round_manager.current_round} Over!")
                    print(f"Winner: {winner}")
                    print(f"Score - Player: {player_score}, Enemy: {enemy_score}\n")
            
            # === VISUAL RENDERING ===
            # Draw base elements
            frame = self.vfx.draw_hp_bars(frame, self.game_state)
            frame = self.vfx.draw_stamina_bar(frame, self.enemy)
            frame = self.vfx.draw_round_info(frame, self.round_manager, current_time)
            
            if self.round_manager.is_fighting():
                frame = self.vfx.draw_stats_overlay(frame, self.game_state)
                frame = self.vfx.draw_telegraph_warning(frame, self.enemy, current_time)
                frame = self.vfx.draw_enemy_punch(frame, self.enemy, current_time)
                frame = self.vfx.draw_combo_indicator(frame, self.enemy)
                frame = self.vfx.draw_vulnerable_indicator(frame, self.enemy)
                frame = self.vfx.draw_hit_flash(frame, current_time)
            
            frame = self.vfx.draw_game_over(frame, self.game_state)
            
            # Draw face bbox (debug)
            if face_bbox:
                cv2.rectangle(frame, (face_bbox[0], face_bbox[1]), 
                            (face_bbox[2], face_bbox[3]), (0, 255, 0), 2)
            
            # Draw hand landmarks
            if hand_results.multi_hand_landmarks:
                for hand_lm in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)
            
            # Show difficulty indicator
            cv2.putText(frame, f"Difficulty: {self.difficulty}", 
                       (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Shadow Boxing - Press Q to quit', frame)
            
            # === KEYBOARD INPUT ===
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):  # SPACE
                if self.round_manager.is_ready():
                    self.round_manager.start_round()
                    self.game_state.reset()
                    self.enemy = EnemyAI(difficulty=self.difficulty)
                    print(f"Round {self.round_manager.current_round} START!")
                elif self.round_manager.is_finished() or self.game_state.game_over:
                    # Restart game (match finished or KO)
                    self.round_manager.reset()
                    self.game_state.reset()
                    self.enemy = EnemyAI(difficulty=self.difficulty)
                    print("\n=== New Game Started! ===")
                    print(f"Difficulty: {self.difficulty}")
                    print("Press SPACE to start first round\n")
            elif key == ord('d'):
                self.change_difficulty()
            elif key == ord('s'):
                enabled = self.sound.toggle_sound()
                print(f"Sound: {'ON' if enabled else 'OFF'}")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("\nGame Over! Thanks for playing!")

# === Entry Point ===
if __name__ == "__main__":
    try:
        game = ShadowBoxingGame()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

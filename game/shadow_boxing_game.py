"""Main game controller coordinating input detection, state, and rendering."""

from __future__ import annotations

import time
from typing import Optional

import cv2
import numpy as np

from detection import (
    MediaPipePipeline,
    check_player_punch_hit,
    get_face_bbox,
    is_defending,
    is_hit,
)
from enemy.enhanced_enemy_ai import EnemyAI
from game.game_state import GameState
from game.round_manager import RoundManager
from game.sound_manager import SoundManager
from game.visual_effects import VisualEffects
from utils import get_hand_center, is_fist


class ShadowBoxingGame:
    # Main game controller that glues MediaPipe input with game logic.

    def __init__(self, pipeline: Optional[MediaPipePipeline] = None, camera_index: int = 0) -> None:
        """Initialize the game components."""
        self.sound = SoundManager()
        self.game_state = GameState()
        self.round_manager = RoundManager(total_rounds=3, round_duration=60, rest_duration=10)
        self.vfx = VisualEffects()
        self.difficulty = "MEDIUM"
        self.enemy = EnemyAI(difficulty=self.difficulty)
        self.match_over_announced = False
        self.last_round_summary = None

        # Track previous round state for detecting changes
        self.prev_round_state = "READY"
        self.prev_round_number = 1

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

        # MediaPipe pipeline
        self.pipeline = pipeline or MediaPipePipeline()

        # Drawing helpers
        self._drawing_utils = self.pipeline.drawing_utils
        self._hand_connections = self.pipeline.hand_connections

        # Camera
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("\n=== Shadow Boxing Game Initialized ===")
        print(f"Difficulty: {self.difficulty}")
        print("Press SPACE to start first round")

    def change_difficulty(self) -> None:
        """Cycle through difficulty levels."""
        difficulties = ["EASY", "MEDIUM", "HARD"]
        current_idx = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_idx + 1) % 3]
        self.enemy = EnemyAI(difficulty=self.difficulty)
        print(f"Difficulty changed to: {self.difficulty}")

    def detect_player_punch(self, hand_landmarks, current_time, frame_width: int, frame_height: int, is_fist_detected: bool) -> bool:
        """Detect player punch based on hand velocity towards the target."""
        if not is_fist_detected:
            self.prev_hand_pos = None
            return False

        hand_pos = get_hand_center(hand_landmarks, frame_width, frame_height)

        if self.prev_hand_pos is not None and self.prev_time != 0:
            delta_time = current_time - self.prev_time

            if delta_time > 0:
                velocity = (hand_pos - self.prev_hand_pos) / delta_time
                speed = np.linalg.norm(velocity)

                # Lowered threshold from 800 to 450 for easier punch detection
                if speed > 450:  # velocity threshold
                    face_center = np.array([frame_width // 2, frame_height // 2])
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
                                print(f"PUNCH DETECTED! Speed: {speed:.1f}")  # Debug
                                return True

        self.prev_hand_pos = hand_pos
        self.prev_time = current_time
        return False

    def run(self) -> None:
        """Main game loop."""
        print("\nGame Started!")
        print("Controls: SPACE=Start/Continue, Q=Quit, D=Difficulty, S=Toggle Sound\n")

        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    continue

                current_time = time.time()
                frame_height, frame_width = frame.shape[:2]
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process MediaPipe detections
                hand_results, face_results, pose_results = self.pipeline.process(rgb)

                # Get face bbox
                face_bbox = None
                if face_results.multi_face_landmarks:
                    face_bbox = get_face_bbox(face_results.multi_face_landmarks[0], frame_width, frame_height)

                pose_landmarks = pose_results.pose_landmarks if pose_results.pose_landmarks else None

                # === GAME LOGIC ===
                # Always update round manager (including during REST)
                self.round_manager.update(current_time)

                # Detect round state changes (for notifications)
                if (
                    self.round_manager.state == "FIGHTING"
                    and (self.prev_round_state != "FIGHTING" or self.prev_round_number != self.round_manager.current_round)
                ):
                    # Round just started!
                    self.vfx.show_round_start(self.round_manager.current_round)

                self.prev_round_state = self.round_manager.state
                self.prev_round_number = self.round_manager.current_round

                if self.round_manager.is_fighting() and not self.game_state.game_over:
                    # Update enemy AI
                    self.enemy.update(current_time, frame_width, frame_height, face_bbox, pose_landmarks, self.game_state)

                    # Detect player defense
                    defending = False
                    if hand_results.multi_hand_landmarks:
                        for hand_lm in hand_results.multi_hand_landmarks:
                            if is_defending(hand_lm, face_bbox, pose_landmarks, frame_width, frame_height):
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
                                if self.detect_player_punch(hand_lm, current_time, frame_width, frame_height, True):
                                    self.game_state.player_punch_attempt()

                                    # Check if hit vulnerable enemy
                                    hand_pos = get_hand_center(hand_lm, frame_width, frame_height)

                                    # Debug vulnerability
                                    if not self.enemy.is_vulnerable():
                                        print("Enemy NOT vulnerable - can't hit yet!")

                                    if check_player_punch_hit(hand_pos, self.enemy, frame_width, frame_height):
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
                        if is_hit(enemy_hand_pos, self.enemy.attack_type, face_bbox, pose_landmarks, frame_width, frame_height):
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

                # Draw round start notification (on top of everything)
                frame = self.vfx.draw_round_notification(frame, current_time)

                # Draw face bbox (debug)
                if face_bbox:
                    cv2.rectangle(frame, (face_bbox[0], face_bbox[1]), (face_bbox[2], face_bbox[3]), (0, 255, 0), 2)

                # Draw hand landmarks
                if hand_results.multi_hand_landmarks:
                    for hand_lm in hand_results.multi_hand_landmarks:
                        self._drawing_utils.draw_landmarks(frame, hand_lm, self._hand_connections)

                # Show difficulty indicator
                cv2.putText(
                    frame,
                    f"Difficulty: {self.difficulty}",
                    (10, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2,
                )

                # Display frame
                cv2.imshow("Shadow Boxing - Press Q to quit", frame)

                # === KEYBOARD INPUT ===
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
                if key == ord(" "):  # SPACE
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
                elif key == ord("d"):
                    self.change_difficulty()
                elif key == ord("s"):
                    enabled = self.sound.toggle_sound()
                    print(f"Sound: {'ON' if enabled else 'OFF'}")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.pipeline.close()
            print("\nGame Over! Thanks for playing!")

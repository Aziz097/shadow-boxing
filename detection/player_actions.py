"""Helper routines for evaluating player actions and enemy interactions."""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np


def get_face_bbox(face_landmarks, frame_width: int, frame_height: int) -> Tuple[int, int, int, int]:
    """Return a bounding box surrounding the detected face landmarks."""
    xs = [lm.x * frame_width for lm in face_landmarks.landmark]
    ys = [lm.y * frame_height for lm in face_landmarks.landmark]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))


def is_defending(hand_landmarks, face_bbox, pose_landmarks, frame_width: int, frame_height: int) -> bool:
    """Determine whether the player's hand is positioned defensively."""
    if not hand_landmarks:
        return False

    hx = np.mean([lm.x * frame_width for lm in hand_landmarks.landmark])
    hy = np.mean([lm.y * frame_height for lm in hand_landmarks.landmark])

    if face_bbox:
        fx1, fy1, fx2, fy2 = face_bbox
        if fx1 < hx < fx2 and fy1 < hy < fy2:
            return True

    if pose_landmarks:
        for idx in range(7):
            landmark = pose_landmarks.landmark[idx]
            if landmark.visibility > 0.5:
                px, py = landmark.x * frame_width, landmark.y * frame_height
                dist = np.sqrt((hx - px) ** 2 + (hy - py) ** 2)
                if dist < 80:
                    return True

    return False


def is_hit(
    enemy_hand_pos: Optional[Tuple[int, int]],
    enemy_atk_type: str,
    face_bbox,
    pose_landmarks,
    frame_width: int,
    frame_height: int,
) -> bool:
    """Determine whether the enemy landed a hit on the player."""
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

    if pose_landmarks:
        if enemy_atk_type == "LEFT":
            target_lm = pose_landmarks.landmark[2]  # left eye
        elif enemy_atk_type == "RIGHT":
            target_lm = pose_landmarks.landmark[5]  # right eye
        else:
            target_lm = pose_landmarks.landmark[0]  # nose

        if target_lm.visibility > 0.5:
            tx = int(target_lm.x * frame_width)
            ty = int(target_lm.y * frame_height)
            dist = np.sqrt((ex - tx) ** 2 + (ey - ty) ** 2)
            return dist < hit_radius

    return False


def check_player_punch_hit(hand_pos, enemy_ai, frame_width: int, frame_height: int) -> bool:
    """Determine whether the player's punch connected with a vulnerable enemy."""
    if not enemy_ai.is_vulnerable() or hand_pos is None:
        return False

    x, y = hand_pos

    # Enemy head area (top-center of screen)
    enemy_head_x = frame_width // 2
    enemy_head_y = int(frame_height * 0.28)
    dist = np.sqrt((x - enemy_head_x) ** 2 + (y - enemy_head_y) ** 2)

    # More forgiving radius - increased from 0.08 to 0.12
    hit_radius = max(frame_width, frame_height) * 0.12

    is_punch_hit = dist < hit_radius
    if is_punch_hit:
        print(f"PLAYER HIT ENEMY! Distance: {dist:.1f}, Radius: {hit_radius:.1f}")

    return is_punch_hit

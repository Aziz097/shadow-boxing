"""Encapsulate MediaPipe detector setup and processing."""

from __future__ import annotations

from typing import Any, Tuple

import mediapipe as mp


class MediaPipePipeline:
    """Wrapper around MediaPipe solutions used by the game loop."""

    def __init__(
        self,
        hand_confidence: float = 0.7,
        face_confidence: float = 0.7,
        pose_confidence: float = 0.7,
        max_hands: int = 2,
        max_faces: int = 1,
    ) -> None:
        self._mp_hands = mp.solutions.hands
        self._mp_face_mesh = mp.solutions.face_mesh
        self._mp_pose = mp.solutions.pose
        self._drawing_utils = mp.solutions.drawing_utils

        self._hands = self._mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=hand_confidence,
        )
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            max_num_faces=max_faces,
            min_detection_confidence=face_confidence,
        )
        self._pose = self._mp_pose.Pose(
            min_detection_confidence=pose_confidence,
        )

    @property
    def hand_connections(self):
        return self._mp_hands.HAND_CONNECTIONS

    @property
    def drawing_utils(self):
        return self._drawing_utils

    def process(self, rgb_frame) -> Tuple[Any, Any, Any]:
        """Run inference on the provided RGB frame."""
        hand_results = self._hands.process(rgb_frame)
        face_results = self._face_mesh.process(rgb_frame)
        pose_results = self._pose.process(rgb_frame)
        return hand_results, face_results, pose_results

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()
        self._face_mesh.close()
        self._pose.close()

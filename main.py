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

# Reduce verbose logs from MediaPipe/TFLite before importing mediapipe
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Add parent directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.shadow_boxing_game import ShadowBoxingGame


def main() -> None:
    """Entry point for starting the Shadow Boxing game."""
    game = ShadowBoxingGame()
    game.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as exc:  # pragma: no cover - runtime safeguard
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()

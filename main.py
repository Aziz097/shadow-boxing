"""
Shadow Boxing Game
Main Entry Point

Controls:
- SPACE: Start game
- ESC: Pause menu
- Q: Quit game

Game Flow:
- 3 Rounds, 20 seconds each
- Player attack phase: Hit targets within 3 seconds
- Enemy attack phase: Block with hands to defend
- 10 second rest between rounds
"""
import sys
import cv2
import time

from game.game_manager import GameManager
import config


def print_welcome():
    """Print welcome message."""
    print("="*60)
    print(" " * 15 + "SHADOW BOXING GAME")
    print("="*60)
    print()
    print("CONTROLS:")
    print("  SPACE - Start Game")
    print("  ESC   - Pause/Resume")
    print("  Q     - Quit")
    print()
    print("GAMEPLAY:")
    print("  - Punch the colored targets when they appear")
    print("  - Block enemy attacks by covering your face with hands")
    print("  - Hit more targets in combo for bonus damage!")
    print("  - 3 Rounds, 20 seconds each")
    print()
    print("="*60)
    print()


def main():
    """Main entry point."""
    print_welcome()
    
    try:
        # Create game manager
        game = GameManager()
        
        # Initialize systems
        if not game.initialize():
            print("Failed to initialize game!")
            print("Make sure your webcam is connected.")
            return 1
        
        print("Game started! Press SPACE to begin...")
        print()
        
        # Run game loop
        game.run()
        
        print("\nGame ended. Thanks for playing!")
        return 0
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

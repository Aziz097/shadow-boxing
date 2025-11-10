"""
Simple test script to verify basic functionality
Run this before running the full game
"""
import sys

print("="*60)
print("SHADOW BOXING - Quick Test")
print("="*60)

# Test 1: Import config
print("\n[1/6] Testing config import...")
try:
    import config
    print("✓ Config imported successfully")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    sys.exit(1)

# Test 2: Import utils
print("\n[2/6] Testing utils import...")
try:
    import utils
    print("✓ Utils imported successfully")
except Exception as e:
    print(f"✗ Utils import failed: {e}")
    sys.exit(1)

# Test 3: Import systems
print("\n[3/6] Testing systems import...")
try:
    from systems.camera_manager import CameraManager
    from systems.mediapipe_manager import MediaPipeManager
    from systems.audio_system import AudioManager
    from systems.visual_effects import VisualEffectsManager
    print("✓ All systems imported successfully")
except Exception as e:
    print(f"✗ Systems import failed: {e}")
    sys.exit(1)

# Test 4: Import player
print("\n[4/6] Testing player import...")
try:
    from player.player import Player
    player = Player()
    print(f"✓ Player created successfully (Health: {player.current_health})")
except Exception as e:
    print(f"✗ Player import failed: {e}")
    sys.exit(1)

# Test 5: Import enemy
print("\n[5/6] Testing enemy import...")
try:
    from enemy.enemy import Enemy
    enemy = Enemy()
    print(f"✓ Enemy created successfully (Health: {enemy.current_health})")
except Exception as e:
    print(f"✗ Enemy import failed: {e}")
    sys.exit(1)

# Test 6: Import game manager
print("\n[6/6] Testing game manager import...")
try:
    from game.game_manager import GameManager
    print("✓ Game manager imported successfully")
except Exception as e:
    print(f"✗ Game manager import failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nYou can now run the game with:")
print("  python main.py")
print()

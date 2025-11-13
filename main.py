import warnings
import os
import pygame
import cv2
import time
import random
import math
import numpy as np
from core.config import Config
from systems.vision_system import VisionSystem
from systems.audio_system import AudioSystem
from systems.render_system import RenderSystem
from systems.input_processor import InputProcessor
from entities.player.player import Player
from entities.enemy.enemy import Enemy
from entities.enemy.ai_controller import AIController
from entities.enemy.enemy_attack_system import EnemyAttackSystem
from game.round_manager import RoundManager
from game.game_state import GameState
from ui.hud_renderer import HUDRenderer
from ui.menu_system import MenuSystem
from ui.fight_overlay import FightOverlay
from ui.result_screen import ResultScreen
from core import constants

# Suppress protobuf deprecated warning
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs

def main():
    # Initialize configuration
    game_config = Config()
    
    # Debug font path
    print(f"=== CONFIG DEBUG ===")
    print(f"FONT_PATH: {game_config.FONT_PATH}")
    print(f"Font exists: {os.path.exists(game_config.FONT_PATH)}")
    print(f"Font directory exists: {os.path.exists(game_config.FONT_DIR)}")
    
    # Initialize systems
    vision_system = VisionSystem(game_config)
    audio_system = AudioSystem(game_config)
    render_system = RenderSystem(game_config)
    input_processor = InputProcessor(game_config)
    
    # Initialize game entities
    player = Player(game_config)
    enemy = Enemy(game_config)
    ai_controller = AIController(game_config, enemy)
    round_manager = RoundManager(game_config)
    game_state = GameState(game_config)
    
    # Initialize UI components
    hud_renderer = HUDRenderer(game_config, render_system)
    menu_system = MenuSystem(game_config, render_system, vision_system) 
    fight_overlay = FightOverlay(game_config)
    result_screen = ResultScreen(game_config)
    
    # Game state variables
    running = True
    last_update_time = time.time()
    clock = pygame.time.Clock()
    last_camera_frame = None
    
    # Play menu music
    try:
        audio_system.play_music("menu", 0.5)
    except Exception as e:
        print(f"Error playing menu music: {str(e)}")
    
    while running:
        current_time = time.time()
        delta_time = current_time - last_update_time
        last_update_time = current_time
        
        # Get camera frame
        vision_data = vision_system.get_frame()
        if vision_data is None:
            continue
        last_camera_frame = vision_data['frame']
        
        # Handle Pygame events
        pygame_event = render_system.handle_events()
        command = None
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        
        # Global quit keys
        if keys[pygame.K_q]:
            running = False
        
        # Handle game state transitions
        if game_state.current_state == constants.GAME_STATES['MENU']:
            # Let menu system handle input
            menu_command = menu_system.handle_input(keys)
            if menu_command == "START":
                # Start game
                game_state.start_game()
                show_round_overlay = True
                fight_overlay.show_round_start(1)
                
                # Stop menu music and play fight music
                try:
                    audio_system.stop_music()
                    audio_system.play_music("fight", 0.3)
                except Exception as e:
                    print(f"Error changing music: {str(e)}")
            elif menu_command == "QUIT":
                running = False
            elif keys[pygame.K_ESCAPE]:
                running = False
        
        elif game_state.current_state == constants.GAME_STATES['ROUND_SPLASH']:
            # Play round sound once
            if not hasattr(game_state, 'round_sound_played') or not game_state.round_sound_played:
                try:
                    round_sound = f"round_{game_state.current_round}"
                    audio_system.play_sound(round_sound)
                    game_state.round_sound_played = True
                except Exception as e:
                    print(f"Error playing round sound: {str(e)}")
            
            # Wait for overlay to finish
            if not fight_overlay.is_active():
                game_state.start_round(game_state.current_round)
                try:
                    audio_system.play_sound("bell")
                except Exception as e:
                    print(f"Error playing bell sound: {str(e)}")
        
        elif game_state.current_state == constants.GAME_STATES['PLAYING']:
            # Process input
            input_processor.process_input(vision_data, game_state)
            
            # Get face bbox for defense and store results for helm rendering
            game_state.face_bbox = vision_system.get_face_bbox(vision_data['face'])
            game_state.face_results = vision_data['face']
            game_state.pose_results = vision_data['pose']
            game_state.hand_results = vision_data['hands']  # For hand skeleton rendering
            
            # Update game state (phase transitions, timers, etc)
            game_state.update(current_time, vision_system)
            
            # Update player and enemy
            player.health = game_state.player_health
            enemy.health = game_state.enemy_health
            player.score = game_state.score
            
            # Check for round end
            if game_state.round_timer <= 0 and game_state.current_round >= game_config.NUM_ROUNDS:
                game_state.current_state = constants.GAME_STATES['GAME_OVER']
                player_won = player.health > enemy.health
                result_screen.show(player_won, player.score)
                try:
                    audio_system.play_sound("ko" if not player_won else "strong_punch")
                except Exception as e:
                    print(f"Error playing game over sound: {str(e)}")
        
        elif game_state.current_state == constants.GAME_STATES['REST']:
            if current_time - game_state.rest_start_time >= game_config.REST_DURATION:
                game_state.current_round += 1
                if game_state.current_round <= game_config.NUM_ROUNDS:
                    game_state.current_state = constants.GAME_STATES['ROUND_SPLASH']
                    fight_overlay.show_round_start(game_state.current_round)
                    game_state.round_sound_played = False
                else:
                    game_state.current_state = constants.GAME_STATES['GAME_OVER']
                    player_won = player.health > enemy.health
                    result_screen.show(player_won, player.score)
        
        elif game_state.current_state == constants.GAME_STATES['GAME_OVER']:
            if command == "SPACE" or keys[pygame.K_RETURN]:
                # Restart game
                player = Player(game_config)
                enemy = Enemy(game_config)
                round_manager = RoundManager(game_config)
                game_state = GameState(game_config)
                game_state.current_state = constants.GAME_STATES['MENU']
                try:
                    audio_system.play_music("menu", 0.5)
                except Exception as e:
                    print(f"Error restarting music: {str(e)}")
            elif pygame_event == False:  # Q or ESC
                running = False
        
        # Update game_state timers
        if game_state.current_state == constants.GAME_STATES['PLAYING']:
            game_state.round_timer = max(0, game_config.ROUND_DURATION - (current_time - game_state.round_start_time))
        elif game_state.current_state == constants.GAME_STATES['REST']:
            game_state.rest_timer = max(0, game_config.REST_DURATION - (current_time - game_state.rest_start_time))
        
        # Update health values
        game_state.player_health = player.health
        game_state.enemy_health = enemy.health
        
        # Render frame
        render_system.render_frame(vision_data['frame'], game_state)
        
        # Render overlays
        if game_state.current_state in [constants.GAME_STATES['ROUND_SPLASH'], constants.GAME_STATES['PLAYING']]:
            fight_overlay.render(render_system.screen)
        
        # Render UI based on state
        if game_state.current_state == constants.GAME_STATES['MENU']:
            menu_system.render(render_system.screen, camera_frame=vision_data['frame'])
        elif game_state.current_state == constants.GAME_STATES['PLAYING']:
            hud_renderer.render_hud(game_state, render_system.screen)
        elif game_state.current_state == constants.GAME_STATES['GAME_OVER']:
            result_screen.render(render_system.screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(game_config.FPS)
    
    # Clean up resources
    vision_system.release()
    render_system.close()
    pygame.quit()

if __name__ == "__main__":
    main()
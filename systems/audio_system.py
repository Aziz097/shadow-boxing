import pygame
import os
from core import config

class AudioSystem:
    def __init__(self, game_config):
        self.config = game_config
        pygame.mixer.init()
        
        # Load sound effects dengan path yang benar
        self.sounds = {
            'bell': self._load_sound("boxing-bell.mp3"),
            'ko': self._load_sound("KO.mp3"),
            'weak_punch': self._load_sound("weak-punch.mp3"),
            'strong_punch': self._load_sound("strongpunch.mp3"),
            'meme_punch': self._load_sound("punch-meme.mp3"),
            'round_1': self._load_sound(os.path.join("round", "round-1.mp3")),
            'round_2': self._load_sound(os.path.join("round", "round-2.mp3")),
            'round_3': self._load_sound(os.path.join("round", "round-3.mp3"))
        }
        
        # Load background music
        self.music = {
            'menu': os.path.join(self.config.MUSIC_DIR, "menu_music.mp3"),
            'fight': os.path.join(self.config.MUSIC_DIR, "fight_music.mp3"),
            'ko': os.path.join(self.config.MUSIC_DIR, "ko_music.mp3")
        }
        
        print("Audio system initialized with sounds:", list(self.sounds.keys()))
    
    def _load_sound(self, filename):
        """Load sound with error handling"""
        # Handle subdirectories
        if isinstance(filename, tuple):
            path = os.path.join(self.config.SFX_DIR, *filename)
        else:
            path = os.path.join(self.config.SFX_DIR, filename)
        
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Warning: Failed to load sound {path}: {str(e)}")
                return None
        else:
            print(f"Warning: Sound file not found: {path}")
            return None
    
    def play_sound(self, sound_name, volume=1.0):
        """Play sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].set_volume(volume)
                self.sounds[sound_name].play()
                print(f"Playing sound: {sound_name}")
            except Exception as e:
                print(f"Error playing sound {sound_name}: {str(e)}")
        else:
            print(f"Sound not found or not loaded: {sound_name}")
    
    def play_music(self, music_name, volume=0.5, loops=-1):
        """Play background music"""
        if music_name in self.music:
            music_path = self.music[music_name]
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loops)
                    print(f"Playing music: {music_name}")
                except Exception as e:
                    print(f"Error playing music {music_name}: {str(e)}")
            else:
                print(f"Music file not found: {music_path}")
        else:
            print(f"Music not found: {music_name}")
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping music: {str(e)}")
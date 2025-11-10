import pygame
import os
from core import config

class AudioSystem:
    def __init__(self, game_config):
        self.config = game_config
        pygame.mixer.init()
        
        # Load sound effects
        self.sounds = {
            'bell': self._load_sound(config.SFX_DIR, "boxing-bell.mp3"),
            'ko': self._load_sound(config.SFX_DIR, "KO.mp3"),
            'weak_punch': self._load_sound(config.SFX_DIR, "weak-punch.mp3"),
            'strong_punch': self._load_sound(config.SFX_DIR, "strongpunch.mp3"),
            'meme_punch': self._load_sound(config.SFX_DIR, "punch-meme.mp3"),
            'round_1': self._load_sound(os.path.join(config.SFX_DIR, "round"), "round-1.mp3"),
            'round_2': self._load_sound(os.path.join(config.SFX_DIR, "round"), "round-2.mp3"),
            'round_3': self._load_sound(os.path.join(config.SFX_DIR, "round"), "round-3.mp3")
        }
        
        # Load background music
        self.music = {
            'menu': os.path.join(config.MUSIC_DIR, "menu_music.mp3"),
            'fight': os.path.join(config.MUSIC_DIR, "fight_music.mp3"),
            'ko': os.path.join(config.MUSIC_DIR, "ko_music.mp3")
        }
        
    def _load_sound(self, directory, filename):
        """Load sound with error handling"""
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        else:
            print(f"Warning: Sound file not found: {path}")
            return None
    
    def play_sound(self, sound_name, volume=1.0):
        """Play sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def play_music(self, music_name, volume=0.5, loops=-1):
        """Play background music"""
        if music_name in self.music and os.path.exists(self.music[music_name]):
            pygame.mixer.music.load(self.music[music_name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
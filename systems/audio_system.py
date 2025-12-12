"""Audio system - manages sound effects and background music."""

import pygame
import os

class AudioSystem:
    def __init__(self, game_config):
        self.config = game_config
        pygame.mixer.init()
        
        self.sounds = {
            'ko': self._load_sound("KO.wav"),
            'player-punch': self._load_sound("player-punch.wav"),
            'enemy-punch': self._load_sound("enemy-punch.wav"),
            'enemy-punch-bloked': self._load_sound("punch-blocked.wav"),
            'enemy-punch-missed': self._load_sound("enemy-punch-missed.wav"),
            'bell': self._load_sound("boxing-bell.wav"),
            'round_1': self._load_sound(os.path.join("round", "round_1.wav")),
            'round_2': self._load_sound(os.path.join("round", "round_2.wav")),
            'round_3': self._load_sound(os.path.join("round", "final_round.wav"))
        }
        
        self.music = {
            'menu': os.path.join(self.config.MUSIC_DIR, "menu_music.wav"),
            'fight': os.path.join(self.config.MUSIC_DIR, "fight_music.wav"),
            'ko': os.path.join(self.config.MUSIC_DIR, "ko_music.wav")
        }
    
    def _load_sound(self, filename):
        if isinstance(filename, tuple):
            path = os.path.join(self.config.SFX_DIR, *filename)
        else:
            path = os.path.join(self.config.SFX_DIR, filename)
        
        if not os.path.exists(path):
            print(f"Warning: Sound file not found: {path}")
            return None
            
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Warning: Failed to load sound {path}: {str(e)}")
            return None
    
    def play_sound(self, sound_name, volume=1.0):
        if sound_name not in self.sounds or not self.sounds[sound_name]:
            return
            
        self.sounds[sound_name].set_volume(volume)
        self.sounds[sound_name].play()
    
    def preload_music(self, music_name):
        """Preload music for faster playback (currently unused)"""
        pass
    
    def play_music(self, music_name, volume=0.5, loops=-1):
        if music_name not in self.music:
            return
            
        music_path = self.music[music_name]
        if not os.path.exists(music_path):
            print(f"Music file not found: {music_path}")
            return
            
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    
    def stop_music(self):
        pygame.mixer.music.stop()
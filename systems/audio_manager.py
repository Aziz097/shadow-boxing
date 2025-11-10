"""
Audio Manager
Handles all sound effects and music playback using pygame.mixer
"""
import pygame
import os
from typing import Dict, Optional
import config


class AudioManager:
    """Manages all game audio (sound effects and music)."""
    
    def __init__(self):
        """Initialize audio system."""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Volume settings (set BEFORE loading sounds)
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        # Sound effects dictionary
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Load all sounds
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all sound effects."""
        sound_files = {
            'round_1': config.SFX_ROUND_1,
            'round_2': config.SFX_ROUND_2,
            'round_3': config.SFX_ROUND_3,
            'boxing_bell': config.SFX_BOXING_BELL,
            'ko': config.SFX_KO,
            'weak_punch': config.SFX_WEAK_PUNCH,
            'strong_punch': config.SFX_STRONG_PUNCH,
            'meme_punch': config.SFX_MEME_PUNCH,
        }
        
        for name, filepath in sound_files.items():
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(self.sfx_volume)
                    print(f"Loaded sound: {name}")
                except Exception as e:
                    print(f"Failed to load {name}: {e}")
            else:
                print(f"Sound file not found: {filepath}")
    
    def play_sound(self, sound_name: str, loops: int = 0):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play
            loops: Number of times to loop (-1 for infinite, 0 for once)
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].play(loops=loops)
        else:
            print(f"Sound not found: {sound_name}")
    
    def stop_sound(self, sound_name: str):
        """
        Stop a specific sound.
        
        Args:
            sound_name: Name of the sound to stop
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
    def stop_all_sounds(self):
        """Stop all playing sounds."""
        pygame.mixer.stop()
    
    def play_round_sound(self, round_number: int):
        """
        Play round announcement sound.
        
        Args:
            round_number: Round number (1, 2, or 3)
        """
        sound_name = f'round_{round_number}'
        self.play_sound(sound_name)
    
    def play_punch_sound(self, combo_count: int = 1):
        """
        Play appropriate punch sound based on combo.
        
        Args:
            combo_count: Number of successful hits (1-4), default 1
        """
        # Stop previous punch sound to prevent overlap
        self.stop_sound('weak_punch')
        self.stop_sound('meme_punch')
        self.stop_sound('strong_punch')
        
        # Play new sound based on combo
        if combo_count >= 4:
            self.play_sound('strong_punch')
        elif combo_count in [2, 3]:
            self.play_sound('meme_punch')
        else:
            self.play_sound('weak_punch')
    
    def play_bell(self):
        """Play boxing bell sound."""
        self.play_sound('boxing_bell')
    
    def play_ko(self):
        """Play KO sound."""
        self.play_sound('ko')
    
    def set_sfx_volume(self, volume: float):
        """
        Set sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume: float):
        """
        Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def fade_out(self, duration_ms: int = 1000):
        """
        Fade out all audio.
        
        Args:
            duration_ms: Fade duration in milliseconds
        """
        pygame.mixer.fadeout(duration_ms)
    
    def cleanup(self):
        """Clean up audio resources."""
        pygame.mixer.quit()

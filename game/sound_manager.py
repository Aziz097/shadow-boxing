"""Sound Manager for Shadow Boxing Game."""
import os
from typing import Dict, Optional

import pygame


class SoundManager:
    """Manages game sound effects with volume control and playback."""
    
    CRITICAL_HP_THRESHOLD = 20
    
    SOUND_VOLUMES = {
        'punch': 0.7,
        'weak_punch': 0.7,
        'strong_punch': 1.0,
        'round': 0.9,
        'ko': 1.0,
        'hit': 0.8,
        'block': 0.6,
    }
    
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self._load_sounds()
        
    def _load_sounds(self) -> None:
        """Load all sound files from assets directory."""
        base_path = os.getcwd()
        
        sound_files = {
            'punch': os.path.join(base_path, 'assets', 'sfx', 'strongpunch.mp3'),
            'weak_punch': os.path.join(base_path, 'assets', 'sfx', 'weak-punch.mp3'),
            'strong_punch': os.path.join(base_path, 'assets', 'sfx', 'strongpunch.mp3'),
            'round_1': os.path.join(base_path, 'assets', 'sfx', 'round', 'round-1.mp3'),
            'round_2': os.path.join(base_path, 'assets', 'sfx', 'round', 'round-2.mp3'),
            'round_3': os.path.join(base_path, 'assets', 'sfx', 'round', 'round-3.mp3'),
            'ko': os.path.join(base_path, 'assets', 'sfx', 'KO.mp3'),
        }
        
        for name, full_path in sound_files.items():
            self._load_single_sound(name, full_path)
    
    def _load_single_sound(self, name: str, path: str) -> None:
        """Load a single sound file."""
        if not os.path.exists(path):
            print(f"✗ Sound file not found: {path}")
            return
            
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            print(f"✓ Loaded sound: {name}")
        except Exception as e:
            print(f"✗ Failed to load {name}: {e}")
    
    def play(self, sound_name: str, volume: Optional[float] = None) -> None:
        """Play a sound effect with optional volume override."""
        if not self.enabled or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        sound.set_volume(volume if volume is not None else 1.0)
        sound.play()
    
    def play_punch(self) -> None:
        """Play player punch sound."""
        self.play('punch', self.SOUND_VOLUMES['punch'])
    
    def play_round_start(self, round_number: int) -> None:
        """Play round announcement sound."""
        self.play(f'round_{round_number}', self.SOUND_VOLUMES['round'])
    
    def play_ko(self) -> None:
        """Play knockout sound."""
        self.play('ko', self.SOUND_VOLUMES['ko'])
    
    def play_enemy_hit(self, player_hp: float, critical: bool = False) -> None:
        """Play appropriate sound when enemy hits player."""
        is_critical = critical or player_hp <= self.CRITICAL_HP_THRESHOLD
        sound_key = 'strong_punch' if is_critical else 'weak_punch'
        volume = self.SOUND_VOLUMES[sound_key]
        self.play(sound_key, volume)
    
    def toggle_sound(self) -> bool:
        """Toggle sound on/off and return new state."""
        self.enabled = not self.enabled
        return self.enabled
    
    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        pygame.mixer.stop()

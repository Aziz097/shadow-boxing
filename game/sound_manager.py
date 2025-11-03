"""
Sound Manager untuk Shadow Boxing Game
Mengelola semua efek suara dalam game
"""
import pygame
import os

class SoundManager:
    """Manages all game sound effects"""
    
    def __init__(self):
        """Initialize pygame mixer and load sounds"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.enabled = True
        
        # Load existing sounds
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all sound files from assets/sfx"""
        sound_files = {
            'punch': 'assets/sfx/strongpunch.mp3',
            # Placeholder untuk sound lainnya - bisa ditambahkan nanti
            # 'hit': 'assets/sfx/hit.mp3',
            # 'block': 'assets/sfx/block.mp3',
            # 'round_bell': 'assets/sfx/bell.mp3',
        }
        
        for name, path in sound_files.items():
            full_path = os.path.join(os.path.dirname(__file__), '..', path)
            if os.path.exists(full_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(full_path)
                    print(f"✓ Loaded sound: {name}")
                except Exception as e:
                    print(f"✗ Failed to load {name}: {e}")
            else:
                print(f"✗ Sound file not found: {full_path}")
    
    def play(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if not self.enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def play_punch(self):
        """Play punch sound effect"""
        self.play('punch', volume=0.7)
    
    def play_hit(self):
        """Play hit sound effect"""
        self.play('hit', volume=0.8)
    
    def play_block(self):
        """Play block sound effect"""
        self.play('block', volume=0.6)
    
    def play_round_bell(self):
        """Play round bell sound"""
        self.play('round_bell', volume=0.9)
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def set_volume(self, volume):
        """Set master volume (0.0 - 1.0)"""
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def stop_all(self):
        """Stop all currently playing sounds"""
        pygame.mixer.stop()

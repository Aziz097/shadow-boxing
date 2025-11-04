"""
Enhanced Enemy AI untuk Shadow Boxing
Dengan telegraph system, difficulty levels, combo attacks, stamina, dan adaptive AI
"""
import random
import time
import numpy as np

class EnemyAI:
    """
    Enhanced Enemy AI dengan fitur:
    - Telegraph/Warning system
    - Difficulty levels (EASY, MEDIUM, HARD)
    - Combo attacks
    - Stamina system
    - Vulnerability windows
    - Adaptive learning
    """
    
    def __init__(self, difficulty="MEDIUM"):
        """
        Initialize Enemy AI
        
        Args:
            difficulty: "EASY", "MEDIUM", or "HARD"
        """
        self.difficulty = difficulty
        self.state = "IDLE"
        self.last_action_time = 0
        
        # Attack properties
        self.attack_target = None
        self.attack_type = None
        self.attack_start_time = 0
        
        # Telegraph system
        self.telegraph_start_time = 0
        
        # Combo system
        self.combo_count = 0
        self.max_combo = 0
        self.in_combo = False
        self.combo_delay = 0.2  # delay between combo hits
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen_rate = 10  # per second
        self.attack_stamina_cost = 20
        
        # Vulnerability
        self.vulnerable = False
        self.vulnerability_start_time = 0
        
        # Adaptive AI tracking
        self.player_defense_pattern = 0  # how often player defends
        self.player_aggression = 0  # how aggressive player is
        self.feint_chance = 0.1
        
        # Difficulty-based parameters
        self._set_difficulty_params()
        
    def _set_difficulty_params(self):
        """Set parameters based on difficulty level"""
        if self.difficulty == "EASY":
            self.attack_duration = 0.6  # slower
            self.recover_duration = 1.0  # longer recovery
            self.telegraph_duration = 0.8  # longer warning
            self.idle_time_range = (2.0, 3.5)  # less aggressive
            self.combo_chance = 0.1  # 10% combo
            self.vulnerability_duration = 2.0  # INCREASED: more time to counter
            
        elif self.difficulty == "HARD":
            self.attack_duration = 0.25  # fast!
            self.recover_duration = 0.4  # quick recovery
            self.telegraph_duration = 0.3  # short warning
            self.idle_time_range = (0.6, 1.2)  # very aggressive
            self.combo_chance = 0.4  # 40% combo
            self.vulnerability_duration = 0.8  # INCREASED: harder but fair
            
        else:  # MEDIUM (default)
            self.attack_duration = 0.4
            self.recover_duration = 0.6
            self.telegraph_duration = 0.5
            self.idle_time_range = (1.0, 2.0)  # more aggressive for 60s rounds
            self.combo_chance = 0.25  # 25% combo
            self.vulnerability_duration = 1.5  # INCREASED: more time to counter punch
    
    def get_attack_type(self):
        """Determine attack type"""
        return random.choice(["CENTER", "LEFT", "RIGHT"])
    
    def decide_combo(self):
        """Decide if this will be a combo attack"""
        if random.random() < self.combo_chance and self.stamina >= self.attack_stamina_cost * 2:
            self.in_combo = True
            self.max_combo = random.choice([2, 3])
            self.combo_count = 0
            return True
        return False
    
    def can_attack(self):
        """Check if enemy has enough stamina to attack"""
        return self.stamina >= self.attack_stamina_cost
    
    def adapt_to_player(self, game_state):
        """
        Adapt strategy based on player behavior
        
        Args:
            game_state: GameState object to analyze player patterns
        """
        # Track player patterns
        total_actions = game_state.player_attack_count + game_state.player_defense_count
        
        if total_actions > 10:
            # Calculate player defense rate
            defense_rate = game_state.player_defense_count / total_actions
            
            # If player defends a lot, increase feint chance
            if defense_rate > 0.6:
                self.feint_chance = 0.3
                # Also attack faster to pressure
                idle_min, idle_max = self.idle_time_range
                self.idle_time_range = (idle_min * 0.8, idle_max * 0.8)
            
            # If player is aggressive, be more defensive
            elif defense_rate < 0.3:
                self.feint_chance = 0.1
                # Counter-attack strategy
                self.vulnerability_duration *= 0.8  # shorter vulnerable window
    
    def update(self, current_time, w, h, face_bbox=None, pose_landmarks=None, game_state=None):
        """
        Update enemy state
        
        Args:
            current_time: Current timestamp
            w, h: Frame dimensions
            face_bbox: Face bounding box (x1, y1, x2, y2)
            pose_landmarks: MediaPipe pose landmarks
            game_state: GameState object for adaptive AI
        """
        # Update stamina
        delta_time = current_time - self.last_action_time
        if self.state == "IDLE" or self.state == "RECOVERING":
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * delta_time)
        
        # Adapt strategy
        if game_state:
            self.adapt_to_player(game_state)
        
        # State machine
        if self.state == "IDLE":
            idle_duration = random.uniform(*self.idle_time_range)
            
            if current_time - self.last_action_time > idle_duration and self.can_attack():
                # Check for feint
                if random.random() < self.feint_chance:
                    # Feint attack (telegraph but don't follow through)
                    self.state = "TELEGRAPH"
                    self.telegraph_start_time = current_time
                    self.attack_type = self.get_attack_type()
                    # Will return to IDLE instead of ATTACKING
                else:
                    # Real attack
                    self.state = "TELEGRAPH"
                    self.telegraph_start_time = current_time
                    self.attack_type = self.get_attack_type()
                    self.decide_combo()
                    
                    # Determine target
                    if face_bbox:
                        self.attack_target = self._target_from_face(face_bbox, self.attack_type, w, h)
                    elif pose_landmarks:
                        self.attack_target = self._target_from_pose(pose_landmarks, self.attack_type, w, h)
                    else:
                        self.attack_target = (w // 2, h // 3)
        
        elif self.state == "TELEGRAPH":
            if current_time - self.telegraph_start_time > self.telegraph_duration:
                # Feint check
                if random.random() < 0.15:  # 15% chance to feint after telegraph
                    self.state = "IDLE"
                    self.last_action_time = current_time
                else:
                    self.state = "ATTACKING"
                    self.attack_start_time = current_time
                    # Consume stamina
                    self.stamina -= self.attack_stamina_cost
        
        elif self.state == "ATTACKING":
            if current_time - self.attack_start_time > self.attack_duration:
                # Check if in combo
                if self.in_combo and self.combo_count < self.max_combo - 1:
                    self.combo_count += 1
                    # Next combo hit
                    self.state = "COMBO_DELAY"
                    self.last_action_time = current_time
                    # New target for next hit
                    self.attack_type = self.get_attack_type()
                    if face_bbox:
                        self.attack_target = self._target_from_face(face_bbox, self.attack_type, w, h)
                    elif pose_landmarks:
                        self.attack_target = self._target_from_pose(pose_landmarks, self.attack_type, w, h)
                else:
                    # End of attack/combo
                    self.in_combo = False
                    self.combo_count = 0
                    self.state = "RECOVERING"
                    self.last_action_time = current_time
                    self.vulnerable = True
                    self.vulnerability_start_time = current_time
                    print(f">>> ENEMY NOW VULNERABLE! Duration: {self.vulnerability_duration}s")  # DEBUG
        
        elif self.state == "COMBO_DELAY":
            if current_time - self.last_action_time > self.combo_delay:
                self.state = "ATTACKING"
                self.attack_start_time = current_time
                self.stamina -= self.attack_stamina_cost * 0.5  # combo hits cost less
        
        elif self.state == "RECOVERING":
            if current_time - self.last_action_time > self.recover_duration:
                self.state = "IDLE"
                self.vulnerable = False
                print(">>> Enemy recovered - no longer vulnerable")  # DEBUG
            
            # Update vulnerability
            if self.vulnerable and current_time - self.vulnerability_start_time > self.vulnerability_duration:
                self.vulnerable = False
                print(">>> Vulnerability window closed")  # DEBUG
    
    def _target_from_face(self, face_bbox, atk_type, w, h):
        """Calculate target position from face bbox"""
        x1, y1, x2, y2 = face_bbox
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        fw = x2 - x1
        
        if atk_type == "LEFT":
            return (int(x1 + fw * 0.25), cy)
        elif atk_type == "RIGHT":
            return (int(x2 - fw * 0.25), cy)
        else:  # CENTER
            return (cx, cy)
    
    def _target_from_pose(self, pose_landmarks, atk_type, w, h):
        """Calculate target position from pose landmarks"""
        if atk_type == "LEFT":
            lm = pose_landmarks.landmark[2]  # left eye
        elif atk_type == "RIGHT":
            lm = pose_landmarks.landmark[5]  # right eye
        else:
            lm = pose_landmarks.landmark[0]  # nose
        
        if lm.visibility > 0.5:
            return (int(lm.x * w), int(lm.y * h))
        else:
            return (w // 2, h // 3)
    
    def get_hand_position(self, current_time):
        """Get current position of enemy's attacking hand"""
        if self.state == "ATTACKING" and self.attack_target:
            progress = min(1.0, (current_time - self.attack_start_time) / self.attack_duration)
            
            # Easing function for more natural movement
            progress = self._ease_in_out(progress)
            
            # Start from bottom of screen
            start_y = 720  # assume 720p
            if self.attack_target:
                tx, ty = self.attack_target
                x = tx
                y = start_y + (ty - start_y) * progress
                return (int(x), int(y))
        
        return None
    
    def _ease_in_out(self, t):
        """Easing function for smoother animation"""
        return t * t * (3.0 - 2.0 * t)
    
    def is_attacking(self):
        """Check if currently in attacking state"""
        return self.state == "ATTACKING"
    
    def is_telegraphing(self):
        """Check if currently showing telegraph warning"""
        return self.state == "TELEGRAPH"
    
    def is_vulnerable(self):
        """Check if currently vulnerable to counter-attack"""
        return self.vulnerable
    
    def is_idle(self):
        """Check if idle"""
        return self.state == "IDLE"
    
    def get_stamina_percentage(self):
        """Get stamina as percentage"""
        return (self.stamina / self.max_stamina) * 100
    
    def take_damage(self):
        """Enemy takes damage (interrupts attack if vulnerable)"""
        if self.vulnerable:
            # Counter hit! Reset to recovering
            self.state = "RECOVERING"
            self.last_action_time = time.time()
            self.vulnerable = False
            self.in_combo = False
            return True  # successful counter
        return False

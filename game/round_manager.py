"""
Round Manager untuk Shadow Boxing
Mengelola sistem ronde (3 ronde x 20 detik) dengan rest period
"""
import time

class RoundManager:
    """Manages rounds, timing, and rest periods"""
    
    def __init__(self, total_rounds=3, round_duration=20, rest_duration=5):
        """
        Initialize Round Manager
        
        Args:
            total_rounds: Total number of rounds (default: 3)
            round_duration: Duration of each round in seconds (default: 20)
            rest_duration: Rest time between rounds in seconds (default: 5)
        """
        self.total_rounds = total_rounds
        self.round_duration = round_duration
        self.rest_duration = rest_duration
        
        # Current state
        self.current_round = 1
        self.state = "READY"  # READY, FIGHTING, REST, FINISHED
        self.round_start_time = 0
        self.rest_start_time = 0
        
        # Round scores
        self.round_winners = []  # Track winner of each round
        self.player_round_wins = 0
        self.enemy_round_wins = 0
        
    def start_round(self):
        """Start a new round"""
        if self.state == "READY" or self.state == "REST":
            self.state = "FIGHTING"
            self.round_start_time = time.time()
            return True
        return False
    
    def update(self, current_time):
        """Update round state based on current time"""
        if self.state == "FIGHTING":
            elapsed = current_time - self.round_start_time
            
            if elapsed >= self.round_duration:
                # Round time up
                if self.current_round < self.total_rounds:
                    self.state = "REST"
                    self.rest_start_time = current_time
                else:
                    self.state = "FINISHED"
                    
        elif self.state == "REST":
            elapsed = current_time - self.rest_start_time
            
            if elapsed >= self.rest_duration:
                # Rest period over, prepare next round
                self.current_round += 1
                self.state = "READY"
    
    def get_remaining_time(self, current_time):
        """Get remaining time in current round"""
        if self.state == "FIGHTING":
            elapsed = current_time - self.round_start_time
            remaining = self.round_duration - elapsed
            return max(0, remaining)
        return 0
    
    def get_rest_remaining(self, current_time):
        """Get remaining rest time"""
        if self.state == "REST":
            elapsed = current_time - self.rest_start_time
            remaining = self.rest_duration - elapsed
            return max(0, remaining)
        return 0
    
    def end_round(self, winner):
        """
        End current round and record winner
        
        Args:
            winner: 'PLAYER', 'ENEMY', or 'DRAW'
        """
        self.round_winners.append(winner)
        
        if winner == "PLAYER":
            self.player_round_wins += 1
        elif winner == "ENEMY":
            self.enemy_round_wins += 1
        
        # Transition to rest or finish
        if self.current_round < self.total_rounds:
            self.state = "REST"
            self.rest_start_time = time.time()
        else:
            self.state = "FINISHED"
    
    def get_round_winner(self, player_score, enemy_score):
        """
        Determine round winner based on scores
        
        Args:
            player_score: Player's score for the round
            enemy_score: Enemy's score for the round
            
        Returns:
            'PLAYER', 'ENEMY', or 'DRAW'
        """
        if player_score > enemy_score:
            return "PLAYER"
        elif enemy_score > player_score:
            return "ENEMY"
        else:
            return "DRAW"
    
    def get_match_winner(self):
        """Get overall match winner"""
        if self.state != "FINISHED":
            return None
            
        if self.player_round_wins > self.enemy_round_wins:
            return "PLAYER"
        elif self.enemy_round_wins > self.player_round_wins:
            return "ENEMY"
        else:
            return "DRAW"
    
    def is_fighting(self):
        """Check if currently in fighting state"""
        return self.state == "FIGHTING"
    
    def is_resting(self):
        """Check if in rest period"""
        return self.state == "REST"
    
    def is_finished(self):
        """Check if match is finished"""
        return self.state == "FINISHED"
    
    def is_ready(self):
        """Check if ready to start (new round)"""
        return self.state == "READY"
    
    def get_status_text(self, current_time):
        """Get current status as text for display"""
        if self.state == "READY":
            return f"Round {self.current_round} - Press SPACE to start"
        elif self.state == "FIGHTING":
            remaining = int(self.get_remaining_time(current_time))
            return f"Round {self.current_round}/{self.total_rounds} - {remaining}s"
        elif self.state == "REST":
            remaining = int(self.get_rest_remaining(current_time))
            return f"REST - {remaining}s"
        elif self.state == "FINISHED":
            winner = self.get_match_winner()
            return f"Match Over - Winner: {winner}"
        return ""
    
    def reset(self):
        """Reset for new match"""
        self.current_round = 1
        self.state = "READY"
        self.round_start_time = 0
        self.rest_start_time = 0
        self.round_winners = []
        self.player_round_wins = 0
        self.enemy_round_wins = 0

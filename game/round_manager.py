"""Round Manager for Shadow Boxing game."""
import time
from typing import Literal, Optional


RoundState = Literal["READY", "FIGHTING", "REST", "FINISHED"]
Winner = Literal["PLAYER", "ENEMY", "DRAW"]


class RoundManager:
    """Manages boxing match rounds, timing, and scoring."""
    
    def __init__(self, total_rounds: int = 3, round_duration: int = 20, rest_duration: int = 10):
        self.total_rounds = total_rounds
        self.round_duration = round_duration
        self.rest_duration = rest_duration
        
        self.current_round = 1
        self.state: RoundState = "READY"
        self.round_start_time = 0.0
        self.rest_start_time = 0.0
        
        self.round_winners: list[Winner] = []
        self.player_round_wins = 0
        self.enemy_round_wins = 0
        
    def start_round(self) -> bool:
        """Start a new round if ready or resting."""
        if self.state in ("READY", "REST"):
            self.state = "FIGHTING"
            self.round_start_time = time.time()
            return True
        return False
    
    def update(self, current_time: float) -> None:
        """Update round state based on elapsed time."""
        if self.state == "FIGHTING":
            self._update_fighting_state(current_time)
        elif self.state == "REST":
            self._update_rest_state(current_time)
    
    def _update_fighting_state(self, current_time: float) -> None:
        """Handle fighting state time expiry."""
        elapsed = current_time - self.round_start_time
        if elapsed >= self.round_duration:
            if self.current_round < self.total_rounds:
                self.state = "REST"
                self.rest_start_time = current_time
            else:
                self.state = "FINISHED"
    
    def _update_rest_state(self, current_time: float) -> None:
        """Handle rest period and auto-start next round."""
        elapsed = current_time - self.rest_start_time
        if elapsed >= self.rest_duration:
            self.current_round += 1
            self.state = "FIGHTING"
            self.round_start_time = current_time
            print(f"Round {self.current_round} START!")
    
    def get_remaining_time(self, current_time: float) -> float:
        """Get remaining time in current round."""
        if self.state == "FIGHTING":
            elapsed = current_time - self.round_start_time
            return max(0, self.round_duration - elapsed)
        return 0.0
    
    def get_rest_remaining(self, current_time: float) -> float:
        """Get remaining rest time."""
        if self.state == "REST":
            elapsed = current_time - self.rest_start_time
            return max(0, self.rest_duration - elapsed)
        return 0.0
    
    def end_round(self, winner: Winner, force_finish: bool = False) -> None:
        """End current round and record winner."""
        self.round_winners.append(winner)
        
        if winner == "PLAYER":
            self.player_round_wins += 1
        elif winner == "ENEMY":
            self.enemy_round_wins += 1
        
        if force_finish:
            self.state = "FINISHED"
        elif self.current_round < self.total_rounds:
            self.state = "REST"
            self.rest_start_time = time.time()
        else:
            self.state = "FINISHED"
    
    def get_round_winner(self, player_score: int, enemy_score: int) -> Winner:
        """Determine round winner based on scores."""
        if player_score > enemy_score:
            return "PLAYER"
        elif enemy_score > player_score:
            return "ENEMY"
        return "DRAW"
    
    def get_match_winner(self) -> Optional[Winner]:
        """Get overall match winner."""
        if self.state != "FINISHED":
            return None
            
        if self.player_round_wins > self.enemy_round_wins:
            return "PLAYER"
        elif self.enemy_round_wins > self.player_round_wins:
            return "ENEMY"
        return "DRAW"
    
    def is_fighting(self) -> bool:
        return self.state == "FIGHTING"
    
    def is_resting(self) -> bool:
        return self.state == "REST"
    
    def is_finished(self) -> bool:
        return self.state == "FINISHED"
    
    def is_ready(self) -> bool:
        return self.state == "READY"
    
    def reset(self) -> None:
        """Reset for new match."""
        self.current_round = 1
        self.state = "READY"
        self.round_start_time = 0.0
        self.rest_start_time = 0.0
        self.round_winners = []
        self.player_round_wins = 0
        self.enemy_round_wins = 0

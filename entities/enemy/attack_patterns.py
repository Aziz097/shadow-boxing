import random
from core import constants

class AttackPatterns:
    @staticmethod
    def get_pattern(round_num):
        """Get attack pattern based on round number"""
        if round_num == 1:
            return AttackPatterns.round_1_pattern()
        elif round_num == 2:
            return AttackPatterns.round_2_pattern()
        else:
            return AttackPatterns.round_3_pattern()
    
    @staticmethod
    def round_1_pattern():
        """Simple attack pattern for round 1"""
        return [
            {"type": "single", "delay": 2.0},
            {"type": "single", "delay": 3.0},
            {"type": "combo", "count": 2, "delay_between": 0.8, "delay_after": 2.0}
        ]
    
    @staticmethod
    def round_2_pattern():
        """Medium difficulty pattern for round 2"""
        return [
            {"type": "combo", "count": 2, "delay_between": 0.7, "delay_after": 1.5},
            {"type": "single", "delay": 1.0},
            {"type": "combo", "count": 3, "delay_between": 0.6, "delay_after": 2.0},
            {"type": "feint", "delay": 1.0}
        ]
    
    @staticmethod
    def round_3_pattern():
        """Hard pattern for round 3"""
        return [
            {"type": "combo", "count": 3, "delay_between": 0.5, "delay_after": 1.0},
            {"type": "feint", "delay": 0.8},
            {"type": "combo", "count": 4, "delay_between": 0.4, "delay_after": 1.5},
            {"type": "rapid", "count": 2, "delay_between": 0.3, "delay_after": 2.0}
        ]
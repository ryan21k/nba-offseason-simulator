import pandas as pd
import numpy as np

class DraftPick:
    def __init__(self):
        self.PICK_VALUE = 1
        self.DECAY_RATE = 0
    
    def get_pick_val(self, pick_num):
        if pick_num < 1 or pick_num > 60:
            raise ValueError("Pick number must be between 1 and 60.")
        return float(self.PICK_VALUE * np.exp(-self.DECAY_RATE * (pick_num - 1)))
    
    def determine_implied_val(self, strength_sending, years_out, protection = "none"):
        curr_strength = max(0.4, min(1.3, strength_sending))

        #inverse linear normalization to determine projected slot based on team strength
        projected_slot = ((curr_strength - 0.4) / (1.3 - 0.4)) * 29 + 1 #x = x_norm * (x_max - x_min) + x_min, x_max = 30, x_min = 1

        regressed_slot = projected_slot + (15.5 - projected_slot) * (1 - (0.85 ** years_out)) #regression to the mean of (1 + 30)/2 = 15.5 over time, with a decay factor of 0.85
        base_value = self.get_pick_val(int(np.clip(regressed_slot, 1, 30)))

        if protection == "top3":
            protection_factor = 0.85
        elif protection == "top10":
            protection_factor = 0.7
        elif protection == "lottery":
            protection_factor = 0.5
        else:
            protection_factor = 1
        
        return base_value * protection_factor
    

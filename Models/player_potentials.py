from pathlib import Path
import pandas as pd
import numpy as np

class PlayerPotential:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.df = None

    def load_dataset(self):
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Player potential data not found at {self.dataset_path}. Please run player_potential_dataset.py first.")
        self.df = pd.read_csv(self.dataset_path)

    def experience_trajectory(self, experience):
        if experience <= 2: #experience the most growth during rookie season/early years
            growth_rate = 1.5 - (experience * 0.075) #50% growth during rookie season, 7.5% decay per year after
        elif experience <= 6: #growth plateaus during prime development years
            growth_rate = 1.0
        else: #growth decays during late years of players' career but not below 0.5 in case of late explosions
            growth_rate = max(0.5, 1.0 - (0.05 * (experience - 6)))
        
        return growth_rate
    
    def potential_evaluation(self, output_path):
        self.load_dataset()

        #calculate potential impact based on years of experience and current player impact
        self.df['GROWTH_MULTIPLIER'] = self.df['YEARS_OF_EXPERIENCE'].apply(self.experience_trajectory)
        self.df['POTENTIAL_IMPACT'] = self.df['GROWTH_MULTIPLIER'] * self.df['PLAYER_IMPACT']

        impact_change = self.df['POTENTIAL_IMPACT'] - self.df['PLAYER_IMPACT'] #difference in impact scores
        star_shield = np.where(self.df['PLAYER_IMPACT'] > 0.35, abs(impact_change) * 0.65, 0.0) #protects stars w/ impact scores > 0.35 and calculates 65% of the loss to add to player

        self.df['ASSET_VALUE'] = (impact_change + star_shield + self.df['YEARS_REMAINING_ON_CONTRACT'] * 0.005)

        self.df = self.df.sort_values(by = 'ASSET_VALUE', ascending = False)
        self.df.to_csv(output_path, index=False)
        return self.df

if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent

    potentials = (
        ROOT_DIR
        / "Data"
        / "Processed Data"
        / "player_potentials.csv"
    )

    player_potential = PlayerPotential(potentials)
    output_path = (
        ROOT_DIR 
        / "Data" 
        / "Processed Data" 
        / "player_potential_evaluation.csv"
    )
    results = player_potential.potential_evaluation(output_path)

    print("\n--- TOP 5 HIGHEST FUTURE ASSET VALUES ---")
    print(results[['PLAYER_NAME', 'YEARS_OF_EXPERIENCE', 'YEARS_REMAINING_ON_CONTRACT', 'PLAYER_IMPACT', 'ASSET_VALUE']].head(5))

    print("\n--- BOTTOM 5 DECAYING/EXPIRING ASSETS ---")
    print(results[['PLAYER_NAME', 'YEARS_OF_EXPERIENCE', 'YEARS_REMAINING_ON_CONTRACT', 'PLAYER_IMPACT', 'ASSET_VALUE']].tail(5))
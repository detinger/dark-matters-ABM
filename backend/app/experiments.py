from __future__ import annotations

from pathlib import Path

import pandas as pd
from mesa.batchrunner import batch_run

from app.simulation.model import DarkPatternTrustModel


def run_experiments(output_path: str = "batch_results.csv") -> pd.DataFrame:
    params = {
        "num_users": [500],
        "network_type": ["small_world"],
        "avg_degree": [8],
        "rewire_prob": [0.08],
        "max_steps": [104],
        "dark_pattern_intensity": [0.0, 0.2, 0.4, 0.6, 0.8],
        "pattern_forced_trial": [True],
        "pattern_hard_cancel": [True],
        "pattern_drip_pricing": [True],
        "adaptive_platform": [False, True],
        "customer_support_quality": [0.2, 0.5],
        "social_influence_strength": [0.10, 0.18, 0.30],
        "review_visibility": [0.20, 0.35, 0.50],
    }
    results = batch_run(
        DarkPatternTrustModel,
        parameters=params,
        iterations=10,
        max_steps=104,
        number_processes=1,
        data_collection_period=1,
        display_progress=True,
    )
    df = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    df = run_experiments("results/batch_results.csv")
    print(df.head())

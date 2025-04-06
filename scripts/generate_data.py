#!/usr/bin/env python

""" Generating and preparing panel data. """

import pandas as pd
import numpy as np
import random
from faker import Faker

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker('en_US')

# Scenario inputs
YEARS = list(range(2000, 2026))
MIN_HOURS = 1000
MAX_HOURS = 500000
NUM_CLIENTS = 99


def generate_realistic_client_names(num_clients):
    names = list({fake.company() for _ in range(num_clients * 2)})[:num_clients]
    client_ids = [f"Client_{i+1}" for i in range(num_clients)]
    return dict(zip(client_ids, names))


def generate_operational_years():
    """Generates 1–3 active periods with consecutive years for each client."""
    total_periods = random.randint(1, 3)
    years_active = set()
    while len(years_active) < 1:
        years_active.clear()
        for _ in range(total_periods):
            start = random.randint(2000, 2024)
            length = random.randint(1, 12)
            for y in range(start, min(start + length, 2026)):
                years_active.add(y)
    return sorted(years_active)


def create_panel_data(client_name_map):
    records = []

    for client_key, client_name in client_name_map.items():
        operational_years = generate_operational_years()

        for year in operational_years:
            hours = np.random.randint(MIN_HOURS, MAX_HOURS)

            # Gross calculation with heteroscedasticity
            base_gross = hours * np.random.uniform(80, 120)
            base_gross += len(operational_years) * np.random.uniform(500, 10000)
            noise_std = 0.05 + (hours / MAX_HOURS) * 0.15
            noise = np.random.normal(0, base_gross * noise_std)
            gross = round(base_gross + noise, 2)

            records.append({
                "Client Name": client_name,
                "Year": year,
                "Billable_Hours": hours,
                "Gross": gross
            })

    return pd.DataFrame(records)


def main():
    client_name_map = generate_realistic_client_names(NUM_CLIENTS)
    panel_df = create_panel_data(client_name_map)
    panel_df.to_csv("../data/panel_data.csv", index=False)
    return panel_df


if __name__ == "__main__":
    panel_df = main()
    print("Panel Data Sample:\n", panel_df.head())










__author__ = "Ednalyn C. De Dios, et al."
__copyright__ = "Copyright 2025, Cumulative Seasonality"
__credits__ = []
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ednalyn C. De Dios"
__email__ = "ednalyn.dedios@gmail.com"
__status__ = "Prototype"
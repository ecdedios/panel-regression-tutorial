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
NUM_RECORDS = 1200

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

def create_panel_data(client_name_map, num_records=NUM_RECORDS):
    billable_data = []
    gross_data = []

    client_keys = list(client_name_map.keys())

    for _ in range(num_records):
        client_key = random.choice(client_keys)
        client_name = client_name_map[client_key]
        operational_years = generate_operational_years()
        total_operational = len(operational_years)

        billable_row = {"Client Name": client_name}
        gross_row = {"Client Name": client_name}

        for year in YEARS:
            if year in operational_years:
                hours = np.random.randint(MIN_HOURS, MAX_HOURS)
                billable_row[year] = hours

                # Gross calculation with heteroscedasticity
                base_gross = hours * np.random.uniform(80, 120)
                base_gross += total_operational * np.random.uniform(500, 10000)
                noise_std = 0.05 + (hours / MAX_HOURS) * 0.15
                noise = np.random.normal(0, base_gross * noise_std)
                gross_row[year] = round(base_gross + noise, 2)
            else:
                billable_row[year] = None
                gross_row[year] = None

        billable_data.append(billable_row)
        gross_data.append(gross_row)

    return pd.DataFrame(billable_data), pd.DataFrame(gross_data)

def transform_to_long_format(df, value_name):
    return df.melt(
        id_vars="Client Name",
        value_vars=[year for year in YEARS],
        var_name="Year",
        value_name=value_name
    ).dropna(subset=[value_name])

def main():
    client_name_map = generate_realistic_client_names(NUM_CLIENTS)
    billable_df, gross_df = create_panel_data(client_name_map, NUM_RECORDS)

    billable_long = transform_to_long_format(billable_df, "Billable_Hours")
    gross_long = transform_to_long_format(gross_df, "Gross")

    # Merge for full panel if needed
    full_panel = pd.merge(billable_long, gross_long, on=["Client Name", "Year"], how="inner")

    # Optional: Save files
    # billable_df.to_csv("billable_wide.csv", index=False)
    # gross_df.to_csv("gross_wide.csv", index=False)
    # billable_long.to_csv("billable_long.csv", index=False)
    # gross_long.to_csv("gross_long.csv", index=False)
    full_panel.to_csv("../data/panel_data.csv", index=False)

    return billable_df, gross_df, billable_long, gross_long, full_panel

# Run main if script is executed directly
if __name__ == "__main__":
    billable_df, gross_df, billable_long, gross_long, full_panel = main()
    print("Billable Hours (Long Format):\n", billable_long.head())
    print("\nGross (Long Format):\n", gross_long.head())
    print("\nMerged Panel Data:\n", full_panel.head())









__author__ = "Ednalyn C. De Dios, et al."
__copyright__ = "Copyright 2025, Cumulative Seasonality"
__credits__ = []
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ednalyn C. De Dios"
__email__ = "ednalyn.dedios@gmail.com"
__status__ = "Prototype"
import pandas as pd
import numpy as np
from faker import Faker

np.random.seed(493)

# Configuration
num_clients = 120
years = list(range(2000, 2026))
records = []

# Initialize Faker
faker = Faker()
Faker.seed(493)  # Ensure reproducibility

# Generate realistic client names
clients = [faker.company() for _ in range(num_clients)]

# Ensure uniqueness
clients = list(pd.Series(clients).drop_duplicates().values)
while len(clients) < num_clients:
    new_names = [faker.company() for _ in range(num_clients - len(clients))]
    clients += list(pd.Series(new_names).drop_duplicates().values)
clients = clients[:num_clients]  # Final trimmed list

client_quality = {client: np.random.normal(0, 1) for client in clients}
econ_shocks = {year: np.random.normal(0, 1.5) for year in years}

def generate_contract_years():
    total_years = np.random.randint(1, 13)
    contract_years = []
    remaining = total_years
    while remaining > 0:
        segment_length = np.random.randint(1, min(6, remaining + 1))
        start = np.random.choice([y for y in years if y + segment_length <= 2026])
        contract_years.extend(range(start, start + segment_length))
        remaining -= segment_length
    return sorted(set(contract_years))

# Build panel data
for client in clients:
    contract_years = generate_contract_years()
    quality = client_quality[client]
    for i, year in enumerate(contract_years):
        sales = np.random.randint(50_000, 1_000_001)
        years_active = i + 1

        # Revenue with decreased reliance on sales and increased effect of years_active
        base_revenue = (
            50_000 +                              # baseline
            15 * sales +                          # lower weight on sales
            250_000 * np.log1p(years_active) +    # stronger effect of years_active
            250_000 * quality +                   # still present but lower
            400_000 * econ_shocks[year]           # economic noise
        )

        noise = np.random.normal(0, 2.0 * np.sqrt(sales))  # even more noise
        revenue = np.clip(base_revenue + noise, 50_000, 10_000_000)

        records.append({
            'client': client,
            'year': year,
            'sales': sales,
            'revenue': revenue,
            'years_active': years_active
        })

df = pd.DataFrame(records)

# Add contract stats
contract_info = (
    df.groupby('client')['year']
    .agg(number_years_in_contract='nunique', min_year='min', max_year='max')
    .reset_index()
)
df = df.merge(contract_info[['client', 'number_years_in_contract']], on='client')

# Final cleaned version
df = df[['client', 'year', 'sales', 'revenue', 'years_active', 'number_years_in_contract']]

# df.to_csv('data.csv', index=False)

# Pivot for sales
df_sales_wide = df.pivot(index='client', columns='year', values='sales')

# Pivot for revenue
df_revenue_wide = df.pivot(index='client', columns='year', values='revenue')

# # Optional: rename columns for clarity (e.g., prefix with 'sales_' or 'rev_')
# df_sales_wide.columns = [f"sales_{col}" for col in df_sales_wide.columns]
# df_revenue_wide.columns = [f"rev_{col}" for col in df_revenue_wide.columns]

# Reset index if needed
df_sales_wide = df_sales_wide.reset_index()
df_revenue_wide = df_revenue_wide.reset_index()

df_sales_wide.to_csv('sales.csv', index=False)
df_revenue_wide.to_csv('revenue.csv', index=False)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed()

# Generate dates for 2 years
start_date = datetime(2019, 8, 19)
end_date = datetime(2024, 9, 15)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Initialize data with zeros
n_days = len(date_range)
data = {
    'DATE': date_range,
    'HOT_TEMP': np.zeros(n_days, dtype=int),
    'COLD_TEMP': np.zeros(n_days, dtype=int),
    'CO2': np.zeros(n_days, dtype=int),
    'WATCH_HOURS': np.zeros(n_days, dtype=int),
    'SI': np.zeros(n_days, dtype=int),
    'COKE': np.zeros(n_days, dtype=int),
    'MN': np.zeros(n_days, dtype=int)
}

# Create DataFrame
df = pd.DataFrame(data)

# Function to generate growth
def generate_growth(start, end, days):
    return np.linspace(start, end, days)

# Generate growth patterns
hot_temp = generate_growth(1, 200, n_days)
cold_temp = generate_growth(0, 50, n_days)
co2 = generate_growth(10, 10000, n_days)
watch_hours = generate_growth(1, 1000, n_days)
si = generate_growth(0, 500, n_days)
coke = generate_growth(0, 100, n_days)
mn = generate_growth(0, 50, n_days)

# Add randomness and ensure integer values
for i, col in enumerate(['HOT_TEMP', 'COLD_TEMP', 'CO2', 'WATCH_HOURS', 'SI', 'COKE', 'MN']):
    random_factor = np.random.normal(1, 0.1, n_days)  # Mean of 1, standard deviation of 0.1
    df[col] = np.maximum(0, (eval(col.lower()) * random_factor).astype(int))

# Weekend boost
weekend_mask = (df['DATE'].dt.dayofweek >= 5)
df.loc[weekend_mask, ['CO2', 'WATCH_HOURS', 'SI']] = df.loc[weekend_mask, ['CO2', 'WATCH_HOURS', 'SI']] * 1.5

# Seasonal variation (higher in summer)
days_in_year = 366  # Account for leap year
summer_boost = np.sin(np.linspace(0, 2*np.pi, days_in_year))
df['CO2'] = df['CO2'] * (1 + 0.2 * summer_boost[df['DATE'].dt.dayofyear - 1])

# Occasional viral videos (once every 2 months on average, starting from the second month)
viral_days = np.random.choice(range(30, n_days), size=11, replace=False)
df.loc[viral_days, ['CO2', 'SI', 'COKE', 'MN']] = df.loc[viral_days, ['CO2', 'SI', 'COKE', 'MN']] * 5

# Ensure integer values
for col in df.columns:
    if col != 'DATE':
        df[col] = df[col].astype(int)

# Calculate cumulative DIFF_TEMP
df['DIFF_TEMP'] = (df['HOT_TEMP'] - df['COLD_TEMP']).cumsum()

# Ensure no negative values
df[df.select_dtypes(include=[np.number]).columns] = df.select_dtypes(include=[np.number]).clip(lower=0)

# Save to CSV
df.to_csv('steel_data.csv', index=False)
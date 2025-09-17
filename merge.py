import os
import pandas as pd
from functools import reduce

# Path to the Dataset folder
dataset_dir = os.path.join(os.path.dirname(__file__), "Dataset")

# Get all CSV files in the Dataset directory
csv_files = [f for f in os.listdir(dataset_dir) if f.endswith('.csv')]

# Sort files by stat type (optional: alphabetical order)
csv_files.sort()

# Read all CSVs into DataFrames, keeping track of stat type
dataframes = []
stat_types = []
for csv_file in csv_files:
    stat_type = csv_file.replace('_stats.csv', '')
    df = pd.read_csv(os.path.join(dataset_dir, csv_file))
    # Rename columns to include stat type, except 'Player Name' and 'Team'
    df = df.rename(columns={col: f"{stat_type}_{col}" if col not in ['Player Name', 'Team'] else col for col in df.columns})
    dataframes.append(df)
    stat_types.append(stat_type)

# Merge all DataFrames on 'Player Name' and 'Team'
merged_df = reduce(lambda left, right: pd.merge(left, right, on=['Player Name', 'Team'], how='outer'), dataframes)

# Save merged DataFrame to CSV
output_path = os.path.join(os.path.dirname(__file__), "merged_dataset.csv")
merged_df.to_csv(output_path, index=False)
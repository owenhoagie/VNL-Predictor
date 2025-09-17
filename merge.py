import pandas as pd
import glob
import os

dataset_dir = "Dataset"
csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))

# Read all CSVs into dataframes and keep track of their columns
dfs = []
column_groups = []
for f in csv_files:
    df = pd.read_csv(f)
    dfs.append(df)
    # Exclude Player Name and Team from stat columns
    stat_cols = [col for col in df.columns if col not in ["Player Name", "Team"]]
    column_groups.append(stat_cols)

# Merge all dataframes on Player Name and Team
merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df, on=["Player Name", "Team"], how="outer")

# Fill NaN with 0
merged_df = merged_df.fillna(0)

# Build final column order: Player Name, Team, then grouped stat columns
final_columns = ["Player Name", "Team"] + [col for group in column_groups for col in group]
merged_df = merged_df[final_columns]

merged_df.to_csv("merged_stats.csv", index=False)
print("Merged stats saved to merged_stats.csv")
import pandas as pd

# Load both CSVs
rankings = pd.read_csv('RatingSystem/player_rankings.csv')
merged = pd.read_csv('merged_stats.csv')

# Select only relevant columns from rankings and rename for output
selected_cols = ['Player Name', 'Team', 'Position', 'positional_rating',
                 'rating_att', 'rating_blk', 'rating_serv', 'rating_set', 'rating_def', 'rating_recv']
rankings_selected = rankings[selected_cols].copy()
rankings_selected.rename(columns={
    'positional_rating': 'Impact',
    'rating_att': 'Attacking Rating',
    'rating_blk': 'Blocking Rating',
    'rating_serv': 'Serving Rating',
    'rating_set': 'Setting Rating',
    'rating_def': 'Defense Rating',
    'rating_recv': 'Receiving Rating'
}, inplace=True)

# Merge on Player Name, Team, and Position to avoid mixing stats for identical names
merged_out = pd.merge(merged, rankings_selected, on=['Player Name', 'Team', 'Position'], how='left')

# Desired column order
base_cols = ['Player Name', 'Team', 'Position', 'Age', 'Height']
new_stats = ['Impact', 'Attacking Rating', 'Blocking Rating', 'Serving Rating', 'Setting Rating', 'Defense Rating', 'Receiving Rating']
other_cols = [col for col in merged_out.columns if col not in base_cols + new_stats]
final_cols = base_cols + new_stats + other_cols

# Save to merged_stats.csv (overwrite)
merged_out[final_cols].to_csv('merged_stats.csv', index=False)
print('Merged ratings added to merged_stats.csv with new stats at the start.')

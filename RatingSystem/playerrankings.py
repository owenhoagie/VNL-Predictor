import pandas as pd
import numpy as np
import os

def clamp(x, minv=0, maxv=1):
    return max(minv, min(x, maxv))

def pctl95(series):
    return np.percentile(series.dropna(), 95) if len(series.dropna()) > 0 else 1

df = pd.read_csv('merged_stats.csv')

# Reference maxima (95th percentile)
ref_max_attacks_per_match = pctl95(df['Attacks Per Match'])
ref_max_blocks_per_match = pctl95(df['Blocks Per Match'])
ref_max_serves_per_match = pctl95(df['Serves Per Match'])
ref_max_sets_per_match = pctl95(df['Sets Per Match'])
ref_max_digs_per_match = pctl95(df['Digs Per Match'])
ref_max_receives_per_match = pctl95(df['Receives Per Match'])

# Attacking
def attacking(row):
    K = row['Kills']
    E = row['Attacking Errors']
    A = row['Attacking Attempts']
    KPM = row['Kills Per Match'] if 'Kills Per Match' in row else row['Attacks Per Match']
    eff = (K - E) / A if A > 0 else 0
    vol = KPM / df['Kills Per Match'].max() if 'Kills Per Match' in df else KPM / df['Attacks Per Match'].max()
    raw = (max(eff, 0) ** 0.5) * (max(vol, 0) ** 1.2)
    return [eff, vol, raw]

# Blocking
def blocking(row):
    B = row['Blocks']
    BE = row['Blocking Errors']
    R = row['Rebounds']
    BPM = row['Blocks Per Match']
    denom = B + BE + R
    # Weigh errors less: use only blocks over total attempts
    eff = B / denom if denom > 0 else 0
    vol = BPM / df['Blocks Per Match'].max()
    raw = (max(eff, 0) ** 0.4) * (max(vol, 0) ** 1.3)
    return [eff, vol, raw]

# Serving
def serving(row):
    A = row['Aces']
    SE = row['Service Errors']
    SA = row['Service Attempts']
    APM = row['Aces Per Match'] if 'Aces Per Match' in row else row['Serves Per Match']
    # Weigh errors less: use only aces over attempts
    eff = A / SA if SA > 0 else 0
    vol = APM / df['Aces Per Match'].max() if 'Aces Per Match' in df else APM / df['Serves Per Match'].max()
    raw = (max(eff, 0) ** 0.6) * (max(vol, 0) ** 1.1)
    return [eff, vol, raw]

# Setting
def setting(row):
    RS = row['Running Sets']
    SS = row['Still Sets']
    SE = row['Setting Errors']
    SPM = row['Sets Per Match']
    denom = RS + SS + SE
    eff = RS / denom if denom > 0 else 0
    vol = SPM / df['Sets Per Match'].max()
    raw = (max(eff, 0) ** 0.5) * (max(vol, 0) ** 1.2)
    return [eff, vol, raw]

# Defense
def defense(row):
    GS = row['Great Saves']
    DE = row['Defensive Errors']
    DR = row['Defensive Receptions']
    DPM = row['Digs Per Match']
    eff = (GS - DE) / DR if DR > 0 else 0
    vol = DPM / df['Digs Per Match'].max()
    raw = (max(eff, 0) ** 0.4) * (max(vol, 0) ** 1.3)
    return [eff, vol, raw]

# Receiving
def receiving(row):
    SR = row['Successful Receives']
    RE = row['Receiving Errors']
    SRc = row['Service Receptions']
    RPM = row['Receives Per Match']
    eff = (SR - RE) / SRc if SRc > 0 else 0
    vol = RPM / df['Receives Per Match'].max()
    raw = (max(eff, 0) ** 0.5) * (max(vol, 0) ** 1.2)
    return [eff, vol, raw]

# Apply formulas
for cat, func in zip(
    ['att', 'blk', 'serv', 'set', 'def', 'recv'],
    [attacking, blocking, serving, setting, defense, receiving]
):
    df[[f'{cat}_eff', f'{cat}_vol', f'{cat}_raw']] = df.apply(lambda row: func(row), axis=1, result_type='expand')
    max_raw = df[f'{cat}_raw'].max()
    df[f'rating_{cat}'] = (100 * df[f'{cat}_raw'] / max_raw).round(2) if max_raw > 0 else 0

# Print best rating in each category and the player who has it
for cat in ['att', 'blk', 'serv', 'set', 'def', 'recv']:
    best_idx = df[f'rating_{cat}'].idxmax()
    best_player = df.loc[best_idx, 'Player Name']
    best_team = df.loc[best_idx, 'Team']
    best_rating = df.loc[best_idx, f'rating_{cat}']
    print(f"Best {cat} rating: {best_rating} ({best_player}, {best_team})")

# Output with sub-scores for transparency
out_cols = [
    'Player Name', 'Team',
    'rating_att', 'att_eff', 'att_vol', 'att_raw',
    'rating_blk', 'blk_eff', 'blk_vol', 'blk_raw',
    'rating_serv', 'serv_eff', 'serv_vol', 'serv_raw',
    'rating_set', 'set_eff', 'set_vol', 'set_raw',
    'rating_def', 'def_eff', 'def_vol', 'def_raw',
    'rating_recv', 'recv_eff', 'recv_vol', 'recv_raw'
]
os.makedirs('RatingSystem', exist_ok=True)
df[out_cols].to_csv('RatingSystem/player_rankings.csv', index=False)
print("Player rankings saved to RatingSystem/player_rankings.csv with component sub-scores.")
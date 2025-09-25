import pandas as pd
import numpy as np
import os

def clamp(x, minv=0, maxv=1):
    return max(minv, min(x, maxv))

def pctl95(series):
    return np.percentile(series.dropna(), 95) if len(series.dropna()) > 0 else 1

positional_weights = {
    "OUTSIDE HITTER": {
        "Attacking": 0.25,
        "Blocking": 0.15,
        "Serving": 0.10,
        "Setting": 0.05,
        "Defense": 0.15,
        "Receiving": 0.30
    },
    "OPPOSITE SPIKER": {
        "Attacking": 0.40,
        "Blocking": 0.30,
        "Serving": 0.10,
        "Setting": 0.05,
        "Defense": 0.15,
        "Receiving": 0.0
    },
    "MIDDLE BLOCKER": {
        "Attacking": 0.25,
        "Blocking": 0.45,
        "Serving": 0.15,
        "Setting": 0.05,
        "Defense": 0.05,
        "Receiving": 0.05
    },
    "SETTER": {
        "Attacking": 0.10,
        "Blocking": 0.05,
        "Serving": 0.10,
        "Setting": 0.50,
        "Defense": 0.10,
        "Receiving": 0.15
    },
    "LIBERO": {
        "Attacking": 0.0,
        "Blocking": 0.0,
        "Serving": 0.10,
        "Setting": 0.10,
        "Defense": 0.40,
        "Receiving": 0.40
    }
}

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

# Calculate positional weighted rating for each player
position_map = {
    'LIBERO': 'LIBERO',
    'OUTSIDE HITTER': 'OUTSIDE HITTER',
    'OPPOSITE HITTER': 'OPPOSITE SPIKER',
    'SETTER': 'SETTER',
    'MIDDLE BLOCKER': 'MIDDLE BLOCKER'
}
def get_raw_positional_rating(row):
    pos = row['Position']
    pos_full = position_map.get(pos, pos)
    weights = positional_weights.get(pos_full, positional_weights['OUTSIDE HITTER'])
    rating = sum([
        weights['Attacking'] * row['rating_att'],
        weights['Blocking'] * row['rating_blk'],
        weights['Serving'] * row['rating_serv'],
        weights['Setting'] * row['rating_set'],
        weights['Defense'] * row['rating_def'],
        weights['Receiving'] * row['rating_recv']
    ])
    return rating

df['raw_positional_rating'] = df.apply(get_raw_positional_rating, axis=1)

# Normalize positional rating by position group
for pos_name in positional_weights.keys():
    mask = df['Position'].str.strip().str.upper().map(position_map.get).fillna(df['Position'].str.strip().str.upper()) == pos_name
    max_rating = df.loc[mask, 'raw_positional_rating'].max()
    df.loc[mask, 'positional_rating'] = (100 * df.loc[mask, 'raw_positional_rating'] / max_rating).round(2) if max_rating > 0 else 0

# Output with positional rating as first value after player, team, position
out_cols = [
    'Player Name', 'Team', 'Position', 'positional_rating',
    'rating_att', 'att_eff', 'att_vol', 'att_raw',
    'rating_blk', 'blk_eff', 'blk_vol', 'blk_raw',
    'rating_serv', 'serv_eff', 'serv_vol', 'serv_raw',
    'rating_set', 'set_eff', 'set_vol', 'set_raw',
    'rating_def', 'def_eff', 'def_vol', 'def_raw',
    'rating_recv', 'recv_eff', 'recv_vol', 'recv_raw'
]
# Round all decimals to the hundredths for output columns
for col in out_cols:
    if df[col].dtype in [float, np.float64, np.float32]:
        df[col] = df[col].round(2)

os.makedirs('RatingSystem', exist_ok=True)
df[out_cols].to_csv('RatingSystem/player_rankings.csv', index=False)
print("Player rankings saved to RatingSystem/player_rankings.csv with normalized positional ratings.")
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
def load_data(filepath):
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows")
    return df
def clean_data(df):
    df = df.dropna()
    df = df[(df['x']<50) & (df['y']<50)]
    return df
def normalize_data(df):
    scaler = MinMaxScaler()
    df[['accel_x', 'accel_y', 'accel_z']] = scaler.fit_transform(df[['accel_x', 'accel_y', 'accel_z']])
    return df
def label_emotions(df):
    gesture_map = {
        1: 'happy', 
        2: ' sad',
        3: 'angry',
        4: 'calm'
    }
    df['emotion'] = df['gesture_id'].map(gesture_map)
    return df
def preprocess(filepath):
    raw = load_data(filepath)
    cleaned = clean_data(raw)
    normalized = normalize_data(cleaned)
    labeled = label_emotions(normalized)
    return labeled

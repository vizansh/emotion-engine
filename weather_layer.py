import pandas as pd

# Example: weather data collected from device sensors
# Columns: timestamp, temperature, humidity, condition
# condition could be strings like "sunny", "rainy", "stormy", "cloudy"

def load_weather(filepath):
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} weather rows")
    return df

def weather_to_emotion(temp, humidity, condition):
    # Simple rule-based mapping for now
    if condition == "sunny" and temp > 25:
        return "energetic"
    elif condition == "rainy":
        return "calm"
    elif condition == "stormy":
        return "anxious"
    elif humidity > 80:
        return "melancholic"
    else:
        return "neutral"

def label_weather_emotions(df):
    df['weather_emotion'] = df.apply(
        lambda row: weather_to_emotion(row['temperature'], row['humidity'], row['condition']),
        axis=1
    )
    return df

def preprocess_weather(filepath):
    raw = load_weather(filepath)
    labeled = label_weather_emotions(raw)
    return labeled

if __name__ == "__main__":
    weather_df = preprocess_weather("weather.csv")
    print(weather_df.head())
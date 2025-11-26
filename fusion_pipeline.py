import pandas as pd

def fuse_row(gesture_emotion, gesture_conf, weather_emotion, weather_conf):
    # If both agree, boost confidence
    if gesture_emotion == weather_emotion:
        fused = gesture_emotion
        conf = min(1.0, 0.6*gesture_conf + 0.6*weather_conf)
    else:
        # Rule-based weighting: gesture dominates real-time, weather sets context
        if gesture_conf >= weather_conf:
            fused = gesture_emotion
            conf = gesture_conf
        else:
            fused = weather_emotion
            conf = weather_conf
    return fused, conf

def fuse_emotions(gesture_df, weather_df):
    # Sort by timestamp
    gesture_df = gesture_df.sort_values("timestamp")
    weather_df = weather_df.sort_values("timestamp")

    # Align by nearest timestamp (merge_asof)
    fused = pd.merge_asof(
        gesture_df, weather_df,
        on="timestamp", direction="nearest", tolerance=1000  # 1s tolerance
    )

    # Apply fusion logic row by row
    fused["fused_emotion"], fused["fused_conf"] = zip(*fused.apply(
        lambda r: fuse_row(
            r.get("gesture_emotion"), r.get("gesture_conf", 0.8),
            r.get("weather_emotion"), r.get("weather_conf", 0.7)
        ), axis=1
    ))

    return fused[["timestamp", "gesture_emotion", "weather_emotion", "fused_emotion", "fused_conf"]]

if __name__ == "__main__":
    # Example usage
    gesture_df = pd.DataFrame({
        "timestamp": [1722064321, 1722064380],
        "gesture_emotion": ["happy", "calm"],
        "gesture_conf": [0.9, 0.8]
    })

    weather_df = pd.DataFrame({
        "timestamp": [1722064321, 1722064380],
        "weather_emotion": ["energetic", "calm"],
        "weather_conf": [0.7, 0.85]
    })

    fused_df = fuse_emotions(gesture_df, weather_df)
    print(fused_df)
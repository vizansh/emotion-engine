from fastapi import FastAPI
from pydantic import BaseModel
import time

# Import your layers
from fusion_pipeline import fuse_emotions
from personalization import PreferenceStore, Personalizer
from weather_layer import weather_to_emotion

# Create FastAPI app
app = FastAPI()

# Initialize personalization store
store = PreferenceStore("user_profiles.json")
perso = Personalizer(store)

# ----------- Request Models ----------- #

class GestureInput(BaseModel):
    timestamp: int
    emotion: str
    confidence: float = 0.8

class WeatherInput(BaseModel):
    timestamp: int
    temperature: float
    humidity: float
    condition: str

class InferenceRequest(BaseModel):
    user_id: str
    gesture: GestureInput
    weather: WeatherInput

class FeedbackRequest(BaseModel):
    user_id: str
    timestamp: int
    genre: str
    emotion: str
    outcome: str  # "like" or "skip"

# ----------- Endpoints ----------- #

@app.post("/infer")
def infer(req: InferenceRequest):
    # Step 1: Gesture emotion
    g_emotion = req.gesture.emotion
    g_conf = req.gesture.confidence

    # Step 2: Weather emotion
    w_emotion = weather_to_emotion(
        req.weather.temperature,
        req.weather.humidity,
        req.weather.condition
    )
    w_conf = 0.7  # fixed confidence for now

    # Step 3: Fusion (simple rule)
    fused_emotion = g_emotion if g_conf >= w_conf else w_emotion
    fused_conf = max(g_conf, w_conf)

    # Step 4: Personalization
    recs = perso.recommend(
        user_id=req.user_id,
        ts=req.gesture.timestamp,
        fused_emotion=fused_emotion,
        weather_emotion=w_emotion,
        top_n=3
    )

    from music_mapping import get_tracks_for_genre

    # Step 5: Return response
    return {
        "timestamp": req.gesture.timestamp,
        "gesture_emotion": {"label": g_emotion, "confidence": g_conf},
        "weather_emotion": {"label": w_emotion, "confidence": w_conf},
        "fused_emotion": {"label": fused_emotion, "confidence": fused_conf},
        "recommendations": [
            {
                "genre": rec["genre"],
                "score": rec["score"],
                "tracks": get_tracks_for_genre(rec["genre"], top_n=2)
            }
            for rec in recs["recommendations"]
        ]
    }

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    # Update personalization with feedback
    perso.update_feedback(
        user_id=req.user_id,
        ts=req.timestamp,
        genre=req.genre,
        emotion=req.emotion,
        outcome=req.outcome
    )
    return {"status": "success", "message": f"Feedback recorded: {req.outcome} for {req.genre}"}
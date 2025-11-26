
---

```markdown
# Emotion-Based Music Recommendation Engine 🎶

## Overview
This project is a demo backend that recommends music genres and playlists based on **user gestures** and **weather conditions**.  
It fuses multiple signals into a single emotion, applies personalization, and returns recommendations via a FastAPI service.

Core layers:
- **Gesture Layer** → detects emotion from user gestures
- **Weather Layer** → maps weather conditions to emotions
- **Fusion Layer** → combines gesture + weather into a unified emotion
- **Personalization Layer** → adapts recommendations based on user feedback
- **Inference API** → `/infer` endpoint for recommendations
- **Feedback API** → `/feedback` endpoint for user reactions
- **Music Mapping Layer** → maps genres to real playlists/tracks

---

## Setup

### Requirements
- Python 3.9+
- FastAPI
- Pydantic
- Uvicorn

Install dependencies:
```bash
pip install fastapi pydantic uvicorn
```

---

## Running the Server
From the project root:
```bash
uvicorn inference_api:app --reload
```

Open interactive docs:
```
http://127.0.0.1:8000/docs
```

---

## Endpoints

### POST `/infer`
Takes gesture + weather input, returns fused emotion and recommendations.

**Request Example:**
```json
{
  "user_id": "vansh_001",
  "gesture": {
    "timestamp": 1722064380,
    "emotion": "calm",
    "confidence": 0.85
  },
  "weather": {
    "timestamp": 1722064380,
    "temperature": 22,
    "humidity": 85,
    "condition": "rainy"
  }
}
```

**Response Example:**
```json
{
  "timestamp": 1722064380,
  "gesture_emotion": {"label": "calm", "confidence": 0.85},
  "weather_emotion": {"label": "calm", "confidence": 0.7},
  "fused_emotion": {"label": "calm", "confidence": 0.85},
  "recommendations": [
    {
      "genre": "lofi",
      "score": 0.6,
      "tracks": [
        {"title": "Lofi Chill Beats", "url": "https://open.spotify.com/playlist/..."},
        {"title": "Late Night Lofi", "url": "https://open.spotify.com/playlist/..."}
      ]
    },
    {
      "genre": "ambient",
      "score": 0.6,
      "tracks": [
        {"title": "Ambient Relaxation", "url": "https://open.spotify.com/playlist/..."},
        {"title": "Deep Ambient", "url": "https://open.spotify.com/playlist/..."}
      ]
    }
  ]
}
```

---

### POST `/feedback`
Records user reactions (like/skip) to improve personalization.

**Request Example:**
```json
{
  "user_id": "vansh_001",
  "timestamp": 1722064380,
  "genre": "ambient",
  "emotion": "calm",
  "outcome": "skip"
}
```

**Response Example:**
```json
{"status": "success", "message": "Feedback recorded: skip for ambient"}
```

---

## Roadmap
- ✅ Core layers implemented
- ✅ Feedback loop
- ✅ Music mapping
- 🔜 Data collection for training
- 🔜 Frontend integration
- 🔜 Cloud deployment

---

## Author
Built by Vansh with guidance from Microsoft Copilot 🤝
```

---
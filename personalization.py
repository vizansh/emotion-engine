import json
import time
from collections import defaultdict
from math import exp
from typing import Dict, List, Tuple, Optional

# ----------- Defaults (Logic 1: Emotion → Genre prior) ----------- #

EMOTION_TO_GENRES: Dict[str, List[str]] = {
    "happy":      ["pop", "dance", "indie-pop"],
    "calm":       ["lofi", "ambient", "jazz"],
    "excited":    ["edm", "trap", "alt-rock"],
    "sad":        ["sad-pop", "acoustic", "lofi"],
    "angry":      ["metal", "hard-rock", "hip-hop"],
    "neutral":    ["chillhop", "indie", "classical"],
    "energetic":  ["edm", "pop", "future-bass"],
    "melancholic":["indie-folk", "acoustic", "ambient"],
    "anxious":    ["piano", "ambient", "lofi"],
}

# Context priors (weather/time-of-day nudges)
WEATHER_GENRE_BOOSTS: Dict[str, Dict[str, float]] = {
    "sunny": {"pop": 0.15, "edm": 0.12, "indie-pop": 0.1},
    "rainy": {"lofi": 0.18, "ambient": 0.15, "jazz": 0.12},
    "stormy": {"ambient": 0.2, "piano": 0.15, "lofi": 0.1},
    "cloudy": {"indie": 0.12, "chillhop": 0.1},
}

TIME_GENRE_BOOSTS: Dict[str, Dict[str, float]] = {
    "morning": {"indie": 0.1, "classical": 0.12, "chillhop": 0.08},
    "afternoon": {"pop": 0.08, "indie-pop": 0.06},
    "evening": {"lofi": 0.12, "jazz": 0.1, "ambient": 0.08},
    "night": {"ambient": 0.14, "piano": 0.12, "lofi": 0.1},
}

def time_bucket_from_timestamp(ts: int) -> str:
    hour = time.localtime(ts).tm_hour
    if 5 <= hour < 12: return "morning"
    if 12 <= hour < 17: return "afternoon"
    if 17 <= hour < 22: return "evening"
    return "night"

# ----------- User profile & storage ----------- #

class UserProfile:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # Genre preference weights (learned)
        self.genre_weights: Dict[str, float] = defaultdict(float)
        # Emotion bias (some users bias towards/away from emotions)
        self.emotion_bias: Dict[str, float] = defaultdict(float)
        # Feedback history: [(ts, genre, outcome)]
        self.history: List[Tuple[int, str, str]] = []
        # Exploration rate (epsilon-greedy)
        self.epsilon: float = 0.08
        # Optional cooldown to avoid repeating recent skips
        self.cooldown_genres: Dict[str, int] = {}

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "genre_weights": dict(self.genre_weights),
            "emotion_bias": dict(self.emotion_bias),
            "history": self.history,
            "epsilon": self.epsilon,
            "cooldown_genres": self.cooldown_genres,
        }

    @staticmethod
    def from_dict(data: Dict):
        up = UserProfile(data["user_id"])
        up.genre_weights = defaultdict(float, data.get("genre_weights", {}))
        up.emotion_bias = defaultdict(float, data.get("emotion_bias", {}))
        up.history = [tuple(h) for h in data.get("history", [])]
        up.epsilon = data.get("epsilon", 0.08)
        up.cooldown_genres = data.get("cooldown_genres", {})
        return up

class PreferenceStore:
    def __init__(self, path: str = "user_profiles.json"):
        self.path = path
        self._profiles: Dict[str, UserProfile] = {}

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for uid, pdata in raw.items():
                self._profiles[uid] = UserProfile.from_dict(pdata)
        except FileNotFoundError:
            self._profiles = {}

    def save(self):
        obj = {uid: p.to_dict() for uid, p in self._profiles.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    def get(self, user_id: str) -> UserProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = UserProfile(user_id)
        return self._profiles[user_id]

# ----------- Personalizer core ----------- #

class Personalizer:
    def __init__(self, store: PreferenceStore):
        self.store = store
        self.store.load()
        # Learning rates
        self.lr_like = 0.12
        self.lr_skip = 0.10
        self.lr_emotion_bias = 0.04
        # Decay (recent behavior weighs more)
        self.recency_half_life_sec = 7 * 24 * 3600  # 7 days

    def _recency_weight(self, ts_event: int, ts_now: int) -> float:
        # Exponential decay based on half-life
        dt = max(0, ts_now - ts_event)
        lam = (0.693 / self.recency_half_life_sec)
        return exp(-lam * dt)

    def update_feedback(self, user_id: str, ts: int, genre: str, emotion: str, outcome: str):
        """
        outcome: 'like' | 'skip'
        """
        profile = self.store.get(user_id)
        profile.history.append((ts, genre, outcome))
        w = self._recency_weight(ts, int(time.time()))

        if outcome == "like":
            profile.genre_weights[genre] += self.lr_like * w
            profile.emotion_bias[emotion] += self.lr_emotion_bias * w
            # Remove cooldown if previously set
            if genre in profile.cooldown_genres:
                profile.cooldown_genres.pop(genre, None)
        elif outcome == "skip":
            profile.genre_weights[genre] -= self.lr_skip * w
            profile.emotion_bias[emotion] -= self.lr_emotion_bias * 0.5 * w
            # Cooldown: avoid repeating immediately after skip
            profile.cooldown_genres[genre] = int(time.time()) + 2 * 3600  # 2 hours

        # Clamp weights to reasonable bounds
        profile.genre_weights[genre] = max(-1.0, min(2.0, profile.genre_weights[genre]))
        profile.emotion_bias[emotion] = max(-0.6, min(0.8, profile.emotion_bias[emotion]))

        self.store.save()

    def _base_scores(self, fused_emotion: str) -> Dict[str, float]:
        """
        Logic 1 prior: emotion -> genres (converted into base scores).
        """
        base = defaultdict(float)
        for genre in EMOTION_TO_GENRES.get(fused_emotion, ["indie"]):
            base[genre] += 0.6  # strong prior
        return base

    def _apply_context_boosts(self, scores: Dict[str, float], weather_emotion: Optional[str], time_bucket: str):
        # Weather boosts
        if weather_emotion:
            for g, b in WEATHER_GENRE_BOOSTS.get(weather_emotion, {}).items():
                scores[g] += b
        # Time-of-day boosts
        for g, b in TIME_GENRE_BOOSTS.get(time_bucket, {}).items():
            scores[g] += b

    def _apply_user_weights(self, scores: Dict[str, float], profile: UserProfile, fused_emotion: str):
        # Emotion bias nudges overall scores
        bias = profile.emotion_bias.get(fused_emotion, 0.0)
        for g in scores:
            scores[g] += bias
        # Genre-specific weights
        for g, w in profile.genre_weights.items():
            scores[g] += w

    def _apply_cooldowns(self, scores: Dict[str, float], profile: UserProfile):
        now = int(time.time())
        for g, until in list(profile.cooldown_genres.items()):
            if until > now:
                scores[g] -= 0.25  # penalize during cooldown
            else:
                profile.cooldown_genres.pop(g, None)

    def _explore_candidates(self, fused_emotion: str, k: int = 2) -> List[str]:
        # Exploration pool: genres adjacent to emotion mapping
        base = EMOTION_TO_GENRES.get(fused_emotion, ["indie"])
        neighbors = set(base)
        # Add a couple cross-emotion neighbors to keep it fresh
        neighbors.update(["chillhop", "indie", "acoustic", "ambient", "pop", "lofi"])
        return list(neighbors)[:max(k, len(neighbors))]

    def recommend(self, user_id: str, ts: int, fused_emotion: str, weather_emotion: Optional[str] = None, top_n: int = 3) -> Dict:
        profile = self.store.get(user_id)
        time_bucket = time_bucket_from_timestamp(ts)

        # Start with Logic 1 prior scores
        scores = self._base_scores(fused_emotion)

        # Embed Logic 1 inside Logic 2 adjustments
        self._apply_context_boosts(scores, weather_emotion, time_bucket)
        self._apply_user_weights(scores, profile, fused_emotion)
        self._apply_cooldowns(scores, profile)

        # Exploration: occasionally add diverse candidates
        import random
        if random.random() < profile.epsilon:
            for g in self._explore_candidates(fused_emotion, k=4):
                scores[g] += 0.08  # light exploration bonus

        # Rank and output
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top = ranked[:top_n]
        return {
            "user_id": user_id,
            "timestamp": ts,
            "fused_emotion": fused_emotion,
            "weather_emotion": weather_emotion,
            "recommendations": [{"genre": g, "score": round(s, 3)} for g, s in top],
            "meta": {
                "time_bucket": time_bucket,
                "epsilon": profile.epsilon
            }
        }


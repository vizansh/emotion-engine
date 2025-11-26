# Simple genre-to-playlist mapping
GENRE_MAP = {
    "lofi": [
        {"title": "Lofi Chill Beats", "url": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC"},
        {"title": "Late Night Lofi", "url": "https://open.spotify.com/playlist/37i9dQZF1DX6xOPeSOGone"}
    ],
    "ambient": [
        {"title": "Ambient Relaxation", "url": "https://open.spotify.com/playlist/37i9dQZF1DWV0gynK7G6pD"},
        {"title": "Deep Ambient", "url": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO"}
    ],
    "jazz": [
        {"title": "Jazz Classics", "url": "https://open.spotify.com/playlist/37i9dQZF1DXbITWG1ZJKYt"},
        {"title": "Smooth Jazz", "url": "https://open.spotify.com/playlist/37i9dQZF1DX7YCknf2jT6s"}
    ]
}

def get_tracks_for_genre(genre: str, top_n: int = 2):
    """Return top N tracks/playlists for a given genre."""
    if genre in GENRE_MAP:
        return GENRE_MAP[genre][:top_n]
    return [{"title": "Unknown Genre", "url": ""}]
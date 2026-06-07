"""
Configuration for Thomas Demo
"""

# Audio constraints
MIN_DURATION = 3    # seconds
MAX_DURATION = 15   # seconds
MIN_SAMPLE_RATE = 16000  # Hz (16kHz minimum)

# Paths
DATABASE_PATH = "data/thomas.db"
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# App info
APP_TITLE = "Thomas"
APP_SUBTITLE = "Voice-Music Separation & Emotion Labeling"

# TorchServe API endpoints (update these when AI team provides them)
TORCHSERVE_BASE_URL = "http://localhost:8080"
SEPARATION_ENDPOINT = f"{TORCHSERVE_BASE_URL}/predictions/voice_separator"
EMOTION_ENDPOINT = f"{TORCHSERVE_BASE_URL}/predictions/emotion_labeler"

# API timeout (seconds)
API_TIMEOUT = 60

# Emotion labels (update based on model output)
EMOTION_LABELS = {
    "happy": {"label": "Mutlu", "emoji": "😊", "color": "#F4D03F"},
    "sad": {"label": "Üzgün", "emoji": "😢", "color": "#5DADE2"},
    "angry": {"label": "Kızgın", "emoji": "😠", "color": "#E74C3C"},
    "fear": {"label": "Korkmuş", "emoji": "😨", "color": "#9B59B6"},
    "surprise": {"label": "Şaşkın", "emoji": "😲", "color": "#E67E22"},
    "neutral": {"label": "Nötr", "emoji": "😐", "color": "#95A5A6"},
    "disgust": {"label": "İğrenme", "emoji": "🤢", "color": "#27AE60"},
}
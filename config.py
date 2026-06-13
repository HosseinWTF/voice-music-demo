"""
Configuration for Thomas Demo
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Audio constraints
MIN_DURATION = 3    # seconds
MAX_DURATION = 15   # seconds
MIN_SAMPLE_RATE = 16000  # Hz (16kHz minimum)

# Paths
DATABASE_PATH = "data/thomas.db"
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
DATASET_DIR = "dataset"

# App info
APP_TITLE = "Thomas"
APP_SUBTITLE = "Voice-Music Separation & Emotion Labeling"

# Rate limiting
RATE_LIMIT_MAX_UPLOADS = 5
RATE_LIMIT_WINDOW_MINUTES = 60
RATE_LIMIT_EXEMPT_USERS = [
    u.strip()
    for u in os.getenv("RATE_LIMIT_EXEMPT", "").split(",")
    if u.strip()
]

# AI API endpoints
SEPARATION_ENDPOINT = os.getenv("SEPARATION_ENDPOINT", "")
EMOTION_ENDPOINT = os.getenv("EMOTION_ENDPOINT", "")
API_TIMEOUT = 120

# Emotion labels
EMOTION_LABELS = {
    "happy":     {"label": "Happy",    "emoji": "😊", "color": "#F4D03F"},
    "sad":       {"label": "Sad",      "emoji": "😢", "color": "#5DADE2"},
    "angry":     {"label": "Angry",    "emoji": "😠", "color": "#E74C3C"},
    "fear":      {"label": "Fear",     "emoji": "😨", "color": "#9B59B6"},
    "fearful":   {"label": "Fear",     "emoji": "😨", "color": "#9B59B6"},
    "surprise":  {"label": "Surprise", "emoji": "😮", "color": "#E67E22"},
    "surprised": {"label": "Surprise", "emoji": "😮", "color": "#E67E22"},
    "neutral":   {"label": "Neutral",  "emoji": "😐", "color": "#95A5A6"},
    "disgust":   {"label": "Disgust",  "emoji": "🤢", "color": "#27AE60"},
}
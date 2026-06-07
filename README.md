# Thomas - Voice-Music Separation & Emotion Labeling

Minimal demo for university capstone project presentation.

## Features

- Upload .wav audio files (3-15 seconds)
- Audio playback
- Basic validation
- SQLite database storage
- Dashboard preview (placeholder)

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
thomas-demo/
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── app.py               # Main application (159 lines)
├── database.py          # Simple SQLite database (51 lines)
├── config.py            # Configuration (15 lines)
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore rules
├── uploads/            # Uploaded audio files (gitignored)
└── data/               # SQLite database (gitignored)
```

**Total Code: 225 lines**

## Current Status

This is a **minimal visual demo** for presentation purposes:

- ✅ File upload with validation
- ✅ Audio playback
- ✅ Database storage
- ⏳ AI processing (coming soon - placeholder button)
- ⏳ Dashboard (frontend only - placeholder data)

## Tech Stack

- Python 3.10+
- Streamlit (web UI)
- SQLite (database)
- Librosa (audio validation)

## Future Implementation

The AI models for voice-music separation and emotion detection will be integrated after the initial presentation.

## Deploy to Streamlit Cloud

This minimal version is ready to deploy on Streamlit Community Cloud without any heavy dependencies.

"""
Run this script ONCE to import all existing .wav files in the dataset/ folder into the database.
Usage: python import_dataset.py
"""

from pathlib import Path
import librosa
import config
import database

EMOTION_KEYWORDS = [
    "angry", "anger",
    "happy", "happiness",
    "sad", "sadness",
    "fear", "fearful",
    "surprise", "surprised", "surprized", "suprised",
    "neutral",
    "disgust", "disgusted"
]

EMOTION_MAP = {
    "anger": "angry",
    "happiness": "happy",
    "sadness": "sad",
    "fearful": "fear",
    "surprised": "surprise",
    "surprized": "surprise",
    "suprised": "surprise",
    "disgusted": "disgust"
}


def detect_emotion(filename: str):
    name = filename.lower()
    for keyword in EMOTION_KEYWORDS:
        if keyword in name:
            return EMOTION_MAP.get(keyword, keyword)
    return None


def import_preloaded_clips():
    database.init_db()

    dataset_path = Path(config.DATASET_DIR)
    if not dataset_path.exists():
        print("dataset/ folder not found. Creating it...")
        dataset_path.mkdir()
        print("Created dataset/ — add your .wav files and run this script again.")
        return

    wav_files = list(dataset_path.glob("*.wav"))
    if not wav_files:
        print("No .wav files found in dataset/")
        return

    print(f"Found {len(wav_files)} .wav files. Importing...")

    imported = 0
    skipped = 0
    no_emotion = 0

    for wav_path in sorted(wav_files):
        try:
            audio, sr = librosa.load(str(wav_path), sr=None, mono=True)
            duration = round(librosa.get_duration(y=audio, sr=sr), 2)
            emotion = detect_emotion(wav_path.name)

            database.add_to_dataset(
                filename=wav_path.name,
                original_filename=wav_path.name,
                duration=duration,
                emotion=emotion,
                source="preloaded"
            )

            emotion_str = emotion if emotion else "no label"
            print(f"  ✓ {wav_path.name} ({duration}s) — {emotion_str}")
            imported += 1
            if not emotion:
                no_emotion += 1

        except Exception as e:
            print(f"  ✗ {wav_path.name} — {e}")
            skipped += 1

    print(f"\nDone. {imported} imported, {skipped} skipped, {no_emotion} without emotion label.")


if __name__ == "__main__":
    import_preloaded_clips()
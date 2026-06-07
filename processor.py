"""
Thomas — Local AI Processor
Demucs (voice/music separation) + Wav2Vec2 (emotion recognition)
No external API needed — runs fully local after first model download.
"""

import os
import time
import tempfile
import subprocess
from pathlib import Path

import torch
import numpy as np
import soundfile as sf
import librosa
from transformers import pipeline


# ── Emotion model ID ──────────────────────────────────────────────────────────
EMOTION_MODEL_ID = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"

# ── Module-level singletons (loaded once, reused) ─────────────────────────────
_emotion_pipeline = None


def _get_emotion_pipeline():
    """Lazy-load the emotion recognition pipeline."""
    global _emotion_pipeline
    if _emotion_pipeline is None:
        device = 0 if torch.cuda.is_available() else -1  # GPU if available, else CPU
        _emotion_pipeline = pipeline(
            "audio-classification",
            model=EMOTION_MODEL_ID,
            device=device,
        )
    return _emotion_pipeline


# ── Voice / Music Separation ──────────────────────────────────────────────────

def separate_voice(audio_path: str, output_dir: str) -> dict:
    """
    Run Demucs htdemucs model to separate vocals from music.

    Demucs CLI writes separated tracks to:
        <output_dir>/htdemucs/<stem>/{vocals,drums,bass,other}.wav

    We grab vocals.wav and copy it to output_dir root for easy access.

    Returns:
        dict: success, vocal_path, error
    """
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        stem = Path(audio_path).stem

        cmd = [
            "python", "-m", "demucs",
            "--two-stems", "vocals",   # only separate vocals vs rest
            "--out", output_dir,
            "--name", "htdemucs",
            audio_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "vocal_path": None,
                "error": f"Demucs hatası: {result.stderr[-500:] if result.stderr else 'Bilinmeyen hata'}"
            }

        # Demucs output path
        vocal_src = Path(output_dir) / "htdemucs" / stem / "vocals.wav"

        if not vocal_src.exists():
            return {
                "success": False,
                "vocal_path": None,
                "error": f"Vokal dosyası bulunamadı: {vocal_src}"
            }

        # Copy to flat output location with original stem prefix
        vocal_dst = Path(output_dir) / f"vocal_{stem}.wav"
        import shutil
        shutil.copy2(vocal_src, vocal_dst)

        return {
            "success": True,
            "vocal_path": str(vocal_dst),
            "error": None,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "vocal_path": None, "error": "Demucs zaman aşımına uğradı (>5 dk)"}
    except Exception as e:
        return {"success": False, "vocal_path": None, "error": str(e)}


# ── Emotion Recognition ───────────────────────────────────────────────────────

def label_emotion(vocal_path: str) -> dict:
    """
    Run Wav2Vec2 emotion classifier on the separated vocal track.

    The model expects 16kHz mono audio. We resample if needed.

    Returns:
        dict: success, emotion, confidence, scores, error
    """
    try:
        pipe = _get_emotion_pipeline()

        # Load & resample to 16kHz mono
        audio, sr = librosa.load(vocal_path, sr=16000, mono=True)

        # Model expects numpy array at 16kHz
        outputs = pipe({"array": audio, "sampling_rate": 16000}, top_k=None)

        # outputs is a list of {"label": str, "score": float}
        scores = {item["label"].lower(): round(item["score"], 4) for item in outputs}
        top = max(outputs, key=lambda x: x["score"])
        emotion = top["label"].lower()
        confidence = round(top["score"], 4)

        return {
            "success": True,
            "emotion": emotion,
            "confidence": confidence,
            "scores": scores,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "emotion": None,
            "confidence": None,
            "scores": {},
            "error": str(e),
        }


# ── Full Pipeline ─────────────────────────────────────────────────────────────

def process_audio(audio_path: str, output_dir: str) -> dict:
    """
    Full pipeline: separate voice → label emotion.

    Returns:
        dict with all results and timing info.
    """
    start = time.time()

    # Step 1 — Separation
    sep = separate_voice(audio_path, output_dir)
    if not sep["success"]:
        return {
            "success": False,
            "stage": "separation",
            "error": sep["error"],
            "processing_time": round(time.time() - start, 2),
        }

    # Step 2 — Emotion
    emo = label_emotion(sep["vocal_path"])
    if not emo["success"]:
        return {
            "success": False,
            "stage": "emotion",
            "error": emo["error"],
            "vocal_path": sep["vocal_path"],
            "processing_time": round(time.time() - start, 2),
        }

    return {
        "success": True,
        "stage": "completed",
        "vocal_path": sep["vocal_path"],
        "emotion": emo["emotion"],
        "confidence": emo["confidence"],
        "scores": emo["scores"],
        "processing_time": round(time.time() - start, 2),
        "error": None,
    }
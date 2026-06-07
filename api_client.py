"""
TorchServe API Client for Thomas Demo
Handles communication with voice separation and emotion labeling models
"""

import os
import time
import requests
import tempfile
from pathlib import Path
import backupconfig


class ThomasAPIClient:
    """Client for TorchServe model API endpoints."""

    def __init__(self):
        self.separation_url = backupconfig.SEPARATION_ENDPOINT
        self.emotion_url = backupconfig.EMOTION_ENDPOINT
        self.timeout = backupconfig.API_TIMEOUT

    def health_check(self):
        """Check if TorchServe is reachable."""
        try:
            response = requests.get(
                f"{backupconfig.TORCHSERVE_BASE_URL}/ping",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False

    def separate_voice(self, audio_file_path: str, output_dir: str) -> dict:
        """
        Send audio to voice separation model.
        
        Args:
            audio_file_path: Path to input .wav file
            output_dir: Directory to save separated vocal track
            
        Returns:
            dict with keys: success, vocal_path, error
        """
        try:
            with open(audio_file_path, "rb") as f:
                files = {"data": (Path(audio_file_path).name, f, "audio/wav")}
                response = requests.post(
                    self.separation_url,
                    files=files,
                    timeout=self.timeout
                )

            if response.status_code != 200:
                return {
                    "success": False,
                    "vocal_path": None,
                    "error": f"API returned status {response.status_code}: {response.text}"
                }

            # Save returned vocal audio
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            vocal_filename = f"vocal_{Path(audio_file_path).stem}.wav"
            vocal_path = os.path.join(output_dir, vocal_filename)

            with open(vocal_path, "wb") as f:
                f.write(response.content)

            return {
                "success": True,
                "vocal_path": vocal_path,
                "error": None
            }

        except requests.exceptions.Timeout:
            return {"success": False, "vocal_path": None, "error": "API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "vocal_path": None, "error": "Could not connect to TorchServe API"}
        except Exception as e:
            return {"success": False, "vocal_path": None, "error": str(e)}

    def label_emotion(self, vocal_file_path: str) -> dict:
        """
        Send vocal audio to emotion labeling model.
        
        Args:
            vocal_file_path: Path to separated vocal .wav file
            
        Returns:
            dict with keys: success, emotion, confidence, scores, error
        """
        try:
            with open(vocal_file_path, "rb") as f:
                files = {"data": (Path(vocal_file_path).name, f, "audio/wav")}
                response = requests.post(
                    self.emotion_url,
                    files=files,
                    timeout=self.timeout
                )

            if response.status_code != 200:
                return {
                    "success": False,
                    "emotion": None,
                    "confidence": None,
                    "scores": {},
                    "error": f"API returned status {response.status_code}: {response.text}"
                }

            result = response.json()

            # Expected response format from model:
            # { "emotion": "happy", "confidence": 0.92, "scores": {"happy": 0.92, "sad": 0.03, ...} }
            return {
                "success": True,
                "emotion": result.get("emotion"),
                "confidence": result.get("confidence"),
                "scores": result.get("scores", {}),
                "error": None
            }

        except requests.exceptions.Timeout:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": "API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": "Could not connect to TorchServe API"}
        except Exception as e:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": str(e)}

    def process_audio(self, audio_file_path: str, output_dir: str) -> dict:
        """
        Full pipeline: separate voice then label emotion.
        
        Returns:
            dict with all results and timing info
        """
        start_time = time.time()

        # Step 1: Voice separation
        sep_result = self.separate_voice(audio_file_path, output_dir)
        if not sep_result["success"]:
            return {
                "success": False,
                "stage": "separation",
                "error": sep_result["error"],
                "processing_time": time.time() - start_time
            }

        # Step 2: Emotion labeling on separated vocals
        emo_result = self.label_emotion(sep_result["vocal_path"])
        if not emo_result["success"]:
            return {
                "success": False,
                "stage": "emotion",
                "error": emo_result["error"],
                "processing_time": time.time() - start_time,
                "vocal_path": sep_result["vocal_path"]
            }

        processing_time = time.time() - start_time

        return {
            "success": True,
            "stage": "completed",
            "vocal_path": sep_result["vocal_path"],
            "emotion": emo_result["emotion"],
            "confidence": emo_result["confidence"],
            "scores": emo_result["scores"],
            "processing_time": round(processing_time, 2),
            "error": None
        }


# Singleton client instance
_client = None


def get_client():
    global _client
    if _client is None:
        _client = ThomasAPIClient()
    return _client
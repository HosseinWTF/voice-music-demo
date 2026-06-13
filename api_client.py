"""
API Client for Thomas Demo
Handles communication with voice separation and emotion labeling models
"""

import os
import time
import requests
from pathlib import Path
import config


class ThomasAPIClient:

    def __init__(self):
        self.separation_url = config.SEPARATION_ENDPOINT
        self.emotion_url = config.EMOTION_ENDPOINT
        self.timeout = config.API_TIMEOUT

    def separate_voice(self, audio_file_path: str, output_dir: str) -> dict:
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
            return {"success": False, "vocal_path": None, "error": "Separation API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "vocal_path": None, "error": "Could not connect to Separation API"}
        except Exception as e:
            return {"success": False, "vocal_path": None, "error": str(e)}

    def label_emotion(self, vocal_file_path: str) -> dict:
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

            return {
                "success": True,
                "emotion": result.get("emotion"),
                "confidence": result.get("confidence"),
                "scores": result.get("scores", {}),
                "error": None
            }

        except requests.exceptions.Timeout:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": "Emotion API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": "Could not connect to Emotion API"}
        except Exception as e:
            return {"success": False, "emotion": None, "confidence": None, "scores": {}, "error": str(e)}

    def process_audio(self, audio_file_path: str, output_dir: str) -> dict:
        start_time = time.time()

        sep_result = self.separate_voice(audio_file_path, output_dir)
        if not sep_result["success"]:
            return {
                "success": False,
                "stage": "separation",
                "error": sep_result["error"],
                "processing_time": round(time.time() - start_time, 2)
            }

        emo_result = self.label_emotion(sep_result["vocal_path"])
        if not emo_result["success"]:
            return {
                "success": False,
                "stage": "emotion",
                "error": emo_result["error"],
                "processing_time": round(time.time() - start_time, 2),
                "vocal_path": sep_result["vocal_path"]
            }

        return {
            "success": True,
            "stage": "completed",
            "vocal_path": sep_result["vocal_path"],
            "emotion": emo_result["emotion"],
            "confidence": emo_result["confidence"],
            "scores": emo_result["scores"],
            "processing_time": round(time.time() - start_time, 2),
            "error": None
        }


_client = None


def get_client():
    global _client
    if _client is None:
        _client = ThomasAPIClient()
    return _client


def process_audio(audio_file_path: str, output_dir: str) -> dict:
    return get_client().process_audio(audio_file_path, output_dir)
"""
Database module for Thomas Demo
Uses Supabase (PostgreSQL)
"""

import json
from supabase import create_client, Client
import config

_client: Client = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    return _client


def init_db():
    pass


def save_file(filename, original_filename, duration, sample_rate=None, file_size=None, username="anonymous"):
    db = get_client()
    result = db.table("audio_files").insert({
        "filename": filename,
        "original_filename": original_filename,
        "duration": duration,
        "sample_rate": sample_rate,
        "file_size": file_size,
        "status": "uploaded",
        "username": username
    }).execute()
    return result.data[0]["id"]


def update_file_status(file_id, status, error_message=None):
    db = get_client()
    db.table("audio_files").update({
        "status": status,
        "error_message": error_message
    }).eq("id", file_id).execute()


def save_analysis(file_id, emotion, confidence, emotion_scores, vocal_file_path, processing_time):
    db = get_client()
    db.table("analysis_results").insert({
        "audio_file_id": file_id,
        "emotion": emotion,
        "emotion_confidence": confidence,
        "emotion_scores": json.dumps(emotion_scores),
        "vocal_file_path": vocal_file_path,
        "processing_time": processing_time
    }).execute()


def upload_vocal_to_storage(local_path: str, filename: str) -> str:
    """Upload vocal file to Supabase Storage and return public URL."""
    try:
        db = get_client()
        with open(local_path, "rb") as f:
            db.storage.from_("vocals").upload(
                path=filename,
                file=f,
                file_options={"content-type": "audio/wav", "upsert": "true"}
            )
        url = db.storage.from_("vocals").get_public_url(filename)
        return url
    except Exception as e:
        return None
    db = get_client()
    db.table("dataset_clips").insert({
        "filename": filename,
        "original_filename": original_filename,
        "duration": duration,
        "emotion": emotion,
        "source": source
    }).execute()


def get_dataset_clips():
    db = get_client()
    result = db.table("dataset_clips").select("*").order("added_at", desc=True).execute()
    rows = []
    for r in result.data:
        rows.append((
            r["id"],
            r["filename"],
            r["duration"],
            r["emotion"],
            r["added_at"],
            r["source"]
        ))
    return rows


def get_dataset_stats():
    db = get_client()
    clips = db.table("dataset_clips").select("emotion, source").execute().data
    total = len(clips)
    user_contributed = sum(1 for c in clips if c["source"] == "user")
    by_emotion = {}
    for c in clips:
        if c["emotion"]:
            by_emotion[c["emotion"]] = by_emotion.get(c["emotion"], 0) + 1
    return {
        "total": total,
        "user_contributed": user_contributed,
        "by_emotion": by_emotion
    }


def get_user_files(username: str):
    db = get_client()
    result = db.table("audio_files").select(
        "id, original_filename, duration, uploaded_at, status, username, analysis_results(emotion, emotion_confidence, processing_time, vocal_file_path)"
    ).eq("username", username).order("uploaded_at", desc=True).limit(100).execute()

    rows = []
    for r in result.data:
        ar = r.get("analysis_results")
        if isinstance(ar, list):
            ar = ar[0] if ar else None
        rows.append((
            r["id"],
            r["original_filename"],
            r["duration"],
            r["uploaded_at"],
            r["status"],
            ar["emotion"] if ar else None,
            ar["emotion_confidence"] if ar else None,
            ar["processing_time"] if ar else None,
            ar["vocal_file_path"] if ar else None,
        ))
    return rows


def get_user_stats(username: str):
    db = get_client()

    files = db.table("audio_files").select(
        "status, duration, uploaded_at"
    ).eq("username", username).execute().data

    file_ids = db.table("audio_files").select("id").eq("username", username).execute().data
    ids = [f["id"] for f in file_ids]

    analyses = []
    if ids:
        analyses = db.table("analysis_results").select(
            "emotion, processing_time, processed_at"
        ).in_("audio_file_id", ids).execute().data

    total_files = len(files)
    processed = sum(1 for f in files if f["status"] == "completed")
    errors = sum(1 for f in files if f["status"] == "error")

    durations = [f["duration"] for f in files if f["duration"]]
    avg_duration = round(sum(durations) / len(durations), 2) if durations else 0

    times = [a["processing_time"] for a in analyses if a["processing_time"]]
    avg_processing_time = round(sum(times) / len(times), 2) if times else 0

    emotion_distribution = {}
    for a in analyses:
        if a["emotion"]:
            emotion_distribution[a["emotion"]] = emotion_distribution.get(a["emotion"], 0) + 1

    return {
        "total_files": total_files,
        "processed": processed,
        "errors": errors,
        "avg_processing_time": avg_processing_time,
        "avg_duration": avg_duration,
        "emotion_distribution": emotion_distribution,
        "analyses": analyses,
        "files": files
    }


def get_all_files():
    db = get_client()
    result = db.table("audio_files").select(
        "id, original_filename, duration, uploaded_at, status, username, analysis_results(emotion, emotion_confidence, processing_time)"
    ).order("uploaded_at", desc=True).limit(100).execute()

    rows = []
    for r in result.data:
        ar = r.get("analysis_results")
        if isinstance(ar, list):
            ar = ar[0] if ar else None
        rows.append((
            r["id"],
            r["original_filename"],
            r["duration"],
            r["uploaded_at"],
            r["status"],
            ar["emotion"] if ar else None,
            ar["emotion_confidence"] if ar else None,
            ar["processing_time"] if ar else None,
        ))
    return rows


def get_stats():
    db = get_client()
    files = db.table("audio_files").select("status, duration").execute().data
    analyses = db.table("analysis_results").select("emotion, processing_time").execute().data

    total_files = len(files)
    processed = sum(1 for f in files if f["status"] == "completed")
    errors = sum(1 for f in files if f["status"] == "error")

    durations = [f["duration"] for f in files if f["duration"]]
    avg_duration = round(sum(durations) / len(durations), 2) if durations else 0

    times = [a["processing_time"] for a in analyses if a["processing_time"]]
    avg_processing_time = round(sum(times) / len(times), 2) if times else 0

    emotion_distribution = {}
    for a in analyses:
        if a["emotion"]:
            emotion_distribution[a["emotion"]] = emotion_distribution.get(a["emotion"], 0) + 1

    return {
        "total_files": total_files,
        "processed": processed,
        "errors": errors,
        "avg_processing_time": avg_processing_time,
        "avg_duration": avg_duration,
        "emotion_distribution": emotion_distribution
    }


def get_recent_results(limit=10):
    db = get_client()
    result = db.table("analysis_results").select(
        "processing_time, emotion, emotion_confidence, audio_files(original_filename, duration, uploaded_at)"
    ).order("processed_at", desc=True).limit(limit).execute()

    rows = []
    for r in result.data:
        af = r.get("audio_files") or {}
        rows.append((
            af.get("original_filename", "—"),
            af.get("duration", 0),
            af.get("uploaded_at", ""),
            r["emotion"],
            r["emotion_confidence"],
            r["processing_time"]
        ))
    return rows

def add_to_dataset(filename, original_filename, duration, emotion=None, source="user"):
    db = get_client()
    db.table("dataset_clips").insert({
        "filename": filename,
        "original_filename": original_filename,
        "duration": duration,
        "emotion": emotion,
        "source": source
    }).execute()

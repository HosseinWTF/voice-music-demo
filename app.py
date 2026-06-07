"""
Thomas - Voice-Music Separation & Emotion Labeling
Capstone Project Demo
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
import config
import database
import audio_utils
import processor

TZ_OFFSET = timedelta(hours=3)

def fmt_date(ts: str) -> str:
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        local = dt + TZ_OFFSET
        return local.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts[:16].replace("T", " ")

st.set_page_config(
    page_title="Thomas",
    page_icon="🎵",
    layout="wide",
    menu_items={}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg:       #0a0b0f;
    --surface:  #111318;
    --surface2: #1a1d27;
    --border:   #22263a;
    --accent:   #6ee7b7;
    --accent2:  #818cf8;
    --text:     #e2e8f0;
    --muted:    #4a5568;
    --mono:     'Space Mono', monospace;
    --sans:     'Inter', sans-serif;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

.block-container {
    max-width: 1080px !important;
    padding: 2.5rem 2rem 5rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #0a0b0f !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    letter-spacing: 0.04em !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.8 !important; }

/* Sign out button special style */
.signout-btn .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.78rem !important;
}
.signout-btn .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    opacity: 1 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-size: 1.9rem !important;
}

/* ── Audio ── */
audio { width: 100% !important; border-radius: 8px !important; }

/* ── Progress ── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 4px !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.8rem 0 !important; }

/* ── Table ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
}
.card-accent { border-left: 3px solid var(--accent); }

/* ── Emotion pill ── */
.emotion-pill {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 999px;
    font-family: var(--mono);
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}

/* ── Page title ── */
.page-title {
    font-family: var(--mono);
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.01em;
}
.page-subtitle {
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: -0.1rem;
    margin-bottom: 1.8rem;
}

/* ── Waveform ── */
.waveform-wrap { display: flex; align-items: center; gap: 2px; height: 52px; }
.waveform-bar { flex: 1; background: var(--accent); border-radius: 2px; opacity: 0.6; }

/* ── Score bars ── */
.score-row { display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 3px; }
.score-track { height: 4px; background: var(--surface2); border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem; }

/* ── Nav item ── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.55rem 0.8rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
    margin-bottom: 0.2rem;
    text-decoration: none;
}
.nav-item:hover { background: var(--surface2); color: var(--text); }
.nav-item.active { background: var(--surface2); color: var(--accent); }

/* ── User chip ── */
.user-chip {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.8rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 1.2rem;
}
.user-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    color: #0a0b0f;
    flex-shrink: 0;
}

/* ── Upload hint ── */
.upload-hint {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}
.hint-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--muted);
}
.hint-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    opacity: 0.6;
    flex-shrink: 0;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: 8px !important;
    padding: 3px !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: var(--muted) !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


def init_app():
    Path(config.UPLOAD_DIR).mkdir(exist_ok=True)
    Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
    Path(config.DATASET_DIR).mkdir(exist_ok=True)
    database.init_db()


def waveform(values: list[float]):
    bars = "".join(
        f'<div class="waveform-bar" style="height:{max(3, int(v * 52))}px;"></div>'
        for v in values[:80]
    )
    st.markdown(
        f'<div class="card" style="padding:0.7rem 1rem;"><div class="waveform-wrap">{bars}</div></div>',
        unsafe_allow_html=True
    )


def emotion_result(emotion: str, confidence: float, scores: dict):
    cfg = config.EMOTION_LABELS.get(emotion, {"label": emotion.title(), "emoji": "🎙️", "color": "#6ee7b7"})
    c = cfg["color"]
    st.markdown(
        f"""
        <div class="card card-accent" style="text-align:center; padding:2rem 1rem;">
            <div style="font-size:3.2rem; margin-bottom:0.5rem;">{cfg['emoji']}</div>
            <div class="emotion-pill" style="background:{c}15; color:{c}; border:1.5px solid {c}35;">
                {cfg['label'].upper()}
            </div>
            <div style="margin-top:0.7rem; color:var(--muted); font-size:0.78rem; font-family:'Space Mono',monospace; letter-spacing:0.04em;">
                {confidence*100:.1f}% confidence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if scores:
        st.markdown('<div style="font-size:0.78rem; color:var(--muted); letter-spacing:0.06em; text-transform:uppercase; margin:0.8rem 0 0.5rem;">Score breakdown</div>', unsafe_allow_html=True)
        for key, val in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            info = config.EMOTION_LABELS.get(key, {"label": key.title(), "color": "#6ee7b7"})
            pct = val * 100
            st.markdown(
                f"""
                <div class="score-row">
                    <span style="color:var(--text);">{info['label']}</span>
                    <span style="color:var(--muted); font-family:monospace;">{pct:.1f}%</span>
                </div>
                <div class="score-track">
                    <div style="height:100%; width:{pct}%; background:{info['color']};"></div>
                </div>
                """,
                unsafe_allow_html=True
            )


@st.dialog("Contribute to Dataset")
def consent_dialog(file_info: dict, emotion: str = None):
    st.markdown(
        """
        <div style="font-size:0.92rem; line-height:1.75; margin-bottom:1.2rem; color:var(--text);">
            Would you like to contribute your audio file to our research dataset?
            <br><br>
            This file will be added to our shared collection of labeled audio clips
            used to train and evaluate our emotion recognition models.
            <br><br>
            <span style="color:#4a5568; font-size:0.8rem;">
                Your file will only be used for academic research purposes within this capstone project.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, contribute", use_container_width=True):
            dataset_filename = f"user_{Path(file_info['filename']).name}"
            dataset_path = Path(config.DATASET_DIR) / dataset_filename
            shutil.copy2(file_info["path"], dataset_path)
            database.add_to_dataset(
                filename=dataset_filename,
                original_filename=file_info["original_filename"],
                duration=file_info["duration"],
                emotion=emotion,
                source="user"
            )
            st.success("Thank you for contributing to our research dataset! 🎙️")
    with col2:
        if st.button("❌ No, skip", use_container_width=True):
            st.info("No problem! Thank you for using Thomas. 👋")


def page_upload():
    st.markdown('<div class="page-title">THOMAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Voice-Music Separation &amp; Emotion Labeling</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-hint">
        <div class="hint-item"><div class="hint-dot"></div>WAV, MP3, MP4, M4A, OGG, FLAC, AAC, MPEG</div>
        <div class="hint-item"><div class="hint-dot"></div>3 – 15 seconds</div>
        <div class="hint-item"><div class="hint-dot"></div>Min 16kHz · Mono</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your audio file here or click to browse",
        type=["wav", "mp3", "mp4", "m4a", "ogg", "flac", "aac", "mpeg", "mpga"],
        label_visibility="visible"
    )

    if uploaded_file is None:
        return

    is_valid, result = audio_utils.validate_and_save(uploaded_file, config.UPLOAD_DIR)
    if not is_valid:
        st.error(result)
        return

    file_info = result

    if st.session_state.get("last_uploaded") != file_info["filename"]:
        st.session_state["last_result"] = None
        st.session_state["consent_done"] = False
        st.session_state["last_uploaded"] = file_info["filename"]

    st.success(f"✓ {file_info['original_filename']} — validated")

    waveform(audio_utils.get_waveform_data(file_info["path"]))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Duration", audio_utils.format_duration(file_info["duration"]))
    c2.metric("Sample Rate", f"{file_info['sample_rate'] // 1000}kHz")
    c3.metric("File Size", audio_utils.format_file_size(file_info["file_size"]))
    c4.metric("Channel", "Mono")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🎵 Listen to original"):
        st.audio(file_info["path"], format="audio/wav")

    file_id = database.save_file(
        filename=file_info["filename"],
        original_filename=file_info["original_filename"],
        duration=file_info["duration"],
        sample_rate=file_info["sample_rate"],
        file_size=file_info["file_size"],
        username=st.session_state.get("user").email if st.session_state.get("user") else "anonymous"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.button("⚙️ Process Audio", type="primary", use_container_width=True):
        return

    database.update_file_status(file_id, "processing")
    bar = st.progress(0, text="Starting…")
    msg = st.empty()

    msg.info("Separating vocals…")
    bar.progress(20, text="Running separation model…")

    result = processor.process_audio(file_info["path"], config.OUTPUT_DIR)
    bar.progress(60, text="Classifying emotion…")

    if not result["success"]:
        bar.progress(100)
        msg.error(f"Failed at {result['stage']}: {result['error']}")
        database.update_file_status(file_id, "error", result["error"])
        return

    bar.progress(85, text="Saving…")
    vocal_filename = Path(result["vocal_path"]).name
    vocal_url = database.upload_vocal_to_storage(result["vocal_path"], vocal_filename)
    database.save_analysis(
        file_id=file_id,
        emotion=result["emotion"],
        confidence=result["confidence"],
        emotion_scores=result["scores"],
        vocal_file_path=vocal_url or result["vocal_path"],
        processing_time=result["processing_time"]
    )
    database.update_file_status(file_id, "completed")
    bar.progress(100, text="Done")
    msg.empty()

    st.markdown("---")

    if result["confidence"] and result["confidence"] < 0.50:
        st.warning(
            f"⚠️ Low confidence ({result['confidence']*100:.0f}%) — the model is uncertain. "
            "The audio may contain heavy background noise or unclear speech."
        )

    st.markdown("### Results")
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("#### Emotion")
        emotion_result(result["emotion"], result["confidence"], result["scores"])
        st.caption(f"Processed in {result['processing_time']}s")

    with right:
        st.markdown("#### Separated Vocals")
        vocal_src = vocal_url or result["vocal_path"]
        st.audio(vocal_src, format="audio/wav")
        if vocal_url:
            st.markdown(f"[⬇️ Download vocal track]({vocal_url})")
        else:
            with open(result["vocal_path"], "rb") as f:
                st.download_button(
                    "⬇️ Download vocal track",
                    data=f,
                    file_name=f"vocal_{file_info['original_filename']}",
                    mime="audio/wav",
                    use_container_width=True
                )

    st.markdown("---")
    consent_dialog(file_info, emotion=result.get("emotion"))


def page_dashboard():
    import pandas as pd

    user = st.session_state.get("user")
    user_id = user.email if user else "anonymous"
    username = st.session_state.get("username", user_id.split("@")[0])

    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Your Analysis History — {username}</div>', unsafe_allow_html=True)

    stats = database.get_user_stats(user_id)

    c1, c2 = st.columns(2)
    c1.metric("Total Uploads", stats["processed"])
    c2.metric("Avg. Process Time", f"{stats['avg_processing_time']}s" if stats["avg_processing_time"] else "—")

    st.markdown("---")

    emo_dist = stats.get("emotion_distribution", {})
    analyses = stats.get("analyses", [])

    if not emo_dist:
        st.markdown(
            '<div class="card" style="text-align:center; padding:2.5rem; color:var(--muted);">'
            '🎙️ No analyses yet. Upload and process an audio file to see your dashboard.'
            '</div>',
            unsafe_allow_html=True
        )
        return

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("#### Emotion Distribution")
        import plotly.express as px
        emo_df = pd.DataFrame([
            {
                "Emotion": f"{config.EMOTION_LABELS.get(k, {'emoji': ''})['emoji']} {config.EMOTION_LABELS.get(k, {'label': k.title()})['label']}",
                "Count": v,
                "Color": config.EMOTION_LABELS.get(k, {"color": "#6ee7b7"})["color"]
            }
            for k, v in sorted(emo_dist.items(), key=lambda x: x[1], reverse=True)
        ])
        fig = px.pie(
            emo_df, names="Emotion", values="Count",
            color="Emotion",
            color_discrete_sequence=emo_df["Color"].tolist(),
            height=320, hole=0.45
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#e2e8f0", size=12))
        )
        fig.update_traces(textfont_color="#0a0b0f", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Score Breakdown")
        total_emo = sum(emo_dist.values())
        for key, count in sorted(emo_dist.items(), key=lambda x: x[1], reverse=True):
            info = config.EMOTION_LABELS.get(key, {"label": key.title(), "emoji": "🎙️", "color": "#6ee7b7"})
            pct = (count / total_emo) * 100
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.7rem;">
                    <span style="font-size:1.3rem; width:28px; text-align:center;">{info.get('emoji','')}</span>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="font-size:0.82rem; color:var(--text);">{info['label']}</span>
                            <span style="font-size:0.78rem; color:var(--muted); font-family:monospace;">{count} · {pct:.0f}%</span>
                        </div>
                        <div style="height:5px; background:var(--surface2); border-radius:3px; overflow:hidden;">
                            <div style="height:100%; width:{pct}%; background:{info['color']}; border-radius:3px;"></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("#### Upload History")
    user_files = database.get_user_files(user_id)
    completed = [f for f in user_files if f[4] == "completed"]
    if completed:
        rows = []
        for fid, fname, dur, ts, status, emotion, conf, proc, vocal_path in completed:
            info = config.EMOTION_LABELS.get(emotion, {"label": emotion or "—", "emoji": ""}) if emotion else {"label": "—", "emoji": ""}
            rows.append({
                "File": fname,
                "Duration": audio_utils.format_duration(dur),
                "Emotion": f"{info.get('emoji','')} {info['label']}",
                "Confidence": f"{conf*100:.0f}%" if conf else "—",
                "Process Time": f"{proc:.1f}s" if proc else "—",
                "Date": fmt_date(ts)
            })
        sel = st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        selected = sel.selection.rows
        if selected:
            idx = selected[0]
            _, fname, dur, ts, _, emotion, conf, proc, vocal_path = completed[idx]
            info = config.EMOTION_LABELS.get(emotion, {"label": emotion or "—", "emoji": "🎙️", "color": "#6ee7b7"}) if emotion else {"label": "—", "emoji": "🎙️", "color": "#6ee7b7"}
            st.markdown(
                f"""
                <div class="card card-accent" style="margin-top:0.8rem;">
                    <div style="font-size:0.72rem; color:var(--muted); margin-bottom:0.5rem; letter-spacing:0.04em;">SELECTED · {fname}</div>
                    <div style="display:flex; align-items:center; gap:0.8rem;">
                        <span style="font-size:1.5rem;">{info.get('emoji','')}</span>
                        <span style="font-family:'Space Mono',monospace; color:{info['color']}; font-weight:700; font-size:1rem;">{info['label'].upper()}</span>
                        <span style="color:var(--muted); font-size:0.78rem;">{f"{conf*100:.0f}% confidence" if conf else ""}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if vocal_path and vocal_path.startswith("http"):
                st.markdown("**🎙️ Separated Vocal Track**")
                st.audio(vocal_path, format="audio/wav")
                st.markdown(f"[⬇️ Download vocal]({vocal_path})")
            elif vocal_path and Path(vocal_path).exists():
                st.markdown("**🎙️ Separated Vocal Track**")
                st.audio(vocal_path, format="audio/wav")
            else:
                st.caption("Vocal file not available.")
    else:
        st.markdown(
            '<div class="card" style="text-align:center; padding:1.5rem; color:var(--muted); font-size:0.85rem;">No completed analyses yet.</div>',
            unsafe_allow_html=True
        )


def page_dataset():
    st.markdown('<div class="page-title">Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Shared Audio Clip Collection</div>', unsafe_allow_html=True)

    ds_stats = database.get_dataset_stats()

    c1, c2 = st.columns(2)
    c1.metric("Total Clips", ds_stats["total"])
    c2.metric("User Contributed", ds_stats["user_contributed"])

    st.markdown("---")
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown("#### Emotion Breakdown")
        by_emotion = ds_stats.get("by_emotion", {})
        if by_emotion:
            total_labeled = sum(by_emotion.values())
            for emo, count in sorted(by_emotion.items(), key=lambda x: x[1], reverse=True):
                info = config.EMOTION_LABELS.get(emo, {"label": emo.title(), "emoji": "🎙️", "color": "#6ee7b7"})
                pct = (count / total_labeled) * 100
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.7rem;">
                        <span style="font-size:1.1rem; width:24px; text-align:center;">{info.get('emoji','')}</span>
                        <div style="flex:1;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                                <span style="font-size:0.8rem; color:var(--text);">{info['label']}</span>
                                <span style="font-size:0.75rem; color:var(--muted); font-family:monospace;">{count}</span>
                            </div>
                            <div style="height:5px; background:var(--surface2); border-radius:3px; overflow:hidden;">
                                <div style="height:100%; width:{pct}%; background:{info['color']}; border-radius:3px;"></div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.caption("No labeled clips yet.")

    with right:
        clips = database.get_dataset_clips()
        if not clips:
            st.markdown(
                '<div class="card" style="text-align:center; padding:2rem; color:var(--muted);">No clips in dataset yet.</div>',
                unsafe_allow_html=True
            )
        else:
            import pandas as pd
            preloaded = [c for c in clips if c[5] == "preloaded"]
            user_clips = [c for c in clips if c[5] == "user"]

            def clips_to_df(clip_list):
                rows = []
                for cid, fname, dur, emotion, added_at, source in clip_list:
                    info = config.EMOTION_LABELS.get(emotion, {"label": emotion or "—", "emoji": ""}) if emotion else {"label": "—", "emoji": ""}
                    rows.append({
                        "File": fname,
                        "Duration": audio_utils.format_duration(dur) if dur else "—",
                        "Emotion": f"{info.get('emoji','')} {info['label']}",
                        "Added": fmt_date(added_at)
                    })
                return pd.DataFrame(rows)

            tab1, tab2 = st.tabs([f"📁 Pre-loaded ({len(preloaded)})", f"👤 User Contributed ({len(user_clips)})"])

            with tab1:
                if preloaded:
                    sel = st.dataframe(clips_to_df(preloaded), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
                    selected = sel.selection.rows
                    if selected:
                        clip = preloaded[selected[0]]
                        clip_path = Path(config.DATASET_DIR) / clip[1]
                        if clip_path.exists():
                            st.markdown(f"**Now playing:** `{clip[1]}`")
                            st.audio(str(clip_path), format="audio/wav")
                        else:
                            st.caption("File not found on disk.")
                else:
                    st.caption("No pre-loaded clips yet.")

            with tab2:
                if user_clips:
                    sel2 = st.dataframe(clips_to_df(user_clips), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
                    selected2 = sel2.selection.rows
                    if selected2:
                        clip2 = user_clips[selected2[0]]
                        clip_path2 = Path(config.DATASET_DIR) / clip2[1]
                        if clip_path2.exists():
                            st.markdown(f"**Now playing:** `{clip2[1]}`")
                            st.audio(str(clip_path2), format="audio/wav")
                        else:
                            st.caption("File not found on disk.")
                else:
                    st.caption("No user contributions yet.")


def page_auth():
    col, _ = st.columns([1, 1.2])
    with col:
        st.markdown('<div class="page-title" style="margin-bottom:0.3rem;">THOMAS</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Voice-Music Separation & Emotion Labeling</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        db = database.get_client()
                        res = db.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["user"] = res.user
                        st.session_state["username"] = res.user.email.split("@")[0]
                        st.rerun()
                    except Exception:
                        st.error("Invalid email or password.")

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min. 6 characters")
            reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                elif reg_password != reg_password2:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        db = database.get_client()
                        res = db.auth.sign_up({"email": reg_email, "password": reg_password})
                        st.session_state["user"] = res.user
                        st.session_state["username"] = res.user.email.split("@")[0]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not create account: {e}")


def render_sidebar(username: str, page: str) -> str:
    with st.sidebar:
        # Logo
        st.markdown(
            '<div style="padding:0.5rem 0 1.2rem;">'
            '<div style="font-family:\'Space Mono\',monospace; font-size:1.1rem; font-weight:700; '
            'background:linear-gradient(90deg,#6ee7b7,#818cf8); -webkit-background-clip:text; '
            '-webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-0.01em;">THOMAS</div>'
            '<div style="font-size:0.65rem; color:#4a5568; letter-spacing:0.1em; text-transform:uppercase; margin-top:1px;">v0.1 · Capstone</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # User chip
        initials = username[:2].upper() if username else "?"
        st.markdown(
            f'<div class="user-chip">'
            f'<div class="user-avatar">{initials}</div>'
            f'<div>'
            f'<div style="font-size:0.8rem; font-weight:500; color:var(--text);">{username}</div>'
            f'<div style="font-size:0.68rem; color:var(--muted);">Signed in</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div style="font-size:0.65rem; color:#4a5568; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.5rem;">Navigation</div>', unsafe_allow_html=True)

        selected = st.radio(
            "nav",
            ["⬆️ Upload & Process", "🗄️ Dataset", "📊 Dashboard"],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="border-top:1px solid var(--border); margin-bottom:1rem;"></div>', unsafe_allow_html=True)

        # Sign out
        st.markdown('<div class="signout-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            del st.session_state["user"]
            del st.session_state["username"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.68rem; color:#4a5568; line-height:1.8; margin-top:1.5rem;">'
            'Streamlit · Supabase · PyTorch<br>Demucs · Wav2Vec2 · Librosa'
            '</div>',
            unsafe_allow_html=True
        )

    return selected


def main():
    init_app()

    if "user" not in st.session_state:
        page_auth()
        return

    user = st.session_state["user"]
    username = st.session_state.get("username", user.email.split("@")[0])

    page = render_sidebar(username, "")

    if page == "⬆️ Upload & Process":
        page_upload()
    elif page == "🗄️ Dataset":
        page_dataset()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
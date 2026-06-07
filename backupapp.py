"""
Thomas - Voice-Music Separation & Emotion Labeling
Capstone Project Demo
"""

import os
import json
import time
from pathlib import Path
import streamlit as st
import backupconfig
import database
import audio_utils
import api_client

# ─────────────────────────────────────────
# Page config (MUST be first Streamlit call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title=backupconfig.APP_TITLE,
    page_icon="🎙️",
    layout="wide",
    menu_items={}
)

# ─────────────────────────────────────────
# Custom CSS — dark, refined aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0c0e13;
    --surface:   #13161e;
    --surface2:  #1c2030;
    --border:    #2a2f42;
    --accent:    #6ee7b7;
    --accent2:   #818cf8;
    --text:      #e2e8f0;
    --text-muted:#64748b;
    --danger:    #f87171;
    --warning:   #fbbf24;
    --mono:      'Space Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

/* ── Global overrides ── */
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

.block-container {
    max-width: 1100px !important;
    padding: 2rem 2rem 4rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #0c0e13 !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-size: 1.8rem !important;
}

/* ── Alerts ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 8px !important;
    font-family: var(--sans) !important;
}

/* ── Audio player ── */
audio {
    width: 100% !important;
    border-radius: 8px !important;
    background: var(--surface2) !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Tables / dataframes ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ── Radio / selectbox ── */
.stRadio label, .stSelectbox label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}

/* ── Custom card component ── */
.thomas-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}

.thomas-card-accent {
    border-left: 3px solid var(--accent);
}

/* ── Emotion badge ── */
.emotion-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-family: var(--mono);
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Logo / title ── */
.thomas-logo {
    font-family: var(--mono);
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.thomas-sub {
    color: var(--text-muted);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: -0.3rem;
}

/* ── Waveform bars ── */
.waveform-container {
    display: flex;
    align-items: center;
    gap: 2px;
    height: 60px;
    padding: 0.5rem 0;
}

.waveform-bar {
    flex: 1;
    background: var(--accent);
    border-radius: 2px;
    opacity: 0.7;
    transition: height 0.3s ease;
}

/* ── Step indicator ── */
.step-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.5rem 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}

.step-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--border);
    flex-shrink: 0;
}

.step-dot.active {
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}

.step-dot.done {
    background: var(--accent2);
}

.step-label.active {
    color: var(--text);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Init
# ─────────────────────────────────────────
def init_app():
    Path(backupconfig.UPLOAD_DIR).mkdir(exist_ok=True)
    Path(backupconfig.OUTPUT_DIR).mkdir(exist_ok=True)
    database.init_db()


# ─────────────────────────────────────────
# Helpers — custom UI components
# ─────────────────────────────────────────
def render_waveform(values: list[float]):
    bars = ""
    for v in values[:80]:
        h = max(4, int(v * 56))
        bars += f'<div class="waveform-bar" style="height:{h}px;"></div>'
    st.markdown(
        f'<div class="thomas-card"><div class="waveform-container">{bars}</div></div>',
        unsafe_allow_html=True
    )


def render_emotion_result(emotion: str, confidence: float, scores: dict):
    info = backupconfig.EMOTION_LABELS.get(emotion, {"label": emotion.title(), "emoji": "🎙️", "color": "#6ee7b7"})
    color = info["color"]

    # Main badge
    st.markdown(
        f"""
        <div class="thomas-card thomas-card-accent" style="text-align:center; padding: 2rem;">
            <div style="font-size:3.5rem; margin-bottom:0.5rem;">{info['emoji']}</div>
            <div class="emotion-badge" style="background:{color}22; color:{color}; border:1.5px solid {color};">
                {info['label'].upper()}
            </div>
            <div style="margin-top:0.8rem; color:var(--text-muted); font-size:0.85rem; font-family:'Space Mono',monospace;">
                Güven: %{confidence*100:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Score bars
    if scores:
        st.markdown("**Duygu Dağılımı**")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for emo_key, score in sorted_scores:
            emo_info = backupconfig.EMOTION_LABELS.get(emo_key, {"label": emo_key.title(), "color": "#6ee7b7"})
            pct = score * 100
            st.markdown(
                f"""
                <div style="margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;">
                        <span style="color:var(--text);">{emo_info['label']}</span>
                        <span style="color:var(--text-muted); font-family:monospace;">%{pct:.1f}</span>
                    </div>
                    <div style="height:6px; background:var(--surface2); border-radius:4px; overflow:hidden;">
                        <div style="height:100%; width:{pct}%; background:{emo_info['color']}; border-radius:4px; transition:width 0.5s;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_processing_steps(stage: str):
    """Display animated processing steps."""
    steps = [
        ("separation", "Müzik & Vokal Ayrıştırma"),
        ("emotion", "Duygu Etiketleme"),
        ("saving", "Sonuçlar Kaydediliyor"),
    ]
    html = ""
    for key, label in steps:
        if stage == key:
            dot_cls = "active"
            label_cls = "active"
        elif steps.index((key, label)) < [s[0] for s in steps].index(stage) if stage in [s[0] for s in steps] else False:
            dot_cls = "done"
            label_cls = ""
        else:
            dot_cls = ""
            label_cls = ""
        html += f'<div class="step-row"><div class="step-dot {dot_cls}"></div><span class="step-label {label_cls}">{label}</span></div>'

    st.markdown(f'<div class="thomas-card">{html}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# Pages
# ─────────────────────────────────────────
def page_upload():
    # Header
    st.markdown('<div class="thomas-logo">THOMAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="thomas-sub">Voice-Music Separation &amp; Emotion Labeling</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # API status
    client = api_client.get_client()
    api_alive = client.health_check()
    if api_alive:
        st.success("TorchServe API bağlantısı aktif", icon="🟢")
    else:
        st.warning(
            "TorchServe API şu anda erişilemiyor. Bağlantı kurulduğunda işlem yapabilirsiniz.",
            icon="🟡"
        )

    st.markdown("---")

    # Upload area
    col_up, col_info = st.columns([3, 2], gap="large")

    with col_up:
        st.markdown("#### Ses Dosyası Yükle")
        uploaded_file = st.file_uploader(
            f".wav formatı · {backupconfig.MIN_DURATION}–{backupconfig.MAX_DURATION} saniye · min {backupconfig.MIN_SAMPLE_RATE // 1000}kHz Mono",
            type=["wav"],
            label_visibility="visible"
        )

    with col_info:
        st.markdown("#### Nasıl Çalışır?")
        st.markdown("""
        <div class="thomas-card" style="font-size:0.88rem; line-height:1.8;">
            <span style="color:var(--accent); font-family:'Space Mono',monospace;">01</span> &nbsp;Ses dosyasını yükle<br>
            <span style="color:var(--accent); font-family:'Space Mono',monospace;">02</span> &nbsp;Müzik & vokal ayrıştırılır<br>
            <span style="color:var(--accent); font-family:'Space Mono',monospace;">03</span> &nbsp;Vokaldeki duygu etiketlenir<br>
            <span style="color:var(--accent); font-family:'Space Mono',monospace;">04</span> &nbsp;Sonuçlar ve temiz ses sunulur
        </div>
        """, unsafe_allow_html=True)

    # File processing
    if uploaded_file is not None:
        is_valid, result = audio_utils.validate_and_save(uploaded_file, backupconfig.UPLOAD_DIR)

        if not is_valid:
            st.error(result)
            return

        file_info = result
        st.success(f"✓ Dosya doğrulandı — {file_info['original_filename']}")

        # Waveform
        waveform = audio_utils.get_waveform_data(file_info["path"])
        render_waveform(waveform)

        # File metadata row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Süre", f"{audio_utils.format_duration(file_info['duration'])}")
        c2.metric("Örnekleme Hz", f"{file_info['sample_rate'] // 1000}kHz")
        c3.metric("Boyut", audio_utils.format_file_size(file_info["file_size"]))
        c4.metric("Kanal", "Mono")

        st.markdown("<br>", unsafe_allow_html=True)

        # Playback of original
        with st.expander("🎵 Orijinal Ses Dosyasını Dinle"):
            st.audio(file_info["path"], format="audio/wav")

        # Save to DB
        file_id = database.save_file(
            filename=file_info["filename"],
            original_filename=file_info["original_filename"],
            duration=file_info["duration"],
            sample_rate=file_info["sample_rate"],
            file_size=file_info["file_size"]
        )

        st.markdown("---")

        # Process button
        if not api_alive:
            st.button("⚙️ Sesi İşle", disabled=True, use_container_width=True)
            st.caption("TorchServe API bağlantısı bekleniyor...")
        else:
            if st.button("⚙️ Sesi İşle", type="primary", use_container_width=True):
                database.update_file_status(file_id, "processing")

                progress_bar = st.progress(0, text="Başlatılıyor...")
                status_box = st.empty()

                # Step 1: Separation
                status_box.info("🎼 Müzik ve vokal ayrıştırılıyor...")
                progress_bar.progress(20, text="Ayrıştırma modeli çalışıyor...")
                time.sleep(0.3)  # visual delay

                result = client.process_audio(file_info["path"], backupconfig.OUTPUT_DIR)
                progress_bar.progress(60, text="Duygu analizi yapılıyor...")

                if not result["success"]:
                    progress_bar.progress(100)
                    status_box.error(f"İşlem hatası ({result['stage']}): {result['error']}")
                    database.update_file_status(file_id, "error", result["error"])
                    return

                # Step 3: Save results
                progress_bar.progress(85, text="Sonuçlar kaydediliyor...")
                database.save_analysis(
                    file_id=file_id,
                    emotion=result["emotion"],
                    confidence=result["confidence"],
                    emotion_scores=result["scores"],
                    vocal_file_path=result["vocal_path"],
                    processing_time=result["processing_time"]
                )
                database.update_file_status(file_id, "completed")

                progress_bar.progress(100, text="Tamamlandı!")
                status_box.empty()

                # ── Results ──
                st.markdown("### Sonuçlar")

                res_col1, res_col2 = st.columns([1, 1], gap="large")

                with res_col1:
                    st.markdown("#### Duygu Analizi")
                    render_emotion_result(result["emotion"], result["confidence"], result["scores"])
                    st.caption(f"İşlem süresi: {result['processing_time']}s")

                with res_col2:
                    st.markdown("#### Ayrıştırılmış Vokal")
                    st.markdown(
                        '<div class="thomas-card thomas-card-accent">Müzikten arındırılmış vokal kaydı</div>',
                        unsafe_allow_html=True
                    )
                    st.audio(result["vocal_path"], format="audio/wav")

                    with open(result["vocal_path"], "rb") as f:
                        st.download_button(
                            "⬇️ Vokal Dosyasını İndir",
                            data=f,
                            file_name=f"vocal_{file_info['original_filename']}",
                            mime="audio/wav",
                            use_container_width=True
                        )


def page_dashboard():
    st.markdown('<div class="thomas-logo">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="thomas-sub">Analiz İstatistikleri & Geçmiş</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    stats = database.get_stats()

    # KPI row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Toplam Dosya", stats["total_files"])
    kpi2.metric("İşlenen", stats["processed"])
    kpi3.metric("Hata", stats["errors"])
    avg_time = stats["avg_processing_time"]
    kpi4.metric("Ort. Süre", f"{avg_time}s" if avg_time else "—")
    kpi5.metric("Ort. Kayıt", f"{stats['avg_duration']}s" if stats["avg_duration"] else "—")

    st.markdown("---")

    col_emo, col_hist = st.columns([1, 2], gap="large")

    with col_emo:
        st.markdown("#### Duygu Dağılımı")
        emo_dist = stats.get("emotion_distribution", {})

        if emo_dist:
            total = sum(emo_dist.values())
            for emo_key, count in sorted(emo_dist.items(), key=lambda x: x[1], reverse=True):
                info = backupconfig.EMOTION_LABELS.get(emo_key, {"label": emo_key.title(), "emoji": "🎙️", "color": "#6ee7b7"})
                pct = (count / total) * 100
                st.markdown(
                    f"""
                    <div style="margin-bottom:0.8rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <span>{info.get('emoji','')} {info['label']}</span>
                            <span style="color:var(--text-muted); font-family:monospace; font-size:0.8rem;">{count} kayıt</span>
                        </div>
                        <div style="height:8px; background:var(--surface2); border-radius:4px; overflow:hidden;">
                            <div style="height:100%; width:{pct}%; background:{info['color']}; border-radius:4px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div class="thomas-card" style="color:var(--text-muted); font-size:0.9rem;">Henüz işlenmiş kayıt yok.</div>',
                unsafe_allow_html=True
            )

    with col_hist:
        st.markdown("#### Son Analizler")
        recent = database.get_recent_results(limit=10)

        if recent:
            import pandas as pd
            rows = []
            for r in recent:
                fname, dur, uploaded_at, emotion, confidence, proc_time = r
                emo_info = backupconfig.EMOTION_LABELS.get(emotion, {"label": emotion or "—", "emoji": ""})
                rows.append({
                    "Dosya": fname,
                    "Süre": f"{audio_utils.format_duration(dur)}",
                    "Duygu": f"{emo_info.get('emoji','')} {emo_info['label']}",
                    "Güven": f"%{confidence*100:.0f}" if confidence else "—",
                    "İşlem (s)": f"{proc_time:.1f}" if proc_time else "—",
                    "Tarih": uploaded_at[:16].replace("T", " ") if uploaded_at else "—"
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                '<div class="thomas-card" style="color:var(--text-muted); font-size:0.9rem;">Henüz tamamlanan analiz yok.</div>',
                unsafe_allow_html=True
            )

    # Full upload history
    st.markdown("---")
    st.markdown("#### Tüm Yüklemeler")

    all_files = database.get_all_files()
    if all_files:
        import pandas as pd
        status_map = {
            "uploaded": "⬆️ Yüklendi",
            "processing": "⚙️ İşleniyor",
            "completed": "✅ Tamamlandı",
            "error": "❌ Hata"
        }
        rows = []
        for row in all_files:
            fid, fname, dur, uploaded_at, status, emotion, confidence, proc_time = row
            emo_info = backupconfig.EMOTION_LABELS.get(emotion, {"label": emotion or "—", "emoji": ""}) if emotion else {"label": "—", "emoji": ""}
            rows.append({
                "ID": fid,
                "Dosya": fname,
                "Süre": f"{audio_utils.format_duration(dur)}",
                "Durum": status_map.get(status, status),
                "Duygu": f"{emo_info.get('emoji','')} {emo_info['label']}",
                "Güven": f"%{confidence*100:.0f}" if confidence else "—",
                "Yüklenme": (uploaded_at or "")[:16].replace("T", " ")
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz yükleme yapılmadı.")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    init_app()

    with st.sidebar:
        st.markdown('<div style="font-family:\'Space Mono\',monospace; font-size:1.1rem; color:#6ee7b7; margin-bottom:0.5rem;">THOMAS</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#64748b; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:1.5rem;">v0.1 · Capstone Demo</div>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio(
            "Sayfa",
            ["⬆️ Yükle & İşle", "📊 Dashboard"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.75rem; color:#64748b;">TorchServe · Streamlit · SQLite<br>Librosa · PyTorch</div>',
            unsafe_allow_html=True
        )

    if page == "⬆️ Yükle & İşle":
        page_upload()
    elif page == "📊 Dashboard":
        page_dashboard()


if __name__ == "__main__":
    main()
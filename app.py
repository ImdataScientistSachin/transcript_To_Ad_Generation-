import os
import streamlit as st
from core import run_pipeline
from utils_logging import configure_logging, get_logger
from core.nlg import SimpleNLG, LLMNLG
from core.cache import CACHE_DIR

configure_logging()
logger = get_logger(__name__)

st.set_page_config(page_title="Transcript → Ad", layout="centered")
st.title("Transcript → Ad Generator")

# On app start, run a maintenance cleanup in background if last cleanup > 24h
try:
    from core.cache import get_last_cleanup, set_last_cleanup, purge_cache
    import threading
    import time

    def _maybe_cleanup():
        try:
            last = get_last_cleanup()
            if time.time() - last > 24 * 3600:
                # purge files older than 30 days
                purge_cache(older_than_seconds=30 * 24 * 3600)
                set_last_cleanup(time.time())
        except Exception:
            logger.exception("Background cache cleanup failed")

    threading.Thread(target=_maybe_cleanup, daemon=True).start()
except Exception:
    logger.exception("Failed to schedule background cache cleanup")

# Sidebar controls
st.sidebar.header("Settings")
nlg_backend = st.sidebar.selectbox("NLG Backend", ["Simple (local)", "LLM (structured JSON)"])
use_mock_llm = st.sidebar.checkbox("Force mock LLM (no API calls)", value=False)
cache_enabled = st.sidebar.checkbox("Enable cache", value=True)
cache_ttl_hours = st.sidebar.number_input("Cache TTL (hours)", min_value=0, max_value=168, value=24)
st.sidebar.markdown("---")

if st.sidebar.button("Show LLM usage log"):
    log_path = os.path.join(os.path.dirname(__file__), "llm_usage.log")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as lf:
                data = lf.read().strip().splitlines()[-50:]
            st.sidebar.text_area("Last LLM usage lines", value="\n".join(data), height=240)
        except Exception:
            st.sidebar.error("Failed to read LLM usage log")
    else:
        st.sidebar.info("No usage log found yet.")

    if st.sidebar.button("Clear cache"):
        try:
            only_old = st.sidebar.checkbox("Only purge files older than N days", value=False)
            if only_old:
                days = st.sidebar.number_input("Purge files older than (days)", min_value=1, max_value=365, value=30)
                removed = purge_cache(older_than_seconds=int(days * 24 * 3600))
            else:
                removed = 0
                if os.path.isdir(CACHE_DIR):
                    for f in os.listdir(CACHE_DIR):
                        p = os.path.join(CACHE_DIR, f)
                        try:
                            os.remove(p)
                            removed += 1
                        except Exception:
                            logger.exception("Failed to remove cache file %s", p)
            st.sidebar.success(f"Cleared {removed} cache files")
        except Exception as e:
            logger.exception("Failed to clear cache")
            st.sidebar.error(f"Failed to clear cache: {e}")

# Build NLG instance based on selection
nlg_instance = None
if nlg_backend == "Simple (local)":
    nlg_instance = SimpleNLG()
else:
    nlg_instance = LLMNLG(cache_ttl=int(cache_ttl_hours * 3600), mock=bool(use_mock_llm))

st.subheader("Upload transcript or paste text")
uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"])
sample = st.selectbox(
    "Or pick a sample",
    [
        "",
        "I love using product X. It's fast and reliable.",
        "Our service saved me hours every week.",
    ],
)

text_input = ""
if uploaded is not None:
    raw = uploaded.getvalue()
    try:
        text_input = raw.decode("utf-8")
    except Exception:
        text_input = str(raw)
else:
    text_input = st.text_area("Transcript text", value=sample, height=240)

run_button = st.button("Run analysis & generate ad")

if run_button and text_input.strip():
    with st.spinner("Running pipeline..."):
        # Pass the chosen NLG backend into the pipeline
        result = run_pipeline(text_input, nlg=nlg_instance)
        logger.info("Pipeline completed")

    st.subheader("Ad JSON / Copy")
    # If LLMNLG produced structured dict, show JSON; else show text
    ad_copy = result.get("ad_copy")
    if isinstance(ad_copy, dict):
        st.json(ad_copy)
        st.markdown("**Rendered CTA**")
        st.write(ad_copy.get("cta"))

        # Download generated ad JSON
        try:
            import json as _json

            ad_bytes = _json.dumps(ad_copy, indent=2, ensure_ascii=False).encode("utf-8")
            st.download_button("Download ad JSON", data=ad_bytes, file_name="ad.json", mime="application/json")
        except Exception:
            logger.exception("Failed to prepare ad JSON download")

        # Show validation error prominently if present and provide details
        v_err = ad_copy.get("_validation_error")
        if v_err:
            st.warning("Ad JSON did not validate against schema — fallback used.")
            with st.expander("View validation details", expanded=True):
                st.markdown("**Validation Error**")
                st.code(str(v_err))
                st.markdown("**Fallback ad JSON (returned to UI)**")
                st.json(ad_copy)
                st.markdown(
                    "If you expected a structured ad, try toggling 'Force mock LLM' or review LLM logs in the sidebar."
                )
    else:
        st.write(ad_copy)
        # Allow download for plain text ad copy
        try:
            txt_bytes = str(ad_copy).encode("utf-8")
            st.download_button("Download ad text", data=txt_bytes, file_name="ad.txt", mime="text/plain")
        except Exception:
            logger.exception("Failed to prepare ad text download")

    st.subheader("Key Insights")
    analysis = result.get("analysis", {})
    kws = analysis.get("keywords", []) or []
    if kws:
        st.markdown("**Keywords (term — score)**")
        for k in kws:
            if isinstance(k, dict):
                st.write(f"- {k.get('term')} — {k.get('score')}")
            else:
                st.write(f"- {k}")
    else:
        st.write("No keywords found")

    ents = analysis.get("entities", []) or []
    if ents:
        st.markdown("**Named Entities**")
        for e in ents:
            st.write(f"- {e.get('text')} ({e.get('label')})")

    pos = analysis.get("pos", {}) or {}
    if pos:
        st.markdown("**POS breakdown**")
        st.json(pos)

    st.subheader("Detected Gaps")
    st.write(result.get("gaps") or "No obvious gaps detected")

    st.subheader("Storyboard (suggested frames)")
    for i, frame in enumerate(result.get("storyboard", []), 1):
        st.markdown(f"**Frame {i}**: {frame}")
    # Image uploads to pair with frames (optional)
    uploaded_images = st.file_uploader(
        "Upload images for frames (optional)", accept_multiple_files=True, type=["png", "jpg", "jpeg", "gif"]
    )

    # Rendering options for low-memory environments
    st.markdown("**Render options**")
    resolution_choice = st.selectbox(
        "Resolution",
        ["720x1280", "480x854"],
        index=0,
    )
    fps_choice = st.selectbox("FPS", [24, 15], index=0)
    crossfade = st.slider("Crossfade duration (s)", min_value=0.0, max_value=2.0, value=0.5, step=0.1)

    # Render preview button — uses MoviePy to create a quick MP4 preview in background
    from core.video import render_storyboard_preview
    import uuid
    import json

    render_id = None
    progress_path = None

    if st.button("Render storyboard preview"):
        # Prepare frames and images
        frames = result.get("storyboard", []) or []
        image_paths = []
        # Save uploaded images to temp files
        if uploaded_images:
            for up in uploaded_images:
                try:
                    cache_dir = os.path.join(os.path.dirname(__file__), "..", ".cache")
                    tmp = os.path.join(cache_dir, up.name)
                    with open(tmp, "wb") as f:
                        f.write(up.getbuffer())
                    image_paths.append(tmp)
                except Exception:
                    image_paths.append(None)

        # Parse resolution
        w, h = (720, 1280) if resolution_choice == "720x1280" else (480, 854)

        options = {"resolution": (w, h), "fps": int(fps_choice), "crossfade": float(crossfade)}

        # Try to use RQ (Redis) if available; otherwise fallback to background thread
        try:
            from core.queue import enqueue_render, get_job_status

            job_id = enqueue_render(frames, image_paths, options)
            placeholder = st.empty()
            prog = st.progress(0)
            status_text = placeholder.text("Queued render job...")

            # Poll job status
            while True:
                time.sleep(1)
                st.experimental_rerun() if False else None
                try:
                    st.session_state  # dummy to ensure Streamlit context
                except Exception:
                    pass
                stat = get_job_status(job_id)
                status = stat.get("status")
                meta = stat.get("meta") or {}
                p = int(meta.get("progress", 0))
                prog.progress(p)
                status_text.text(f"Render job {status} — {p}%")
                if status in ("finished", "failed", "stopped") or p >= 100 or status in ("error", "deferred"):
                    result_path = meta.get("status") or stat.get("result")
                    if isinstance(result_path, str) and result_path.startswith("error:"):
                        placeholder.error(result_path)
                    elif result_path:
                        try:
                            with open(result_path, "rb") as vf:
                                video_bytes = vf.read()
                            st.video(video_bytes)
                            # Use job id in filename when available
                            fname = f"preview_{job_id}.mp4" if job_id else "preview.mp4"
                            st.download_button("Download preview", data=video_bytes, file_name=fname, mime="video/mp4")
                        except Exception as e:
                            placeholder.error(f"Failed to read result: {e}")
                    break

        except Exception:
            # fallback to local thread renderer (previous behavior)
            render_id = str(uuid.uuid4())
            progress_path = os.path.join(os.path.dirname(__file__), "..", ".cache", f"render_{render_id}.json")

            def _write_progress(p: int, status: str = ""):
                try:
                    with open(progress_path, "w", encoding="utf-8") as pf:
                        json.dump({"progress": int(p), "status": status}, pf)
                except Exception:
                    pass

            # Background worker
            def _worker():
                try:
                    _write_progress(0, "starting")
                    out = render_storyboard_preview(
                        frames,
                        resolution=(w, h),
                        fps=int(fps_choice),
                        crossfade=float(crossfade),
                        images=image_paths,
                        progress_callback=lambda p: _write_progress(p, "rendering"),
                    )
                    _write_progress(100, out)
                except Exception as e:
                    _write_progress(100, f"error:{e}")

            # Start background thread
            t = threading.Thread(target=_worker, daemon=True)
            t.start()

            # Poll for progress and update UI
            placeholder = st.empty()
            prog = st.progress(0)
            status_text = placeholder.text("Rendering preview...")
            last_progress = 0
            while True:
                time.sleep(0.5)
                try:
                    with open(progress_path, "r", encoding="utf-8") as pf:
                        data = json.load(pf)
                    p = int(data.get("progress", 0))
                    prog.progress(p)
                    if p != last_progress:
                        status_text.text(f"Rendering preview... {p}%")
                        last_progress = p
                    if p >= 100:
                        # finished; data.status contains output path or error
                        status = data.get("status", "")
                        if isinstance(status, str) and status.startswith("error:"):
                            placeholder.error(status)
                        else:
                            # status is output path
                            try:
                                with open(status, "rb") as vf:
                                    video_bytes = vf.read()
                                st.video(video_bytes)
                                # Use render id to construct filename when possible
                                fname = f"preview_{render_id}.mp4" if render_id else "preview.mp4"
                                st.download_button(
                                    "Download preview",
                                    data=video_bytes,
                                    file_name=fname,
                                    mime="video/mp4",
                                )
                            except Exception as e:
                                placeholder.error(f"Failed to read output: {e}")
                        break
                except Exception:
                    # ignore read errors while file is being created
                    pass

            placeholder.success("Render complete")

    st.sidebar.success("Pipeline run complete")

"""Simple video rendering utilities for storyboards.

This module provides a lightweight `render_storyboard_preview` function
that converts a list of short frame descriptions into a short MP4 using
MoviePy. The renderer is intentionally simple: each frame is a solid
background with centered text. This is suitable for quick previews and
tests; for production-quality video, integrate stock footage or a
rendering API.
"""
from typing import List, Optional, Callable, Any
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


def render_storyboard_preview(
    frames: List[str],
    out_path: Optional[str] = None,
    duration_per_frame: float = 3.0,
    resolution: tuple = (720, 1280),
    fps: int = 24,
    crossfade: float = 0.5,
    images: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> str:
    """Render a brief MP4 preview from storyboard frames.

    Args:
        frames: List of frame description strings.
        out_path: Optional output path. If None, a temporary file is created.
        duration_per_frame: Seconds per frame.

    Returns:
        The path to the rendered MP4 file.

    Raises:
        ImportError: If MoviePy or its backend is not available.
    """
    try:
        from moviepy.editor import concatenate_videoclips, ColorClip, CompositeVideoClip, ImageClip
        from moviepy.video.fx.all import fadein, fadeout
    except Exception as e:
        logger.error("MoviePy not available: %s", e)
        raise ImportError("moviepy is required for rendering storyboard previews")
    # Use Pillow for text rasterization to avoid ImageMagick dependency
    # Prepare PIL placeholders before attempting import so mypy sees consistent names
    Image: Any = None
    ImageDraw: Any = None
    ImageFont: Any = None
    try:
        from PIL import Image as _Image, ImageDraw as _ImageDraw, ImageFont as _ImageFont
        Image = _Image
        ImageDraw = _ImageDraw
        ImageFont = _ImageFont
    except Exception:
        Image = None
        ImageDraw = None
        ImageFont = None

    if not frames:
        # Create a single empty clip indicating no frames
        frames = ["(no storyboard frames)"]
    if images is None:
        images = []

    clips = []
    # Build a clip per frame: colored background + centered text
    total = len(frames)
    for i, text in enumerate(frames):
        # Color clip provides a background; default portrait-friendly
        w, h = resolution
        bg = ColorClip(size=(w, h), color=(20, 20, 20)).set_duration(duration_per_frame)
        # If an image is provided for this frame, use it centered and scaled
        img_clip = None
        if images and i < len(images) and images[i] is not None:
            try:
                img_clip = ImageClip(images[i]).set_duration(duration_per_frame)
                img_clip = img_clip.resize(height=h - 120)
                img_clip = img_clip.set_position(('center', 'center'))
            except Exception:
                img_clip = None

        # Render text to an image via Pillow to avoid ImageMagick/TextClip
        txt_img_path = None
        img_h = 0
        try:
            if Image is not None:
                # Create a transparent image for the text with word wrap
                font = ImageFont.load_default()
                margin = 20
                max_w = w - 2 * margin
                # naive wrapping: split into chunks roughly by characters
                lines = []
                words = str(text).split()
                cur = ""
                for word in words:
                    if len((cur + " " + word).strip()) * 10 < max_w:
                        cur = (cur + " " + word).strip()
                    else:
                        lines.append(cur)
                        cur = word
                if cur:
                    lines.append(cur)
                # estimate height
                line_h = 24
                img_h = line_h * max(1, len(lines)) + 40
                img = Image.new("RGBA", (max_w, img_h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                y = 10
                for ln in lines:
                    draw.text((10, y), ln, font=font, fill=(255, 255, 255, 255))
                    y += line_h
                # save temp
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                img.save(tf.name)
                txt_img_path = tf.name
                img_h = img_h if img_h else img_h
        except Exception:
            logger.exception("Failed to rasterize text image for frame %d", i)
            txt_img_path = None

        parts = [bg]
        if img_clip:
            parts.append(img_clip)
        if txt_img_path:
            try:
                text_clip = ImageClip(txt_img_path).set_duration(duration_per_frame)
                # Position text above the bottom margin or centered if no image height known
                y_pos = 'center' if img_h == 0 else (h - img_h - 40)
                text_clip = text_clip.set_position(('center', y_pos))
                parts.append(text_clip)
            except Exception:
                logger.exception("Failed to create ImageClip for rasterized text for frame %d", i)
        composed = CompositeVideoClip(parts)
        # Apply fade in/out if requested
        if crossfade and crossfade > 0:
            try:
                composed = fadein(composed, crossfade)
                composed = fadeout(composed, crossfade)
            except Exception:
                logger.exception("Failed to apply fade in/out for frame %d", i)
        clips.append(composed)
        # cleanup temp text image if created
        try:
            if txt_img_path:
                os.unlink(txt_img_path)
        except Exception:
            logger.debug("Failed to delete temp text image %s", txt_img_path, exc_info=True)
        # report progress after preparing each clip (scaled to 0-60%)
        if progress_callback:
            try:
                progress_callback(int(10 + (i / max(1, total)) * 50))
            except Exception:
                logger.debug("Progress callback raised during clip prep", exc_info=True)

    final = None
    try:
        if crossfade and crossfade > 0 and len(clips) > 1:
            # apply crossfade by using concatenate with padding negative (overlap)
            final = concatenate_videoclips(clips, method='compose', padding=-crossfade)
        else:
            final = concatenate_videoclips(clips, method='compose')
    except Exception:
        # As a last resort, attempt a simple concatenation and log the error
        logger.exception("Primary concatenation failed, falling back to simple concatenate")
        from moviepy.editor import concatenate_videoclips as _cv
        final = _cv(clips)

    if out_path is None:
        fd, out_path = tempfile.mkstemp(suffix='.mp4')
        os.close(fd)
    # Before writing, report mid progress
    if progress_callback:
        try:
            progress_callback(60)
        except Exception:
            logger.debug("Progress callback raised before write_videofile", exc_info=True)

    # Write the file to disk; use provided fps
    # Write the file to disk (this may be slow depending on ffmpeg and system)
    final.write_videofile(out_path, codec='libx264', audio=False, fps=fps, verbose=False, logger=None)
    # Notify final progress
    if progress_callback:
        try:
            progress_callback(100)
        except Exception:
            logger.debug("Progress callback raised after write_videofile", exc_info=True)
    return out_path

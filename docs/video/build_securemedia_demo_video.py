from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import AudioFileClip, CompositeAudioClip, ImageClip, concatenate_audioclips, concatenate_videoclips


ROOT = Path(r"C:\Users\sseja\OneDrive\Documents\New project 2")
VIDEO_DIR = ROOT / "docs" / "video"
AUDIO_DIR = VIDEO_DIR / "audio"
FRAME_DIR = VIDEO_DIR / "frames"
OUTPUT_PATH = VIDEO_DIR / "securemedia-demo.mp4"

SCENES = [
    {
        "audio": AUDIO_DIR / "scene01_intro.wav",
        "title": "SecureMedia AI",
        "body": "A simple website that checks uploaded images for similarity, duplicate risk, and ownership status.",
        "image": None,
    },
    {
        "audio": AUDIO_DIR / "scene02_home.wav",
        "title": "Step 1: Open the website",
        "body": "The home screen keeps the flow simple: choose a file, preview the image, and read the result cards on the right.",
        "image": ROOT / "securemedia-video-idle.png",
    },
    {
        "audio": AUDIO_DIR / "scene03_selected.wav",
        "title": "Step 2: Select an image",
        "body": "The preview updates immediately, so the user can confirm the selected file before running analysis.",
        "image": ROOT / "securemedia-video-selected.png",
    },
    {
        "audio": AUDIO_DIR / "scene04_result.wav",
        "title": "Step 3: Analyze the upload",
        "body": "The backend processes the image, compares it with stored data, and returns similarity, duplicate status, owner, and blockchain verification.",
        "image": ROOT / "securemedia-video-result-final.png",
    },
    {
        "audio": AUDIO_DIR / "scene05_deploy.wav",
        "title": "Deployment",
        "body": "The project runs as a single full-stack service on Google Cloud Run, with React on the frontend and Flask on the backend.",
        "image": ROOT / "docs" / "assets" / "securemedia-cloudrun-live.png",
    },
]


def load_font(size: int, bold: bool = False):
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = load_font(58, bold=True)
BODY_FONT = load_font(34)
FOOTER_FONT = load_font(24)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paste_contained(base: Image.Image, image: Image.Image, box: tuple[int, int, int, int]):
    left, top, width, height = box
    image = image.copy()
    image.thumbnail((width, height))
    shadow = Image.new("RGBA", (image.width + 24, image.height + 24), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((12, 12, image.width + 12, image.height + 12), radius=26, fill=(15, 23, 42, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    x = left + (width - image.width) // 2
    y = top + (height - image.height) // 2
    base.alpha_composite(shadow, (x - 12, y - 12))

    frame = Image.new("RGBA", (image.width + 20, image.height + 20), (255, 255, 255, 0))
    frame_draw = ImageDraw.Draw(frame)
    frame_draw.rounded_rectangle((0, 0, image.width + 19, image.height + 19), radius=24, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    base.alpha_composite(frame, (x - 10, y - 10))
    base.alpha_composite(image.convert("RGBA"), (x, y))


def build_scene_frame(index: int, scene: dict):
    canvas = Image.new("RGBA", (1920, 1080), (244, 247, 251, 255))
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle((64, 56, 1856, 1024), radius=34, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    draw.text((110, 108), scene["title"], font=TITLE_FONT, fill=(15, 23, 42, 255))

    body_lines = wrap_text(draw, scene["body"], BODY_FONT, 760)
    y = 210
    for line in body_lines:
        draw.text((110, y), line, font=BODY_FONT, fill=(71, 85, 105, 255))
        y += 48

    draw.rounded_rectangle((110, 480, 530, 600), radius=24, fill=(239, 246, 255, 255))
    draw.text((140, 518), "Live website demo", font=BODY_FONT, fill=(29, 78, 216, 255))
    draw.text((110, 950), "AI-generated narration. Demo video created locally.", font=FOOTER_FONT, fill=(100, 116, 139, 255))

    if scene["image"] is not None:
        image = Image.open(scene["image"]).convert("RGBA")
        paste_contained(canvas, image, (820, 120, 940, 820))
    else:
        draw.rounded_rectangle((840, 210, 1710, 770), radius=32, fill=(239, 246, 255, 255))
        draw.text((930, 410), "SecureMedia AI", font=load_font(72, bold=True), fill=(29, 78, 216, 255))
        draw.text((930, 510), "Upload, analyze, and review results", font=load_font(34), fill=(51, 65, 85, 255))

    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    output = FRAME_DIR / f"scene_{index:02d}.png"
    canvas.convert("RGB").save(output, quality=95)
    return output


def main():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []

    for index, scene in enumerate(SCENES, start=1):
        if not scene["audio"].exists():
            raise FileNotFoundError(f"Missing audio file: {scene['audio']}")
        frame_path = build_scene_frame(index, scene)
        audio_clip = AudioFileClip(str(scene["audio"]))
        duration = audio_clip.duration + 0.35
        image_clip = ImageClip(str(frame_path)).with_duration(duration)
        video_clips.append(image_clip)
        audio_clips.append(audio_clip)

    final_video = concatenate_videoclips(video_clips, method="compose")
    final_audio = concatenate_audioclips(audio_clips)
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        str(OUTPUT_PATH),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )

    for clip in video_clips:
        clip.close()
    for clip in audio_clips:
        clip.close()
    final_audio.close()
    final_video.close()

    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()

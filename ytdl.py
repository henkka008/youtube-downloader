import shutil

from pytubefix import YouTube
from sys import argv
import os
import subprocess

ffmpeg = shutil.which("ffmpeg")
if ffmpeg is None:
    raise RuntimeError("ffmpeg not found. Install ffmpeg and add it to PATH")

link = argv[1]
yt = YouTube(link)

print("Title: ", yt.title)
print("Views: ", yt.views)

video = (
    yt.streams
    .filter(adaptive=True, file_extension='mp4', only_video=True)
    .order_by("resolution")
    .desc()
    .first()
)

audio = (
    yt.streams
    .filter(adaptive=True, only_audio=True)
    .order_by("abr")
    .desc()
    .first()
)

output = './videos'
os.makedirs(output, exist_ok=True)

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename.strip()

def get_unique_filename(folder, filename, extension):
    filename = sanitize_filename(filename)
    counter = 1
    full_path = os.path.join(folder,f"{filename}.{extension}")
    while os.path.exists(full_path):
        full_path = os.path.join(folder, f"{filename} ({counter}).{extension}")
        counter += 1
    return full_path

video_path = os.path.join(output, "video.mp4")
audio_ext = audio.subtype
audio_path = os.path.join(output, f"audio.{audio_ext}")
final_path = get_unique_filename(output, yt.title, "mp4")



video.download(output_path=output, filename="video.mp4")
audio.download(output_path="./videos",filename=f"audio.{audio_ext}")



ffmpeg_cmd = [
    ffmpeg,
    "-y",
    "-i", video_path,
    "-i", audio_path,
    "-c:v", "copy",
]

if audio_ext == "mp4":
    ffmpeg_cmd += ["-c:a", "copy"]
else:
    ffmpeg_cmd += ["-c:a", "aac", "-b:a", "192k"]

ffmpeg_cmd.append(final_path)
subprocess.run(ffmpeg_cmd, check=True)

print("Cleaning...")
os.remove(video_path)
os.remove(audio_path)

print("Done: ", final_path)

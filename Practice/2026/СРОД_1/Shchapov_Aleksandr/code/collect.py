"""Restore missing media from the manifest. Texts are authored descriptions, kept in Git.
Usage: python3 code/collect.py
Requires: yt-dlp, imageio-ffmpeg; access to the public source URLs.
Existing files are retained. Re-downloaded streams may have different hashes.
"""
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import imageio_ffmpeg
import yt_dlp

root = Path(__file__).resolve().parents[1]
records = json.loads((root / 'data/manifest.json').read_text(encoding='utf-8'))['records']
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
for record in records:
    for kind in ('image', 'audio'):
        material = record['materials'][kind]
        target = root / material['path']
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if kind == 'image':
            request = urllib.request.Request(material['source_url'], headers={'User-Agent': 'Mozilla/5.0'})
            target.write_bytes(urllib.request.urlopen(request, timeout=60).read())
        else:
            with tempfile.TemporaryDirectory() as temp:
                options = {'outtmpl': str(Path(temp) / 'audio.%(ext)s'), 'noplaylist': True,
                           'format': 'bestaudio/best', 'ffmpeg_location': ffmpeg, 'cachedir': False}
                with yt_dlp.YoutubeDL(options) as downloader:
                    info = downloader.extract_info(material['source_url'], download=True)
                    source = downloader.prepare_filename(info)
                subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', source,
                                '-ar', '44100', '-c:a', 'pcm_s16le', str(target)], check=True)
        print('Restored', target.relative_to(root))

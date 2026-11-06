from openai import OpenAI
from pathlib import Path
from tempfile import TemporaryDirectory
from dotenv import load_dotenv

import yt_dlp

load_dotenv()

def download_audio(url: str, output_dir: str) -> str:
    options = {
        'format': 'bestaudio/best',
        'outtmpl': str(Path(output_dir) / '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }
        ],
    }

    with yt_dlp.YoutubeDL(options) as youtube:
        info = youtube.extract_info(url, download=True)

    audio_path = Path(output_dir) / f"{info['id']}.mp3"

    if not audio_path.exists():
        raise FileNotFoundError('Audio file was not created')

    return str(audio_path)

def transcribe_audio(audio_path: str) -> dict:
    client = OpenAI()

    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='verbose_json',
            timestamp_granularities=['segment'],
        )

    segments = [
        {
            'start': segment.start,
            'end': segment.end,
            'text': segment.text,
        }
        for segment in transcript.segments
    ]

    return {
        'text': transcript.text,
        'language': transcript.language,
        'segments': segments,
    }
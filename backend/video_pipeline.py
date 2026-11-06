from tempfile import TemporaryDirectory

from backend.transcription_service import download_audio, transcribe_audio
from backend.chunking_service import create_chunks
from backend.vector_service import save_chunks
from backend.youtube_service import get_video_info
from backend.supadata_service import get_transcript
from urllib.parse import urlparse, parse_qs 

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        video_id = parsed.path.strip('/')
    elif parsed.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
        video_id = parse_qs(parsed.query).get('v', [''])[0]
    else:
        raise ValueError('Invalid YouTube URL')

    if not video_id:
        raise ValueError('Video ID not found')

    return video_id

def process_video(url):
    video_id = extract_video_id(url)
    segments = get_transcript(url)
    chunks = create_chunks(segments)
    save_chunks(chunks, video_id)
    
    return {
    'video_id': video_id,
    'chunks_count': len(chunks),
    'status': 'completed',
}
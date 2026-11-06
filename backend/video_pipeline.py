from tempfile import TemporaryDirectory

from backend.transcription_service import download_audio, transcribe_audio
from backend.chunking_service import create_chunks
from backend.vector_service import save_chunks
from backend.youtube_service import get_video_info


def process_video(url):
    video_info = get_video_info(url)
    print(video_info)
    video_id = video_info['video_id']
    with TemporaryDirectory() as temp_dir:
        print('Temporary folder:', temp_dir)
        audio_path = download_audio(url, temp_dir)
        transcription = transcribe_audio(audio_path)
        segments = transcription['segments']
        chunks = create_chunks(segments)
        save_chunks(chunks, video_id)

    return {
    'video_id': video_id,
    'title': video_info['title'],
    'chunks_count': len(chunks),
    'status': 'completed',
}    
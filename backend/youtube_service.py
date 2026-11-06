from urllib.parse import urlparse
import yt_dlp


def get_video_info(url: str) -> dict:
    parsed = urlparse(url)

    allowed_domains = {
        'youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'youtu.be',
    }

    if parsed.scheme not in ('http', 'https') or parsed.hostname not in allowed_domains:
        raise ValueError('Please provide a valid YouTube URL')

    options = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(options) as youtube:
        info = youtube.extract_info(url, download=False)

    return {
        'video_id': info.get('id'),
        'title': info.get('title'),
        'channel': info.get('channel'),
        'duration': info.get('duration'),
        'thumbnail': info.get('thumbnail'),
        'url': info.get('webpage_url'),
    }
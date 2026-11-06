
import os
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


def get_transcript(url: str) -> list:
    params = urlencode({
        'url': url,
        'mode': 'native'
    })

    request = Request(
        f'https://api.supadata.ai/v1/transcript?{params}',
        headers={
            'x-api-key': os.environ['SUPADATA_API_KEY']
        }
    )

    with urlopen(request, timeout=30) as response:
        data = json.load(response)

    segments = []

    for segment in data['content']:
        start = segment['offset'] / 1000
        end = start + segment['duration'] / 1000

        segments.append({
            'text': segment['text'],
            'start': start,
            'end': end
        })

    return segments


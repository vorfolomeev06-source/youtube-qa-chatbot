from fastapi import HTTPException
from pydantic import BaseModel
from backend.youtube_service import get_video_info
from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
import logging
import os
import json
from backend.video_pipeline import process_video
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from backend.config import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    LANGSMITH_API_KEY,
)

app = FastAPI(
    title='YouTube Q&A Chatbot',
    description='AI-powered YouTube video question answering',
    version='1.0.0',
)


@app.get('/')
def home():
    return {
        'message': 'YouTube Q&A Chatbot API is running'
    }


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'openai_configured': bool(OPENAI_API_KEY),
        'pinecone_configured': bool(PINECONE_API_KEY),
        'langsmith_configured': bool(LANGSMITH_API_KEY),
    }


class VideoRequest(BaseModel):
    url: str


@app.post('/video/info')
def video_info(request: VideoRequest):
    try:
        return get_video_info(request.url)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail='Could not retrieve video information from YouTube',
        )


@app.get('/test-transcript')
def test_transcript():
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch('aircAruvnKk')

        return {
            'status': 'ok',
            'segments': [
                {
                    'text': segment.text,
                    'start': segment.start,
                    'duration': segment.duration
                }
                for segment in list(transcript)[:3]
            ]
        }

    except Exception:
        logging.exception('YouTube transcript test failed')

        raise HTTPException(
            status_code=502,
            detail='Transcript retrieval failed'
        )

@app.get('/test-supadata')
def test_supadata():
    params = urlencode({
        'url': 'https://www.youtube.com/watch?v=aircAruvnKk',
        'mode': 'native'
    })

    request = Request(
        f'https://api.supadata.ai/v1/transcript?{params}',
        headers={'x-api-key': os.environ['SUPADATA_API_KEY']}
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)

        return {
            'status': 'ok',
            'segments': data['content'][:3]
        }

    except HTTPError as error:
        logging.exception('Supadata request failed')
        raise HTTPException(
            status_code=502,
            detail=f'Supadata returned HTTP {error.code}'
        )

@app.post('/video/process')
def video_process(request: VideoRequest):
    return process_video(request.url)
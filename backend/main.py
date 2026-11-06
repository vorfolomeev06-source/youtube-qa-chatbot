from fastapi import HTTPException
from pydantic import BaseModel
from backend.youtube_service import get_video_info
from fastapi import FastAPI


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
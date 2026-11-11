from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from backend.vector_service import search_chunks, get_video_chunks


@tool
def search_transcript(question: str, video_id: str) -> str:
    '''Search the video transcript for information relevant to a question.'''

    chunks = search_chunks(question, video_id, top_k=5)

    if not chunks:
        return 'No relevant information found in the video.'

    results = []

    for chunk in chunks:
        results.append(
            f"[{chunk['start']:.0f}s] {chunk['text']}"
        )

    return '\n\n'.join(results)


@tool
def get_video_context(video_id: str) -> str:
    '''Retrieve the video transcript in chronological order for broader context.'''

    chunks = get_video_chunks(video_id)

    if not chunks:
        return 'No transcript found for this video.'

    return '\n\n'.join(
        f"[{chunk['start']:.0f}s] {chunk['text']}"
        for chunk in chunks
    )

model = ChatOpenAI(
    model='gpt-4.1-mini',
    temperature=0
)

def build_video_agent(video_id: str):

    @tool
    def search_current_video(question: str) -> str:
        '''Search the current YouTube video transcript for relevant information.'''
        return search_transcript.invoke({
            'question': question,
            'video_id': video_id
        })

    @tool
    
    def get_current_video_context() -> str:
        '''Retrieve the current video transcript for broader context.'''
        return get_video_context.invoke({
            'video_id': video_id
        })

    @tool
    def find_video_moment(topic: str) -> str:
        '''Find the most relevant timestamp in the current YouTube video for a specific topic.'''

        chunks = search_chunks(topic, video_id, top_k=1)

        if not chunks:
            return 'No matching moment found in this video.'

        chunk = chunks[0]
        timestamp = int(chunk['start'])

        url = f'https://www.youtube.com/watch?v={video_id}&t={timestamp}s'

        return (
            f"Topic: {topic}\n"
            f"Timestamp: {timestamp} seconds\n"
            f"URL: {url}\n"
            f"Transcript: {chunk['text']}"
        )

    return create_agent(
        model=model,
        tools=[
    search_current_video,
    get_current_video_context,
    find_video_moment
        ],
        system_prompt='''
        you are an educational ai assistant for youtube videos.

        rules:
        - answer questions using the current video's transcript.
        - use search_current_video for questions about video content.
        - use get_current_video_context when broader context is necessary.
        - use tool results as your source of information.
        - do not invent information.
        - include relevant timestamps when available.
        - answer in the same language as the user.
        - use find_video_moment when the user asks where a topic appears in the video or requests a timestamp.
        '''
    )

def ask_agent(
    question: str,
    video_id: str,
    history: list | None = None
):
    agent = build_video_agent(video_id)

    messages = []

    for message in (history or [])[-10:]:
        if message.get('role') in ['user', 'assistant']:
            messages.append({
                'role': message['role'],
                'content': message['content']
            })

    messages.append({
        'role': 'user',
        'content': question
    })

    result = agent.invoke({
        'messages': messages
    })

    search_query = question

    for message in result['messages']:
        for call in (getattr(message, 'tool_calls', None) or []):
            if call['name'] == 'search_current_video':
                search_query = call['args']['question']
            elif call['name'] == 'find_video_moment':
                search_query = call['args']['topic']

    chunks = search_chunks(search_query, video_id, top_k=5)

    sources = []

    for chunk in chunks:
        timestamp = int(chunk['start'])

        sources.append({
            'text': chunk['text'],
            'start': chunk['start'],
            'end': chunk['end'],
            'url': f'https://www.youtube.com/watch?v={video_id}&t={timestamp}s'
        })

    return {
        'answer': result['messages'][-1].content,
        'video_id': video_id,
        'sources': sources
    }
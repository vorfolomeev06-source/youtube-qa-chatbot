
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

openai_client = OpenAI()
pc = Pinecone()

INDEX_NAME = 'youtube-learning-qa'
NAMESPACE = 'test-video'


def get_index():
    existing_indexes = pc.list_indexes().names()

    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1',
            ),
        )

    return pc.Index(INDEX_NAME)


def save_chunk(text: str, start: float, end: float):
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=text,
    )

    embedding = response.data[0].embedding
    index = get_index()

    index.upsert(
        vectors=[
            {
                'id': 'test-chunk-1',
                'values': embedding,
                'metadata': {
                    'text': text,
                    'start': start,
                    'end': end,
                    'video_id': 'test-video',
                },
            }
        ],
        namespace=NAMESPACE,
    )

    return 'Chunk saved successfully'


def search_chunks(question: str, video_id: str, top_k: int = 3) -> list:
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=question,
    )

    query_vector = response.data[0].embedding
    index = get_index()

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace = video_id,
        include_metadata=True,
    )

    return [
        {
            'score': match.score,
            'text': match.metadata.get('text'),
            'start': match.metadata.get('start'),
            'end': match.metadata.get('end'),
        }
        for match in results.matches
    ]

def save_chunks(chunks: list, video_id: str):
    vectors = []

    for i, chunk in enumerate(chunks):
        chunk_id = f'{video_id}-{i}'
        text = chunk['text']
        start = chunk['start']
        end = chunk['end']

        response = openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=text,
        )

        embedding = response.data[0].embedding

        item = {
            'id': chunk_id,
            'values': embedding,
            'metadata': {
                'text': text,
                'start': start,
                'end': end,
                'video_id': video_id,
            },
        }

        vectors.append(item)
        print(chunk_id, len(embedding))

    print('Total vectors:', len(vectors))

    if not vectors:
        return

    index = get_index()

    index.upsert(
        vectors=vectors,
        namespace=video_id,
    )

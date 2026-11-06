from openai import OpenAI
from backend.vector_service import search_chunks

client = OpenAI()

def answer_question(question: str, video_id: str):
    chunks = search_chunks(question, video_id, top_k = 5)
    context_parts = []
    for chunk in chunks:
        context_parts.append(
    f"[Timestamp: {chunk['start']:.0f}s]\n{chunk['text']}"
)
        context = '\n\n'.join(context_parts)

        system_prompt = '''
        you are an educational ai assistant.
        answer the user's question using only the provided video trancsript context.
        do not invent information that is not supported by the context.
        if the context does not contain the answer, clearly say so.
        give clear, helpful explanations.
        when relevant, reference timestamps from the provided context.
'''
    response = client.responses.create(
    model='gpt-4.1-mini',
    instructions=system_prompt,
    input=f'Video transcript context:\n{context}\n\nUser question:\n{question}'
)
    answer = response.output_text
    return {
        'answer': answer,
        'video_id': video_id,
        'sources': chunks
    }
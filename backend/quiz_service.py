from openai import OpenAI
from backend.vector_service import get_video_chunks
from pydantic import BaseModel, Field
from typing import Literal

client = OpenAI()

class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: Literal['A', 'B', 'C', 'D']
    explanation: str


class Quiz(BaseModel):
    questions: list[QuizQuestion]

def generate_quiz(
    video_id: str,
    difficulty: str,
    num_questions: int = 5
):
    chunks = get_video_chunks(video_id)

    if not chunks:
        raise ValueError('No transcript chunks found for this video')

    context = '\n\n'.join(chunk['text'] for chunk in chunks)
    difficulty = difficulty.lower()

    if difficulty not in ['easy', 'medium', 'hard']:
        raise ValueError('Difficulty must be easy, medium, or hard')

    if not 1 <= num_questions <= 10:
        raise ValueError('Number of questions must be between 1 and 10')

    prompt = f'''
    you are an ai educational quiz generator.
    create {num_questions} multiple choice questions based only on the video transcript ptovided below.

    difficulty level: {difficulty}.

    difficulty guidelines:
    -easy: basic facts and simple concepts.
    -medium: understanding and connections between concepts.
    hard: deeper reasoning and application of knowledge.

    requirements: 
    - every question must have exactly four answer options.
    - only one option can be correct
    - provide a short explanation for the correct answer
    - all questions must be based on the transcript
    - do not invent information
    - avoid duplicate questions 
    - always generate all questions, answer options, and explanations in english.
    - if the transcript is in another language, translate the relevant information into english.

    video transcript:
    {context}
    '''


    response = client.responses.parse(
    model='gpt-4.1-mini',
    instructions='you are an educational quiz generator. always write every question, answer option, and explanation in english, regardless of the transcript language.',
    input=prompt,
    text_format=Quiz,
    temperature=0.3
)

    quiz = response.output_parsed

    if quiz is None:
        raise ValueError('Quiz generation returned no structured response')

    if len(quiz.questions) != num_questions:
        raise ValueError('Generated quiz has an incorrect number of questions')

    return quiz.model_dump()
    


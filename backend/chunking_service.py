def create_chunks(segments: list, max_words: int = 150) -> list:
    chunks = []
    current_text = []
    current_start = None
    current_end = None
    word_count = 0

    for segment in segments:
        text = segment['text'].strip()

        if not text:
            continue

        words = text.split()

        if current_start is None:
            current_start = segment['start']

        if current_text and word_count + len(words) > max_words:
            chunks.append({
                'start': current_start,
                'end': current_end,
                'text': ' '.join(current_text),
            })

            current_text = []
            current_start = segment['start']
            word_count = 0

        current_text.append(text)
        current_end = segment['end']
        word_count += len(words)

    if current_text:
        chunks.append({
            'start': current_start,
            'end': current_end,
            'text': ' '.join(current_text),
        })

    return chunks
import { useState } from 'react'
import './App.css'

const tabs = [
  { id: 'chat', label: 'Ask AI' },
  { id: 'quiz', label: 'Quiz' },  
]

function formatTime(seconds) {
  const total = Math.floor(Number(seconds))
  const minutes = Math.floor(total / 60)
  const remaining = total % 60

  return `${minutes}:${String(remaining).padStart(2, '0')}`
}




function renderAnswerWithTimestamps(text, onTimestampClick) {
  const parts = String(text ?? '')
    .split(/(\*\*.*?\*\*|\b\d{1,2}:\d{2}(?::\d{2})?\b|\b\d+(?:\.\d+)?\s*(?:seconds?|secs?|s)\b)/gi)
    .filter(Boolean)

  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }

    let seconds = null

    const timeMatch = part.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/)

    if (timeMatch) {
      seconds = timeMatch[3]
        ? Number(timeMatch[1]) * 3600 + Number(timeMatch[2]) * 60 + Number(timeMatch[3])
        : Number(timeMatch[1]) * 60 + Number(timeMatch[2])
    } else {
      const secondsMatch = part.match(/^(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|s)$/i)

      if (secondsMatch) {
        seconds = Number(secondsMatch[1])
      }
    }

    if (seconds !== null) {
      return (
        <button
          key={index}
          type="button"
          className="inline-timestamp"
          onClick={() => onTimestampClick(seconds)}
          title={`Jump to ${formatTime(seconds)}`}
        >
          {formatTime(seconds)}
        </button>
      )
    }

    return part
  })
}




function App() {
  const [videoUrl, setVideoUrl] = useState('')
  const [videoId, setVideoId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [activeTab, setActiveTab] = useState('chat')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')

  const [seekSeconds, setSeekSeconds] = useState(0)
  const [playerVersion, setPlayerVersion] = useState(0)

const [difficulty, setDifficulty] = useState('medium')
const [quiz, setQuiz] = useState(null)
const [quizLoading, setQuizLoading] = useState(false)
const [quizError, setQuizError] = useState('')
const [currentQuestion, setCurrentQuestion] = useState(0)
const [selectedAnswer, setSelectedAnswer] = useState(null)
const [quizAnswers, setQuizAnswers] = useState([])
const [quizFinished, setQuizFinished] = useState(false)


  async function handleStartLearning(event) {
    event.preventDefault()

    if (!videoUrl.trim()) {
      setError('Please enter a YouTube URL.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/video/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: videoUrl.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to process video')
      }

      if (!data.video_id) {
        throw new Error('Video ID missing from API response')
      }

      setVideoId(data.video_id)
      setActiveTab('chat')
      setMessages([])
      setSeekSeconds(0)
      setPlayerVersion(0)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  async function handleAskAI(event) {
    event.preventDefault()

    const userQuestion = question.trim()

    if (!userQuestion || chatLoading) {
      return
    }

    setChatLoading(true)
    setChatError('')
    setQuestion('')

    setMessages((previous) => [
      ...previous,
      { role: 'user', text: userQuestion },
    ])

    try {
      const response = await fetch('/api/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
  question: userQuestion,
  video_id: videoId,
  history: messages.slice(-10).map((message) => ({
    role: message.role,
    content: message.text
  }))
}),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate answer')
      }

      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          text: data.answer,
          sources: data.sources || [],
        },
      ])
    } catch (err) {
      setChatError(err.message || 'Unable to get an answer')
    } finally {
      setChatLoading(false)
    }
  }

  function jumpToTimestamp(seconds) {
    const time = Math.max(0, Math.floor(Number(seconds)))

    setSeekSeconds(time)
    setPlayerVersion((previous) => previous + 1)
  }

  function resetVideo() {
    setVideoId(null)
    setVideoUrl('')
    setMessages([])
    setQuestion('')
    setError('')
    setChatError('')
    setSeekSeconds(0)
    setPlayerVersion(0)
  }

async function handleGenerateQuiz() {
  setQuizLoading(true)
  setQuizError('')
  setQuiz(null)
  setCurrentQuestion(0)
  setSelectedAnswer(null)
  setQuizAnswers([])
  setQuizFinished(false)

  try {
    const response = await fetch('/api/quiz/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        difficulty: difficulty,
        num_questions: 5,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to generate quiz')
    }

    if (!Array.isArray(data.questions) || data.questions.length === 0) {
      throw new Error('Quiz response contains no questions')
    }

    setQuiz(data)
  } catch (err) {
    setQuizError(err.message || 'Something went wrong')
  } finally {
    setQuizLoading(false)
  }
}

function handleSelectAnswer(answer) {
  if (selectedAnswer !== null) return

  setSelectedAnswer(answer)
  setQuizAnswers((previous) => [...previous, answer])
}

function handleNextQuestion() {
  if (selectedAnswer === null) return

  if (currentQuestion < quiz.questions.length - 1) {
    setCurrentQuestion((previous) => previous + 1)
    setSelectedAnswer(null)
  } else {
    setQuizFinished(true)
  }
}
function backToQuizLevels() {
  setQuiz(null)
  setCurrentQuestion(0)
  setSelectedAnswer(null)
  setQuizAnswers([])
  setQuizFinished(false)
  setQuizError('')
}

  return (
    <div className="app">
      <header className="header">
        <div className="brand">STUDY / AI</div>
        <span className="header-label">
          YOUR PERSONAL LEARNING SPACE
        </span>
      </header>

      {!videoId ? (
        <main className="hero">
          <div className="eyebrow">
            LEARN SMARTER, NOT HARDER
          </div>

          <h1>
            Turn any video into
            <br />
            a learning experience.
          </h1>

          <p className="subtitle">
  Ask questions, explore key concepts, and test
  your knowledge with interactive YouTube quizzes.
</p>

          <form
            className="video-form"
            onSubmit={handleStartLearning}
          >
            <input
              type="text"
              placeholder="Paste a YouTube video URL..."
              value={videoUrl}
              onChange={(event) => setVideoUrl(event.target.value)}
              disabled={loading}
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Processing...' : 'Start Learning →'}
            </button>
          </form>

          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}

          {loading && (
            <p className="subtitle">
              Processing your video...
            </p>
          )}
        </main>
      ) : (

<main className="workspace">
  <div className="eyebrow">YOUR LEARNING SESSION</div>
  <h1>Ready to learn.</h1>

  <div className="video-player">
    <iframe
      key={`${videoId}-${playerVersion}`}
      src={`https://www.youtube.com/embed/${videoId}?start=${seekSeconds}&autoplay=${playerVersion > 0 ? 1 : 0}&playsinline=1`}
      title="YouTube video player"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    />
  </div>

  <nav className="feature-tabs" aria-label="Learning tools">

            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={activeTab === tab.id ? 'tab active' : 'tab'}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <section className="feature-content">
            {activeTab === 'chat' && (
              <div className="chat-section">
                <div className="feature-heading">
                  <h2>Ask AI</h2>
                  <p>
                    Ask anything about this video and explore
                    answers with timestamps.
                  </p>
                </div>

                <div className="chat-messages">
                  {messages.length === 0 && (
                    <p className="empty-chat">
                      Your learning conversation starts here.
                      Ask your first question.
                    </p>
                  )}

                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`message ${message.role}`}
                    >
                      <div className="message-label">
                        {message.role === 'user' ? 'YOU' : 'STUDY / AI'}
                      </div>

                      
                      <p>
                        {message.role === 'assistant'
                          ? renderAnswerWithTimestamps(
                              message.text,
                              jumpToTimestamp
                            )
                          : message.text}
                      </p>


                      {message.sources?.length > 0 && (
                        <div className="message-sources">
                          <span className="sources-label">
                            RELEVANT MOMENTS
                          </span>

                          <div className="timestamp-list">
                            {message.sources.map((source, sourceIndex) => (
                              <button
                                key={sourceIndex}
                                type="button"
                                className="timestamp"
                                onClick={() => jumpToTimestamp(source.start)}
                              >
                                ▶ {formatTime(source.start)}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {chatLoading && (
                    <p className="loading-message">
                      AI is thinking...
                    </p>
                  )}
                </div>

                {chatError && (
                  <p className="error-message" role="alert">
                    {chatError}
                  </p>
                )}

                <form className="chat-form" onSubmit={handleAskAI}>
                  <input
                    type="text"
                    placeholder="Ask a question about this video..."
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    disabled={chatLoading}
                  />

                  <button
                    type="submit"
                    disabled={chatLoading || !question.trim()}
                  >
                    Send →
                  </button>
                </form>
              </div>
            )}

            
{activeTab === 'quiz' && (
  <div className="quiz-section">
    <div className="feature-heading">
      <h2>Test Your Knowledge</h2>
      <p>Challenge yourself with questions based on this video.</p>
    </div>

    {!quiz && (
      <div className="quiz-setup">
        <h3>Choose your difficulty</h3>

        <div className="difficulty-options">
          {['easy', 'medium', 'hard'].map((level) => (
            <button
              key={level}
              type="button"
              className={difficulty === level ? 'selected' : ''}
              onClick={() => setDifficulty(level)}
              disabled={quizLoading}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>

        <button
          type="button"
          className="primary-action"
          onClick={handleGenerateQuiz}
          disabled={quizLoading}
        >
          {quizLoading ? 'Generating quiz...' : 'Generate Quiz →'}
        </button>
      </div>
    )}

    {quizError && (
      <p className="error-message" role="alert">
        {quizError}
      </p>
    )}

    {quiz && !quizFinished && (() => {
      const item = quiz.questions[currentQuestion]
      const correctAnswer = item.correct_answer
      const isCorrect = selectedAnswer === correctAnswer

      return (
        <div className="quiz-question">
          <div className="quiz-progress">
            QUESTION {currentQuestion + 1} OF {quiz.questions.length}
          </div>

          <h3>{item.question}</h3>

          <div className="quiz-options">
            {item.options.map((option, index) => {
              const letter = String.fromCharCode(65 + index)
              const isSelected = selectedAnswer === letter

              return (
                <button
                  key={letter}
                  type="button"
                  disabled={selectedAnswer !== null}
                  className={
                    selectedAnswer !== null && letter === correctAnswer
                      ? 'correct'
                      : isSelected
                        ? 'incorrect'
                        : ''
                  }
                  onClick={() => handleSelectAnswer(letter)}
                >
                  <span className="option-letter">{letter}</span>
                  {option.replace(/^[A-D][).]\s*/i, '')}
                </button>
              )
            })}
          </div>

          {selectedAnswer !== null && (
            <div className="quiz-feedback">
              <strong>
                {isCorrect ? 'Correct answer!' : 'Not quite!'}
              </strong>

              <p>{item.explanation}</p>

              <button
                type="button"
                className="primary-action"
                onClick={handleNextQuestion}
              >
                {currentQuestion === quiz.questions.length - 1
                  ? 'See Results →'
                  : 'Next Question →'}
              </button>
            </div>
          )}
        </div>
      )
    })()}

    
          {quiz && quizFinished && (
            <div className="quiz-results">
              <div className="eyebrow">QUIZ COMPLETED</div>

              <h3>
                {quizAnswers.filter(
                  (answer, index) =>
                    answer === quiz.questions[index].correct_answer
                ).length} / {quiz.questions.length}
              </h3>

              <p>Questions answered correctly</p>

              <button
                type="button"
                className="primary-action"
                onClick={handleGenerateQuiz}
              >
                Try Again →
              </button>

              <button
                type="button"
                className="primary-action"
                onClick={backToQuizLevels}
              >
                ← Back to Quiz Levels
              </button>
            </div>
          )}
        </div>
      )}


          </section>

          <button
            type="button"
            className="reset-button"
            onClick={resetVideo}
          >
            ← Process another video
          </button>
        </main>
      )}
    </div>
  )
}

export default App


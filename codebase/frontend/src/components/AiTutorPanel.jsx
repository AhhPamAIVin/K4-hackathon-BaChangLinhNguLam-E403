import React, { useEffect, useRef, useState } from 'react';
import {
  ArrowRight,
  BookOpenCheck,
  Brain,
  Check,
  CheckCircle2,
  ChevronRight,
  HelpCircle,
  Loader2,
  MessageSquareText,
  RotateCcw,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Target,
  Trophy,
  X,
} from 'lucide-react';
import {
  askKnowledge,
  askStudyReview,
  createQuiz,
} from '../services/vlearnApi';
import './AiTutorPanel.css';

const QA_SUGGESTIONS = [
  'Tóm tắt ý chính của phần đang học',
  'Giải thích khái niệm này bằng ví dụ',
  'Điểm nào dễ bị hiểu nhầm nhất?',
];

const STUDY_SUGGESTIONS = [
  'Hỏi mình từng bước để kiểm tra mức độ nhớ bài',
  'So sánh hai khái niệm quan trọng trong buổi học',
  'Tạo một mẹo ghi nhớ ngắn từ nội dung bài',
];

function toHistory(messages) {
  return messages
    .filter((message) => ['user', 'assistant'].includes(message.role))
    .slice(-12)
    .map(({ role, content }) => ({ role, content }));
}

function ChatMessage({ message, onQuestionSelect }) {
  const [expandedCitation, setExpandedCitation] = useState(null);

  if (message.role === 'user') {
    return (
      <div className="tutor-message user">
        <div className="tutor-message-label">Bạn</div>
        <div className="tutor-message-bubble">{message.content}</div>
      </div>
    );
  }

  return (
    <div className={`tutor-message assistant ${message.blocked ? 'guardrail-blocked' : ''} ${message.needsClarification ? 'needs-clarification' : ''}`}>
      <div className="tutor-message-label">
        <span className="assistant-mark">
          {message.blocked
            ? <ShieldAlert size={12} />
            : message.needsClarification
              ? <HelpCircle size={12} />
              : <Sparkles size={12} />}
        </span>
        {message.blocked
          ? 'VLearn Guardrail'
          : message.needsClarification
            ? 'Cần thêm ngữ cảnh'
            : 'VLearn AI'}
      </div>
      <div className="tutor-message-content">{message.content}</div>
      {message.citations?.length > 0 && (
        <>
          <div className="tutor-citations">
            {message.citations.map((citation) => {
              const citationKey = `${citation.id}-${citation.source}`;
              const isExpanded = expandedCitation === citationKey;
              return (
                <button
                  key={citationKey}
                  className={`citation-chip expandable ${isExpanded ? 'active' : ''}`}
                  onClick={() => setExpandedCitation(isExpanded ? null : citationKey)}
                  aria-expanded={isExpanded}
                  title={`Xem nội dung từ ${citation.source}`}
                >
                  <span>{citation.id}</span>
                  <ChevronRight size={11} />
                </button>
              );
            })}
          </div>
          {message.citations.map((citation) => {
            const citationKey = `${citation.id}-${citation.source}`;
            if (expandedCitation !== citationKey) return null;
            return (
              <div key={`${citationKey}-preview`} className="citation-preview">
                <div className="citation-preview-header">
                  <BookOpenCheck size={13} />
                  <div>
                    <strong>{citation.id}</strong>
                    <span>{citation.source}</span>
                  </div>
                  <button
                    onClick={() => setExpandedCitation(null)}
                    title="Đóng nội dung nguồn"
                  >
                    <X size={13} />
                  </button>
                </div>
                <p>
                  {citation.excerpt ||
                    'Nguồn này chưa có nội dung xem trước. Hãy mở transcript để kiểm tra.'}
                </p>
              </div>
            );
          })}
        </>
      )}
      {message.suggested_questions?.length > 0 && (
        <div className="assistant-followups">
          {message.suggested_questions.map((question) => (
            <button key={question} onClick={() => onQuestionSelect(question)}>
              {question}
              <ArrowRight size={12} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function EmptyChat({ mode, onSuggestion }) {
  const isStudy = mode === 'study';
  const suggestions = isStudy ? STUDY_SUGGESTIONS : QA_SUGGESTIONS;
  return (
    <div className="tutor-empty">
      <div className={`empty-icon ${isStudy ? 'study' : ''}`}>
        {isStudy ? <Brain size={24} /> : <Sparkles size={24} />}
      </div>
      <h3>{isStudy ? 'Ôn lại để nhớ lâu hơn' : 'Hỏi ngay trong lúc đọc'}</h3>
      <p>
        {isStudy
          ? 'AI sẽ gợi mở, đối chiếu và giúp bạn chủ động nhớ lại kiến thức.'
          : 'Câu trả lời chỉ dựa trên học liệu và luôn kèm nguồn kiểm chứng.'}
      </p>
      <div className="empty-suggestions">
        {suggestions.map((suggestion) => (
          <button key={suggestion} onClick={() => onSuggestion(suggestion)}>
            <span>{suggestion}</span>
            <ArrowRight size={14} />
          </button>
        ))}
      </div>
    </div>
  );
}

function QuizCompletion({
  quiz,
  answers,
  onReset,
  onRetryWeak,
  onReviewGaps,
}) {
  const correctCount = answers.filter((answer) => answer.isCorrect).length;
  const percent = Math.round((correctCount / answers.length) * 100);
  const wrongAnswers = answers.filter((answer) => !answer.isCorrect);
  const masteredObjectives = [
    ...new Set(
      answers
        .filter((answer) => answer.isCorrect)
        .map((answer) => answer.question.learning_objective)
    ),
  ];
  const gapMap = new Map();
  wrongAnswers.forEach(({ question }) => {
    const key = question.learning_objective;
    const existing = gapMap.get(key) || {
      objective: key,
      explanations: [],
      citations: new Set(),
    };
    existing.explanations.push(question.explanation);
    question.citations.forEach((citation) => existing.citations.add(citation));
    gapMap.set(key, existing);
  });
  const gaps = [...gapMap.values()].map((gap) => ({
    ...gap,
    citations: [...gap.citations],
  }));
  const status = percent >= 80
    ? 'Nắm khá chắc'
    : percent >= 60
      ? 'Đang tiến bộ'
      : 'Cần củng cố';

  return (
    <div className="quiz-completion">
      <div className="completion-hero">
        <div className={`score-ring score-${percent >= 80 ? 'high' : percent >= 60 ? 'mid' : 'low'}`}>
          <strong>{percent}%</strong>
          <span>{correctCount}/{answers.length} đúng</span>
        </div>
        <div>
          <span className="completion-eyebrow"><Trophy size={12} /> Hoàn thành</span>
          <h3>{status}</h3>
          <p>{quiz.quiz_title}</p>
        </div>
      </div>

      {gaps.length > 0 ? (
        <section className="knowledge-gap-section">
          <div className="completion-section-title">
            <span><Target size={14} /></span>
            <div>
              <h4>Kiến thức cần củng cố</h4>
              <p>Dựa trên {wrongAnswers.length} câu bạn trả lời chưa đúng.</p>
            </div>
          </div>
          <div className="knowledge-gap-list">
            {gaps.map((gap, index) => (
              <article key={gap.objective} className="knowledge-gap-card">
                <div className="gap-number">{index + 1}</div>
                <div>
                  <h5>{gap.objective}</h5>
                  <p>{gap.explanations[0]}</p>
                  <div className="tutor-citations">
                    {gap.citations.map((citation) => (
                      <span key={citation} className="citation-chip">{citation}</span>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
          <button
            className="review-gaps-button"
            onClick={() => onReviewGaps(gaps.map((gap) => gap.objective))}
          >
            <Brain size={16} />
            Ôn các phần còn hổng với AI
          </button>
        </section>
      ) : (
        <section className="perfect-result">
          <CheckCircle2 size={22} />
          <div>
            <h4>Chưa phát hiện lỗ hổng trong lượt này</h4>
            <p>Hãy thử bộ câu hỏi khó hơn để kiểm tra sâu hơn.</p>
          </div>
        </section>
      )}

      {masteredObjectives.length > 0 && (
        <section className="mastered-section">
          <h4>Phần bạn đã nắm</h4>
          {masteredObjectives.slice(0, 4).map((objective) => (
            <div key={objective}>
              <CheckCircle2 size={13} />
              <span>{objective}</span>
            </div>
          ))}
        </section>
      )}

      <div className="completion-actions">
        {wrongAnswers.length > 0 && (
          <button onClick={onRetryWeak}>
            <RotateCcw size={14} /> Làm lại câu sai
          </button>
        )}
        <button className="secondary" onClick={onReset}>Tạo bộ câu hỏi mới</button>
      </div>
    </div>
  );
}

function QuizWorkspace({ onReviewGaps }) {
  const [day, setDay] = useState('day-1');
  const [count, setCount] = useState(5);
  const [difficulty, setDifficulty] = useState('từ dễ đến khó');
  const [quiz, setQuiz] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [completed, setCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const startQuiz = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await createQuiz(
        `Tạo ${count} câu ${day === 'day-1' ? 'ngày 1' : 'ngày 2'}, mức độ ${difficulty}`
      );
      setQuiz(result);
      setQuestionIndex(0);
      setSelectedAnswer(null);
      setRevealed(false);
      setAnswers([]);
      setCompleted(false);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  const resetQuiz = () => {
    setQuiz(null);
    setQuestionIndex(0);
    setSelectedAnswer(null);
    setRevealed(false);
    setAnswers([]);
    setCompleted(false);
  };

  if (!quiz) {
    return (
      <div className="quiz-setup">
        <div className="quiz-hero">
          <div className="empty-icon quiz"><BookOpenCheck size={24} /></div>
          <div>
            <h3>Tạo phiên trắc nghiệm</h3>
            <p>Kiểm tra hiểu bài bằng câu hỏi có giải thích và citation.</p>
          </div>
        </div>

        <label className="setup-label">Nội dung</label>
        <div className="segmented-control">
          {['day-1', 'day-2'].map((value) => (
            <button
              key={value}
              className={day === value ? 'active' : ''}
              onClick={() => setDay(value)}
            >
              {value === 'day-1' ? 'Ngày 1' : 'Ngày 2'}
            </button>
          ))}
        </div>

        <label className="setup-label">Số câu</label>
        <div className="quiz-count-options">
          {[5, 10, 15].map((value) => (
            <button
              key={value}
              className={count === value ? 'active' : ''}
              onClick={() => setCount(value)}
            >
              {value}
            </button>
          ))}
        </div>

        <label className="setup-label" htmlFor="quiz-difficulty">Độ khó</label>
        <select
          id="quiz-difficulty"
          value={difficulty}
          onChange={(event) => setDifficulty(event.target.value)}
        >
          <option value="chủ yếu dễ">Chủ yếu dễ</option>
          <option value="chủ yếu trung bình">Chủ yếu trung bình</option>
          <option value="từ dễ đến khó">Từ dễ đến khó</option>
          <option value="chủ yếu khó">Chủ yếu khó</option>
        </select>

        {error && <div className="tutor-error">{error}</div>}
        <button className="start-quiz-button" onClick={startQuiz} disabled={loading}>
          {loading ? <Loader2 className="spin-icon" size={17} /> : <Sparkles size={17} />}
          {loading ? 'Đang tạo câu hỏi…' : 'Bắt đầu trắc nghiệm'}
        </button>
      </div>
    );
  }

  if (completed) {
    return (
      <QuizCompletion
        quiz={quiz}
        answers={answers}
        onReset={resetQuiz}
        onRetryWeak={() => {
          const weakQuestions = answers
            .filter((answer) => !answer.isCorrect)
            .map((answer) => answer.question);
          setQuiz((current) => ({ ...current, questions: weakQuestions }));
          setQuestionIndex(0);
          setSelectedAnswer(null);
          setRevealed(false);
          setAnswers([]);
          setCompleted(false);
        }}
        onReviewGaps={(gaps) => onReviewGaps(gaps, day)}
      />
    );
  }

  const question = quiz.questions[questionIndex];
  const isCorrect = selectedAnswer === question.correct_option_id;
  const isLast = questionIndex === quiz.questions.length - 1;

  const goNext = () => {
    if (isLast) {
      setCompleted(true);
      return;
    }
    setQuestionIndex((current) => current + 1);
    setSelectedAnswer(null);
    setRevealed(false);
  };

  const revealAnswer = () => {
    setAnswers((current) => [
      ...current,
      {
        question,
        selectedAnswer,
        isCorrect,
      },
    ]);
    setRevealed(true);
  };

  return (
    <div className="quiz-session">
      <div className="quiz-session-header">
        <div>
          <span>Câu {questionIndex + 1}/{quiz.questions.length}</span>
          <strong>{question.difficulty}</strong>
        </div>
        <button onClick={resetQuiz} title="Tạo phiên mới"><RotateCcw size={15} /></button>
      </div>
      <div className="quiz-progress">
        <span style={{ width: `${((questionIndex + 1) / quiz.questions.length) * 100}%` }} />
      </div>
      <h3 className="quiz-question">{question.question}</h3>
      <div className="quiz-options">
        {question.options.map((option) => {
          const isSelected = selectedAnswer === option.id;
          const isAnswer = revealed && option.id === question.correct_option_id;
          const isWrong = revealed && isSelected && !isAnswer;
          return (
            <button
              key={option.id}
              className={`${isSelected ? 'selected' : ''} ${isAnswer ? 'correct' : ''} ${isWrong ? 'wrong' : ''}`}
              onClick={() => !revealed && setSelectedAnswer(option.id)}
            >
              <span className="option-id">{option.id}</span>
              <span>{option.text}</span>
              {isAnswer && <Check size={16} />}
            </button>
          );
        })}
      </div>
      {!revealed ? (
        <button
          className="check-answer-button"
          disabled={!selectedAnswer}
          onClick={revealAnswer}
        >
          Kiểm tra đáp án
        </button>
      ) : (
        <div className={`quiz-explanation ${isCorrect ? 'correct' : 'wrong'}`}>
          <strong>{isCorrect ? 'Chính xác' : 'Chưa chính xác'}</strong>
          <p>{question.explanation}</p>
          <div className="tutor-citations">
            {question.citations.map((citation) => (
              <span key={citation} className="citation-chip">{citation}</span>
            ))}
          </div>
          <button onClick={goNext}>
            {isLast ? 'Xem tổng kết' : 'Câu tiếp theo'}
            {isLast ? <Target size={14} /> : <ChevronRight size={14} />}
          </button>
        </div>
      )}
    </div>
  );
}

export default function AiTutorPanel({
  mode,
  onModeChange,
  selection,
  onClearSelection,
  currentDay,
  onClose,
}) {
  const [qaMessages, setQaMessages] = useState([]);
  const [studyMessages, setStudyMessages] = useState([]);
  const [studyDay, setStudyDay] = useState(currentDay);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const messages = mode === 'study' ? studyMessages : qaMessages;
  const setMessages = mode === 'study' ? setStudyMessages : setQaMessages;

  useEffect(() => {
    if (mode !== 'quiz') inputRef.current?.focus();
  }, [mode, selection]);

  useEffect(() => {
    const textarea = inputRef.current;
    if (!textarea || mode === 'quiz') return;
    textarea.style.height = 'auto';
    const nextHeight = Math.min(Math.max(textarea.scrollHeight, 24), 120);
    textarea.style.height = `${nextHeight}px`;
    textarea.style.overflowY = textarea.scrollHeight > 120 ? 'auto' : 'hidden';
  }, [input, mode]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    setStudyDay(currentDay);
  }, [currentDay]);

  const submitMessage = async (text = input) => {
    const cleanText = text.trim();
    if (!cleanText || loading || mode === 'quiz') return;
    const priorMessages = messages;
    const userMessage = { role: 'user', content: cleanText };
    setMessages([...priorMessages, userMessage]);
    setInput('');
    setLoading(true);
    setError('');
    try {
      const result = mode === 'study'
        ? await askStudyReview({
            message: cleanText,
            day: studyDay,
            history: toHistory(priorMessages),
          })
        : await askKnowledge({
            message: cleanText,
            history: toHistory(priorMessages),
            selection,
          });
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: result.answer,
          citations: result.citations,
          suggested_questions: result.suggested_questions,
          blocked: result.blocked,
          guardrailCode: result.guardrail_code,
          needsClarification: result.needs_clarification,
        },
      ]);
      if (mode === 'qa' && selection) onClearSelection();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  };

  const reviewKnowledgeGaps = (gaps, quizDay) => {
    setStudyDay(quizDay);
    setInput(
      `Mình vừa làm xong trắc nghiệm và cần ôn lại các phần sau: ${gaps
        .slice(0, 5)
        .join('; ')}. Hãy giúp mình ôn từng phần bằng câu hỏi gợi mở.`
    );
    onModeChange('study');
  };

  return (
    <aside className="ai-tutor-panel" aria-label="VLearn AI Tutor">
      <div className="tutor-panel-header">
        <div className="tutor-title">
          <span><Sparkles size={15} /></span>
          <div>
            <strong>VLearn AI</strong>
            <small>Học cùng nguồn đáng tin cậy</small>
          </div>
        </div>
        <button className="tutor-close" onClick={onClose} title="Đóng AI Tutor">
          <X size={18} />
        </button>
      </div>

      <div className="tutor-tabs">
        <button className={mode === 'qa' ? 'active' : ''} onClick={() => onModeChange('qa')}>
          <MessageSquareText size={14} /> Hỏi đáp
        </button>
        <button className={mode === 'study' ? 'active' : ''} onClick={() => onModeChange('study')}>
          <Brain size={14} /> Ôn tập
        </button>
        <button className={mode === 'quiz' ? 'active' : ''} onClick={() => onModeChange('quiz')}>
          <HelpCircle size={14} /> Trắc nghiệm
        </button>
      </div>

      <div className="learning-scope-banner">
        <ShieldCheck size={13} />
        <span>Chỉ trả lời nội dung học tập từ học liệu VLearn</span>
      </div>

      {mode === 'quiz' ? (
        <div className="tutor-panel-body quiz-body">
          <QuizWorkspace onReviewGaps={reviewKnowledgeGaps} />
        </div>
      ) : (
        <>
          {mode === 'study' && (
            <div className="study-day-picker">
              <span>Phạm vi ôn tập</span>
              <div>
                {['day-1', 'day-2'].map((day) => (
                  <button
                    key={day}
                    className={studyDay === day ? 'active' : ''}
                    onClick={() => setStudyDay(day)}
                  >
                    {day === 'day-1' ? 'Ngày 1' : 'Ngày 2'}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="tutor-messages">
            {messages.length === 0 ? (
              <EmptyChat mode={mode} onSuggestion={submitMessage} />
            ) : (
              messages.map((message, index) => (
                <ChatMessage
                  key={`${message.role}-${index}`}
                  message={message}
                  onQuestionSelect={submitMessage}
                />
              ))
            )}
            {loading && (
              <div className="tutor-thinking">
                <Loader2 className="spin-icon" size={15} />
                Đang đối chiếu học liệu…
              </div>
            )}
            {error && <div className="tutor-error">{error}</div>}
            <div ref={messagesEndRef} />
          </div>

          <div className="tutor-composer">
            {mode === 'qa' && selection && (
              <div className="selection-context">
                <div>
                  <span>Đoạn đã chọn · Trang {selection.page}</span>
                  <p>“{selection.text}”</p>
                </div>
                <button onClick={onClearSelection} title="Bỏ đoạn đã chọn"><X size={14} /></button>
              </div>
            )}
            <div className="composer-row">
              <textarea
                ref={inputRef}
                rows={1}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                maxLength={4000}
                placeholder={
                  mode === 'study'
                    ? 'Bạn muốn ôn lại nội dung nào?'
                    : selection
                      ? 'Hỏi về đoạn vừa chọn…'
                      : 'Hỏi về kiến thức trong bài…'
                }
              />
              <button
                className="send-button"
                onClick={() => submitMessage()}
                disabled={!input.trim() || loading}
                title="Gửi câu hỏi"
              >
                <Send size={16} />
              </button>
            </div>
            <div className="composer-meta">
              <small>Enter để gửi · Shift + Enter để xuống dòng</small>
              <span>{input.length}/4000</span>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}

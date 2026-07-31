const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '');

async function request(path, body) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 90000);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(
        typeof payload.detail === 'string'
          ? payload.detail
          : 'VLearn AI chưa thể xử lý yêu cầu này.'
      );
    }
    return payload;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu mất quá nhiều thời gian. Hãy thử lại.');
    }
    if (error instanceof TypeError) {
      throw new Error(
        'Không kết nối được backend. Hãy kiểm tra server tại cổng 8000.'
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export function askKnowledge({ message, history, selection }) {
  return request('/api/v1/agents/direct-qa/chat', {
    message,
    history,
    ...(selection ? { selection } : {}),
  });
}

export function askStudyReview({ message, day, history }) {
  return request('/api/v1/agents/study/review', {
    message,
    history,
    ...(day ? { day } : {}),
  });
}

export function createQuiz(requestText) {
  return request('/api/v1/agents/study/quiz', { request: requestText });
}


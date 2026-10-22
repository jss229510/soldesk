/** Python 챗봇 서버(8000번) 호출. Vite 프록시가 /pyapi 를 8000번으로 넘겨준다. */
const CHAT_BASE_URL = import.meta.env?.VITE_CHAT_BASE_URL ?? '/pyapi';
// LLM 답변은 몇 초 걸릴 수 있다 → 최대 30초까지 기다린다.
const TIMEOUT_MS = 30000;

const SERVER_DOWN_MESSAGE = '챗봇 서버에 연결하지 못했습니다. 8000번 Python 서버가 실행 중인지 확인하세요.';

/**
 * 챗봇에게 질문하기 (POST /pyapi/chat)
 * @param {Array<{role: 'user'|'assistant', content: string}>} messages 지금까지의 대화 전체
 * @param {string} accessToken 로그인 JWT (Python 서버가 Spring 에 확인한다)
 * @returns {Promise<string>} 챗봇 답변
 */
export const sendChat = async (messages, accessToken) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${CHAT_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ messages }),
      signal: controller.signal,
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(typeof data?.detail === 'string' ? data.detail : SERVER_DOWN_MESSAGE);
    }
    return data.reply;
  } catch (err) {
    if (err.name === 'AbortError') throw new Error('답변이 너무 오래 걸려요. 잠시 후 다시 시도해 주세요.', { cause: err });
    if (err instanceof TypeError) throw new Error(SERVER_DOWN_MESSAGE, { cause: err });
    throw err;
  } finally {
    clearTimeout(timer);
  }
};

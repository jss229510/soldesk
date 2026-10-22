import { useEffect, useRef, useState } from 'react';
import { sendChat } from '../../api/chat';

// 챗봇 이름 (Python .env 의 BOT_NAME 과 맞춰 두면 좋다)
const BOT_NAME = '파츠봇';
// 입력 최대 글자 수 (Python main.py 의 MAX_QUESTION_LENGTH 와 같은 값)
const MAX_LENGTH = 500;

// 기본 질문 버튼. followUp 이 있으면 서버에 보내지 않고 연계 질문을 먼저 띄운다.
const QUESTIONS = [
  {
    label: '최근 자주 사용하는 컴퓨터 조합',
    send: '최근 자주 사용하는 컴퓨터 조합을 알려 주세요.',
  },
  {
    label: '잘나가는 부품 추천',
    followUp: {
      question: '구매를 원하는 부품은 무엇인가요?',
      options: [
        { label: 'CPU', send: 'CPU 중에서 요즘 제일 잘나가는 제품을 추천해 주세요.' },
        { label: '그래픽카드', send: '그래픽카드(GPU) 중에서 요즘 제일 잘나가는 제품을 추천해 주세요.' },
        { label: 'SSD', send: 'SSD 중에서 요즘 제일 잘나가는 제품을 추천해 주세요.' },
        { label: '램', send: '램(RAM) 중에서 요즘 제일 잘나가는 제품을 추천해 주세요.' },
        { label: '파워', send: '파워(PSU) 중에서 요즘 제일 잘나가는 제품을 추천해 주세요.' },
      ],
    },
  },
  {
    label: '구매 목적별 추천',
    followUp: {
      question: '구매 목적이 무엇인가요?',
      options: [
        { label: '사무', send: '사무용 PC 조합을 추천해 주세요.' },
        { label: '디자인', send: '디자인(영상편집·그래픽 작업)용 PC 조합을 추천해 주세요.' },
        { label: '방송', send: '방송(스트리밍)용 PC 조합을 추천해 주세요.' },
        { label: '게이밍', send: '게이밍용 PC 조합을 추천해 주세요.' },
      ],
    },
  },
];

// 화면 전용 정보(options)는 빼고 서버에 보낼 대화만 남긴다.
const toHistory = (messages) => messages.map(({ role, content }) => ({ role, content }));

/**
 * 오른쪽 아래에 떠 있는 챗봇.
 * MainLayout 에 한 번만 넣으면 모든 페이지에서 보인다.
 * 로그인한 회원만 대화할 수 있다 (OpenAI 비용 보호).
 */
export const ChatWidget = ({ user, onLogin }) => {
  const [open, setOpen] = useState(false);
  // 대화 기록 : [{ role: 'user'|'assistant', content, options? }, ...]
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const listRef = useRef(null);

  // 메시지가 늘어나거나 "답변 중" 표시가 바뀌면 맨 아래로 스크롤
  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, sending]);

  /** 질문을 서버에 보낸다. label 은 말풍선에 보일 글 (없으면 text 그대로) */
  const send = async (text, label = text) => {
    const question = text.trim();
    if (question === '' || sending) return;

    const shown = [...messages, { role: 'user', content: label }];
    const history = [...toHistory(messages), { role: 'user', content: question }];
    setMessages(shown);
    setInput('');
    setError('');
    setSending(true);

    try {
      const reply = await sendChat(history, user.accessToken);
      setMessages([...shown, { role: 'assistant', content: reply }]);
    } catch (err) {
      // 실패하면 방금 질문을 기록에서 빼고 입력창에 되돌려 놓는다 → 다시 보내기 쉬움
      setMessages(messages);
      setInput(label === text ? question : '');
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  /** 기본 질문 버튼 클릭 */
  const pickQuestion = (q) => {
    if (sending) return;
    if (!q.followUp) {
      send(q.send, q.label);
      return;
    }
    // 연계 질문 : 서버를 거치지 않고 화면에서 바로 선택지를 띄운다
    setError('');
    setMessages([
      ...messages,
      { role: 'user', content: q.label },
      { role: 'assistant', content: q.followUp.question, options: q.followUp.options },
    ]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    send(input);
  };

  const handleReset = () => {
    setMessages([]);
    setError('');
  };

  const handleLogin = () => {
    setOpen(false);
    onLogin?.();
  };

  // 마지막 말풍선이 연계 질문이면 그 선택지를, 아니면 기본 질문을 버튼으로 보여준다
  const last = messages[messages.length - 1];
  const followOptions = last?.options;

  return (
    <>
      {open && (
        <section className="chat-panel" aria-label={`${BOT_NAME} 대화창`}>
          <header className="chat-head">
            <div>
              <b>{BOT_NAME}</b>
              <span className="chat-sub">PC 부품 추천 도우미</span>
            </div>
            <div className="chat-head-btns">
              {messages.length > 0 && (
                <button type="button" className="chat-icon-btn" onClick={handleReset}>
                  새 대화
                </button>
              )}
              <button
                type="button"
                className="chat-icon-btn"
                onClick={() => setOpen(false)}
                aria-label="대화창 닫기"
              >
                ✕
              </button>
            </div>
          </header>

          {!user ? (
            <div className="chat-body chat-guest">
              <p>{BOT_NAME}은 로그인한 회원만 사용할 수 있어요.</p>
              <button type="button" className="chat-login-btn" onClick={handleLogin}>
                로그인하러 가기
              </button>
            </div>
          ) : (
            <>
              <div className="chat-body" ref={listRef}>
                <div className="chat-bubble bot">
                  {user.nickname ?? '회원'}님, 안녕하세요! PartZone 판매 데이터로
                  PC 조합과 부품을 추천해 드릴게요. 아래에서 골라 보세요.
                </div>

                {messages.map((m, i) => (
                  <div key={i} className={m.role === 'user' ? 'chat-bubble me' : 'chat-bubble bot'}>
                    {m.content}
                  </div>
                ))}

                {sending && <div className="chat-bubble bot chat-typing">답변을 만드는 중…</div>}

                {!sending && (
                  <div className="chat-suggest">
                    {followOptions
                      ? followOptions.map((o) => (
                        <button key={o.label} type="button" onClick={() => send(o.send, o.label)}>
                          {o.label}
                        </button>
                      ))
                      : QUESTIONS.map((q) => (
                        <button key={q.label} type="button" onClick={() => pickQuestion(q)}>
                          {q.label}
                        </button>
                      ))}
                  </div>
                )}
              </div>

              {error && <p className="chat-error">{error}</p>}

              <form className="chat-form" onSubmit={handleSubmit}>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`${BOT_NAME}에게 물어보세요`}
                  maxLength={MAX_LENGTH}
                  disabled={sending}
                  aria-label="질문 입력"
                  autoComplete="off"
                />
                <button type="submit" disabled={sending || input.trim() === ''}>
                  보내기
                </button>
              </form>
            </>
          )}
        </section>
      )}

      <button
        type="button"
        className="chat-fab"
        onClick={() => setOpen(!open)}
        aria-label={open ? `${BOT_NAME} 닫기` : `${BOT_NAME} 열기`}
      >
        {open ? '✕' : BOT_NAME}
      </button>
    </>
  );
};

export default ChatWidget;

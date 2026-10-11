import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  // 이메일 입력값과 안내 문구
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const emailRef = useRef();

  const onSubmit = (event) => {
    // 제출 시 새로고침 방지
    event.preventDefault();
    setError("");
    setMessage("");
    // 이메일 빈칸 확인
    if (!email.trim()) {
      setError("가입한 이메일을 입력해주세요.");
      emailRef.current.focus();
      return;
    }
    // 이메일 형식 확인
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("올바른 이메일 형식으로 입력해주세요.");
      emailRef.current.focus();
      return;
    }
    // 메일 발송 API는 아직 연결하지 않음
    setMessage("메일 발송 기능은 준비 중입니다. 현재는 입력 화면만 이용할 수 있습니다.");
  };

  const goLogin = () => {
    // 로그인으로 이동
    navigate("/login");
  };

  return (
    <div className="flex justify-center px-4 py-8">
      <form
        noValidate
        onSubmit={onSubmit}
        className="w-full max-w-sm rounded-xl border p-5 shadow-lg"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--line)",
          color: "var(--text)",
        }}
      >
        <h2 className="text-center text-2xl font-bold">비밀번호 찾기</h2>
        <p className="mb-5 mt-2 text-center text-sm" style={{ color: "var(--text-2)" }}>
          가입할 때 사용한 이메일을 입력해주세요.
        </p>
        <label htmlFor="reset-email" className="mb-1 block text-sm font-medium">이메일</label>
        <input
          id="reset-email"
          ref={emailRef}
          name="email"
          type="email"
          autoComplete="email"
          maxLength={255}
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
            setError("");
            setMessage("");
          }}
          placeholder="가입한 이메일을 입력하세요"
          aria-invalid={Boolean(error)}
          aria-describedby={error ? "reset-error" : "reset-note"}
          className="w-full rounded-lg border px-3 py-2 outline-none"
          style={{ backgroundColor: "var(--bg-surface-2)", borderColor: "var(--line)", color: "var(--text)" }}
        />
        <p id="reset-note" className="mt-2 text-xs" style={{ color: "var(--text-2)" }}>비밀번호 재설정 메일 발송은 준비 중입니다.</p>
        {error && <p id="reset-error" role="alert" className="mt-3 text-sm text-red-500">{error}</p>}
        {message && <p role="status" className="mt-3 rounded-lg border border-cyan-400 bg-cyan-950 p-3 text-sm text-cyan-400">{message}</p>}
        <button type="submit" className="mt-5 w-full rounded-lg bg-cyan-500 py-2.5 font-semibold text-gray-950 hover:bg-cyan-400">
          재설정 메일 요청
        </button>
        <button
          type="button"
          onClick={goLogin}
          className="mt-3 w-full rounded-lg border py-2.5 text-sm"
          style={{ borderColor: "var(--line)", color: "var(--text-2)" }}
        >
          로그인으로 돌아가기
        </button>
      </form>
    </div>
  );
};

export default ForgotPasswordPage;

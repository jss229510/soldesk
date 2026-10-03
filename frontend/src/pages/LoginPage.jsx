import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/users";

const LoginPage = ({ onNavigate, onSuccess }) => {
  const navigate = useNavigate();

  const [input, setInput] = useState({
    email: "",
    password: "",
  });

  const emailRef = useRef();
  const passwordRef = useRef();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onChange = (e) => {
    setInput({
      ...input,
      [e.target.name]: e.target.value,
    });
  };

  const onSubmit = async () => {
    if (loading) return;
    setError("");
    // 이메일 빈칸 확인
    if (!input.email.trim()) {
      alert("이메일을 입력해주세요.");
      emailRef.current.focus();
      return;
    }

    // 이메일 형식 확인
    if (!input.email.includes("@")) {
      alert("올바른 이메일 형식으로 입력해주세요.");
      emailRef.current.focus();
      return;
    }

    // 비밀번호 빈칸 확인
    if (!input.password.trim()) {
      alert("비밀번호를 입력해주세요.");
      passwordRef.current.focus();
      return;
    }

    // 서버가 계정과 비밀번호를 확인한 경우에만 로그인 성공 처리한다.
    setLoading(true);
    try {
      const user = await loginUser(input.email.trim(), input.password);
      setInput({ email: "", password: "" });
      onSuccess?.(user);
    } catch (err) {
      setError(err.status === 401
        ? "이메일 또는 비밀번호가 올바르지 않습니다."
        : err.status === 400
          ? "이메일과 비밀번호를 확인해주세요."
          : "로그인 서버에 연결하지 못했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const onRegister = () => {
    onNavigate?.();
    navigate("/register");
  };

  return (
    <div className="h-full">
      <div
        className="flex h-full w-full flex-col justify-center rounded-xl border p-4 shadow-md"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--line)",
          color: "var(--text)",
        }}
      >
        <div className="mb-4 text-center">
          <h2 id="login-title" className="text-lg font-bold">
            로그인
          </h2>

          <p
            className="mt-1 text-xs"
            style={{ color: "var(--text-2)" }}
          >
            PartZone에 로그인하세요
          </p>
        </div>

        <input
          ref={emailRef}
          autoFocus
          name="email"
          type="email"
          value={input.email}
          onChange={onChange}
          placeholder="이메일"
          className="mb-3 w-full rounded-lg border px-3 py-2 text-sm outline-none"
          style={{
            backgroundColor: "var(--bg-surface-2)",
            borderColor: "var(--line)",
            color: "var(--text)",
          }}
        />

        <input
          ref={passwordRef}
          name="password"
          type="password"
          value={input.password}
          onChange={onChange}
          placeholder="비밀번호"
          className="mb-4 w-full rounded-lg border px-3 py-2 text-sm outline-none"
          style={{
            backgroundColor: "var(--bg-surface-2)",
            borderColor: "var(--line)",
            color: "var(--text)",
          }}
        />

        {error && <p role="alert" className="mb-3 text-sm text-red-500">{error}</p>}

        <button
          type="button"
          onClick={onSubmit}
          disabled={loading}
          className="w-full rounded-lg bg-cyan-500 py-2 text-sm font-semibold text-gray-950 hover:bg-cyan-400"
        >
          {loading ? "로그인 중..." : "로그인"}
        </button>

        <div className="mt-4 flex justify-center gap-3 text-xs">
          <button
            type="button"
            onClick={onRegister}
            style={{ color: "var(--text-2)" }}
          >
            회원가입
          </button>

          <button
            type="button"
            onClick={() => {
              onNavigate?.();
              navigate("/forgot-password");
            }}
            style={{ color: "var(--text-2)" }}
          >
            비밀번호 찾기
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { signupUser } from "../api/users";

const RegisterPage = () => {
  const navigate = useNavigate();

  const [input, setInput] = useState({
    email: "",
    password: "",
    passwordCheck: "",
    nickname: "",
  });

  const emailRef = useRef();
  const passwordRef = useRef();
  const passwordCheckRef = useRef();
  const nicknameRef = useRef();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onChange = (e) => {
    setInput({
      ...input,
      [e.target.name]: e.target.value,
    });
  };

  const onSubmit = async (event) => {
    event.preventDefault();
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

    // 서버의 회원가입 규칙과 동일하게 영문·숫자·8~20자·공백 없음 여부를 확인한다.
    if (!/^(?=.*[A-Za-z])(?=.*\d)\S{8,20}$/.test(input.password)) {
      alert("비밀번호는 영문과 숫자를 포함해 공백 없이 8~20자로 입력해주세요.");
      passwordRef.current.focus();
      return;
    }

    // 비밀번호 확인
    if (!input.passwordCheck.trim()) {
      alert("비밀번호를 한 번 더 입력해주세요.");
      passwordCheckRef.current.focus();
      return;
    }

    // 비밀번호 일치 확인
    if (input.password !== input.passwordCheck) {
      alert("비밀번호가 일치하지 않습니다.");
      passwordCheckRef.current.focus();
      return;
    }

    // 닉네임 확인
    if (!input.nickname.trim()) {
      alert("닉네임을 입력해주세요.");
      nicknameRef.current.focus();
      return;
    }

    setLoading(true);
    try {
      await signupUser({
        email: input.email.trim(),
        password: input.password,
        nickname: input.nickname.trim(),
      });
      alert("회원가입이 완료되었습니다. 로그인해주세요.");
      navigate("/login");
    } catch (err) {
      const firstFieldError = Object.values(err.errors ?? {})[0];
      setError(firstFieldError ?? err.message);
    } finally {
      setLoading(false);
    }
  };

  const goLogin = () => {
    navigate("/login");
  };

  return (
    <div className="flex justify-center px-4 py-8">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm rounded-xl border p-5 shadow-lg"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--line)",
          color: "var(--text)",
        }}
      >
        <div className="mb-5 text-center">
          <h2 className="text-2xl font-bold">
            회원가입
          </h2>

          <p
            className="mt-1 text-sm"
            style={{ color: "var(--text-2)" }}
          >
            PartZone 계정을 만들어보세요
          </p>
        </div>

        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">
            이메일
          </label>

          <input
            ref={emailRef}
            name="email"
            type="email"
            value={input.email}
            onChange={onChange}
            placeholder="이메일을 입력하세요"
            className="w-full rounded-lg border px-3 py-2 outline-none"
            style={{
              backgroundColor: "var(--bg-surface-2)",
              borderColor: "var(--line)",
              color: "var(--text)",
            }}
          />
        </div>

        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">
            비밀번호
          </label>

          <input
            ref={passwordRef}
            name="password"
            type="password"
            value={input.password}
            onChange={onChange}
            placeholder="8자 이상 입력하세요"
            className="w-full rounded-lg border px-3 py-2 outline-none"
            style={{
              backgroundColor: "var(--bg-surface-2)",
              borderColor: "var(--line)",
              color: "var(--text)",
            }}
          />
        </div>

        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">
            비밀번호 확인
          </label>

          <input
            ref={passwordCheckRef}
            name="passwordCheck"
            type="password"
            value={input.passwordCheck}
            onChange={onChange}
            placeholder="비밀번호를 다시 입력하세요"
            className="w-full rounded-lg border px-3 py-2 outline-none"
            style={{
              backgroundColor: "var(--bg-surface-2)",
              borderColor: "var(--line)",
              color: "var(--text)",
            }}
          />
        </div>

        <div className="mb-5">
          <label className="mb-1 block text-sm font-medium">
            닉네임
          </label>

          <input
            ref={nicknameRef}
            name="nickname"
            type="text"
            value={input.nickname}
            onChange={onChange}
            placeholder="닉네임을 입력하세요"
            className="w-full rounded-lg border px-3 py-2 outline-none"
            style={{
              backgroundColor: "var(--bg-surface-2)",
              borderColor: "var(--line)",
              color: "var(--text)",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg py-2.5 font-semibold"
          style={{
            border: "1px solid #ccc",
            backgroundColor: "#fff",
            color: "#0f172a",
            boxShadow: "0 2px 4px rgba(15, 23, 42, 0.12)",
          }}
        >
          {loading ? "회원가입 중..." : "회원가입"}
        </button>

        {error && <p role="alert" className="mt-3 text-sm text-red-500">{error}</p>}

        <button
          type="button"
          onClick={goLogin}
          className="mt-3 w-full text-center text-sm"
          style={{ color: "var(--text-2)" }}
        >
          이미 계정이 있으신가요? 로그인
        </button>
      </form>
    </div>
  );
};

export default RegisterPage;

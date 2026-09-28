import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const navigate = useNavigate();

  const [input, setInput] = useState({
    email: "",
    password: "",
  });

  const emailRef = useRef();
  const passwordRef = useRef();

  const onChange = (e) => {
    setInput({
      ...input,
      [e.target.name]: e.target.value,
    });
  };

  const onSubmit = () => {
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

    // 비밀번호 길이 확인
    if (input.password.length < 8) {
      alert("비밀번호는 8자 이상 입력해주세요.");
      passwordRef.current.focus();
      return;
    }

    // 프론트 확인용
    console.log(input);
    alert("로그인 정보 확인 완료!");
  };

  const onRegister = () => {
    navigate("/register");
  };

  return (
    <div className="h-full">
      <div
        className="flex h-full w-64 flex-col justify-center rounded-xl border p-4 shadow-md"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--line)",
          color: "var(--text)",
        }}
      >
        <div className="mb-4 text-center">
          <h2 className="text-lg font-bold">
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

        <button
          type="button"
          onClick={onSubmit}
          className="w-full rounded-lg bg-cyan-500 py-2 text-sm font-semibold text-gray-950 hover:bg-cyan-400"
        >
          로그인
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
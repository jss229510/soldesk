import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

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

    console.log(input);

    alert("회원가입 정보 확인 완료!");

    // 나중에 여기에 백엔드 연결
  };

  const goLogin = () => {
    navigate("/login");
  };

  return (
    <div className="flex justify-center px-4 py-8">
      <div
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
          type="button"
          onClick={onSubmit}
          className="w-full rounded-lg bg-cyan-500 py-2.5 font-semibold text-gray-950 hover:bg-cyan-400"
        >
          회원가입
        </button>

        <button
          type="button"
          onClick={goLogin}
          className="mt-3 w-full text-center text-sm"
          style={{ color: "var(--text-2)" }}
        >
          이미 계정이 있으신가요? 로그인
        </button>
      </div>
    </div>
  );
};

export default RegisterPage;
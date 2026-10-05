import { useNavigate } from "react-router-dom";

const ForgotPasswordPage = () => {
  const navigate = useNavigate();

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
        <h2 className="text-center text-2xl font-bold">비밀번호 찾기</h2>
        <p className="mt-4 text-sm" style={{ color: "var(--text-2)" }}>
          비밀번호 재설정 메일 발송 기능은 준비 중입니다.
          계정 접근이 필요하면 고객센터에 문의해주세요.
        </p>
        <button
          type="button"
          onClick={goLogin}
          className="mt-6 w-full rounded-lg bg-cyan-500 py-2.5 font-semibold text-gray-950 hover:bg-cyan-400"
        >
          로그인으로 돌아가기
        </button>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;

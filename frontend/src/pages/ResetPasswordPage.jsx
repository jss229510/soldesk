import { useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { resetPassword } from "../api/users";

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  // 메일 링크에 있는 일회용 토큰
  const token = new URLSearchParams(location.hash.slice(1)).get("token");
  const [password, setPassword] = useState("");
  const [passwordCheck, setPasswordCheck] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const passwordRef = useRef();
  const checkRef = useRef();

  const onSubmit = async (event) => {
    event.preventDefault();
    if (loading) return;
    setError("");
    if (!token) {
      setError("메일의 재설정 링크로 다시 접속해주세요.");
      return;
    }
    if (!password.trim() || password.length < 8 || new TextEncoder().encode(password).length > 72) {
      setError("비밀번호는 8자 이상, 72바이트 이내로 입력해주세요.");
      passwordRef.current.focus();
      return;
    }
    if (password !== passwordCheck) {
      setError("비밀번호가 일치하지 않습니다.");
      checkRef.current.focus();
      return;
    }
    setLoading(true);
    try {
      await resetPassword(token, password);
      sessionStorage.removeItem("partzone-login");
      setPassword("");
      setPasswordCheck("");
      alert("비밀번호가 변경되었습니다. 새 비밀번호로 로그인해주세요.");
      // 기존 로그인 상태도 초기화
      window.location.replace("/login");
    } catch (err) {
      setError(err.status === 400
        ? "만료되었거나 사용할 수 없는 링크입니다. 메일을 다시 요청해주세요."
        : "비밀번호 변경에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = { backgroundColor: "var(--bg-surface-2)", borderColor: "var(--line)", color: "var(--text)" };
  return (
    <div className="flex justify-center px-4 py-8">
      <form noValidate onSubmit={onSubmit} className="w-full max-w-sm rounded-xl border p-5 shadow-lg"
        style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--line)", color: "var(--text)" }}>
        <h2 className="text-center text-2xl font-bold">비밀번호 재설정</h2>
        <p className="mb-5 mt-2 text-center text-sm" style={{ color: "var(--text-2)" }}>새 비밀번호를 입력해주세요.</p>
        {!token && <p role="alert" className="mb-3 text-sm text-red-500">메일의 재설정 링크로 접속해주세요.</p>}
        <label htmlFor="new-password" className="mb-1 block text-sm font-medium">새 비밀번호</label>
        <input id="new-password" ref={passwordRef} type="password" autoComplete="new-password"
          value={password} onChange={(event) => setPassword(event.target.value)} disabled={loading}
          className="mb-4 w-full rounded-lg border px-3 py-2" style={inputStyle} />
        <label htmlFor="password-check" className="mb-1 block text-sm font-medium">비밀번호 확인</label>
        <input id="password-check" ref={checkRef} type="password" autoComplete="new-password"
          value={passwordCheck} onChange={(event) => setPasswordCheck(event.target.value)} disabled={loading}
          className="w-full rounded-lg border px-3 py-2" style={inputStyle} />
        {error && <p role="alert" className="mt-3 text-sm text-red-500">{error}</p>}
        <button type="submit" disabled={loading || !token}
          className="mt-5 w-full rounded-lg bg-cyan-500 py-2.5 font-semibold text-gray-950 hover:bg-cyan-400 disabled:opacity-60">
          {loading ? "변경 중..." : "비밀번호 변경"}
        </button>
        <button type="button" onClick={() => navigate("/forgot-password")}
          className="mt-3 w-full rounded-lg border py-2.5 text-sm" style={{ borderColor: "var(--line)", color: "var(--text-2)" }}>
          재설정 메일 다시 요청
        </button>
      </form>
    </div>
  );
};

export default ResetPasswordPage;

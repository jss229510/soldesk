import { request } from './client';

// 회원가입 요청: 이메일, 비밀번호, 닉네임 전달
export const registerUser = (email, password, nickname) => request('/users', {
  method: 'POST',
  body: JSON.stringify({ email, password, nickname }),
});

// 주소에 넣을 이메일은 encodeURIComponent로 변환
export const checkEmail = (email) => request(`/users/check-email?email=${encodeURIComponent(email)}`);
export const checkNickname = (nickname) => request(`/users/check-nickname?nickname=${encodeURIComponent(nickname)}`);

// 로그인은 실제 서버 사용
export const loginUser = (email, password) => request('/users/login', {
  method: 'POST',
  body: JSON.stringify({ email, password }),
});

// JWT로 로그인한 회원 확인
export const fetchCurrentUser = (accessToken) => request('/users/me', {
  headers: { Authorization: `Bearer ${accessToken}` },
});

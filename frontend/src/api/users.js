import { request } from './client';

// 로그인은 mock 설정과 관계없이 실제 서버에 요청한다.
export const loginUser = (email, password) => request('/users/login', {
  method: 'POST',
  body: JSON.stringify({ email, password }),
});

export const fetchCurrentUser = (accessToken) => request('/users/me', {
  headers: { Authorization: `Bearer ${accessToken}` },
});

/**
 * API 클라이언트.
 * 지금은 mock 데이터를 지연시켜 돌려주고, 실제 서버가 준비되면
 * USE_MOCK 을 false 로 두고 request() 만 실제 fetch 로 바꾸면 된다.
 */
export const BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? '/api';
export const USE_MOCK = import.meta.env?.VITE_USE_MOCK !== 'false';

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

/** mock 응답을 실제 네트워크처럼 감싼다. */
export const mockResponse = async (data, ms = 220) => {
  await delay(ms);
  return structuredClone(data);
};

export const request = async (path, options = {}) => {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!response.ok) {
    throw new ApiError('요청을 처리하지 못했습니다.', response.status);
  }

  return response.json();
};

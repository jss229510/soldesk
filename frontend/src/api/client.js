/**
 * API 클라이언트.
 * 부품 조회는 실제 API를 사용하고 예산 추천 등은 기존 mock 설정을 따른다.
 */
export const BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? '/api';
export const USE_MOCK = import.meta.env?.VITE_USE_MOCK !== 'false';
// 부품 조회만 실제 서버에 연결한다. 예산 추천은 기존 설정을 유지한다.
export const USE_REAL_PARTS = import.meta.env?.VITE_USE_REAL_PARTS === 'true';

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

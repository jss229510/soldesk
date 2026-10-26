/** Shared JSON API client and mock-response helpers. */
export const BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? '/api';
export const USE_MOCK = import.meta.env?.VITE_USE_MOCK !== 'false';

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class ApiError extends Error {
  constructor(message, status, errors = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errors = errors && typeof errors === 'object' && !Array.isArray(errors)
      ? errors
      : {};
  }
}

/** mock 응답을 실제 네트워크처럼 감싼다. */
export const mockResponse = async (data, ms = 220) => {
  await delay(ms);
  return structuredClone(data);
};

export const request = async (path, options = {}) => {
  const headers = new Headers(options.headers);

  // FormData는 브라우저가 multipart boundary를 포함한 Content-Type을 직접 설정해야 한다.
  if (options.body != null && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) return null;

  const text = await response.text();
  let data = null;

  if (text.trim()) {
    try {
      data = JSON.parse(text);
    } catch {
      // Preserve HTTP error status even when a proxy returns HTML instead of JSON.
      if (response.ok) {
        throw new ApiError('서버 응답이 올바른 JSON 형식이 아닙니다.', response.status);
      }
    }
  }

  if (!response.ok) {
    const message = typeof data?.message === 'string' && data.message.trim()
      ? data.message
      : '요청을 처리하지 못했습니다.';

    throw new ApiError(message, response.status, data?.errors);
  }

  return data;
};

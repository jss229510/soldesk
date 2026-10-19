import { useRef, useState } from 'react';
import { ApiError } from '../api/client';
import { Button } from './common';
import { BOARD_CATEGORIES } from '../constants/boardCategories';

// Match the current BoardRequest validation limits.
const TITLE_MAX = 100;
const CONTENT_MAX = 1000;
const fieldClass = 'w-full rounded-lg border border-gray-600 '
  + 'bg-gray-900 px-3 py-2 text-gray-300';

function validate(form) {
  const errors = {};
  if (!BOARD_CATEGORIES.some((item) => item.code === form.category)) {
    errors.category = '게시판을 선택해주세요.';
  }
  if (!form.title.trim()) errors.title = '제목을 입력해주세요.';
  else if (form.title.trim().length > TITLE_MAX) {
    errors.title = `제목은 ${TITLE_MAX}자 이하로 입력해주세요.`;
  }
  if (!form.content.trim()) errors.content = '내용을 입력해주세요.';
  else if (form.content.length > CONTENT_MAX) {
    errors.content = `내용은 ${CONTENT_MAX}자 이하로 입력해주세요.`;
  }
  return errors;
}

export default function BoardForm({
  initialValues,
  submitLabel,
  onSubmit,
  onCancel,
  onRequireLogin,
}) {
  const [form, setForm] = useState(() => ({
    category: initialValues?.category ?? '',
    title: initialValues?.title ?? '',
    content: initialValues?.content ?? '',
  }));
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);
  const formRef = useRef(null);

  const focusError = (nextErrors) => {
    const name = ['category', 'title', 'content'].find((key) => nextErrors[key]);
    if (name) formRef.current?.elements.namedItem(name)?.focus();
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: '' }));
    setMessage('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    // A ref also blocks a second submit before React rerenders the button.
    if (submittingRef.current) return;
    setMessage('');
    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      focusError(nextErrors);
      return;
    }

    submittingRef.current = true;
    setSubmitting(true);
    try {
      await onSubmit({ ...form, title: form.title.trim() });
    } catch (error) {
      const fieldErrors = {};
      ['category', 'title', 'content'].forEach((name) => {
        if (typeof error.errors?.[name] === 'string') {
          fieldErrors[name] = error.errors[name];
        }
      });
      setErrors(fieldErrors);
      if (error.status === 401) {
        setMessage('로그인이 만료되었습니다. 다시 로그인한 뒤 저장해주세요.');
        onRequireLogin();
      } else if (error.status === 403) {
        setMessage('이 게시글의 작성 또는 수정 권한이 없습니다.');
      } else if (error.status === 404) {
        setMessage('게시글이 없거나 삭제되었습니다.');
      } else if (error.status >= 500
        || (error.status >= 200 && error.status < 300)) {
        setMessage('저장 결과를 확인하지 못했습니다. 재시도 전에 목록을 확인해주세요.');
      } else {
        setMessage(error instanceof ApiError ? error.message
          : '저장 결과를 확인하지 못했습니다. 재시도 전에 목록을 확인해주세요.');
      }
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  };

  return (
    <form ref={formRef} onSubmit={handleSubmit} noValidate className="space-y-5">
      {message && <p role="alert" className="text-sm text-red-400">{message}</p>}
      <fieldset disabled={submitting} className="min-w-0 space-y-5">
        <div>
          <label htmlFor="board-category" className="mb-2 block font-medium">
            게시판
          </label>
          <select
            id="board-category"
            name="category"
            value={form.category}
            onChange={handleChange}
            className={fieldClass}
            aria-invalid={Boolean(errors.category)}
            aria-describedby={errors.category ? 'category-error' : undefined}
          >
            <option value="">게시판을 선택해주세요</option>
            {BOARD_CATEGORIES.map((item) => (
              <option key={item.code} value={item.code}>{item.label}</option>
            ))}
          </select>
          {errors.category && (
            <p id="category-error" role="alert" className="mt-1 text-sm text-red-400">
              {errors.category}
            </p>
          )}
        </div>
        <div>
          <label htmlFor="board-title" className="mb-2 block font-medium">제목</label>
          <input
            id="board-title"
            name="title"
            type="text"
            value={form.title}
            onChange={handleChange}
            maxLength={TITLE_MAX}
            className={fieldClass}
            aria-invalid={Boolean(errors.title)}
            aria-describedby={errors.title ? 'title-error' : undefined}
          />
          {errors.title && (
            <p id="title-error" role="alert" className="mt-1 text-sm text-red-400">
              {errors.title}
            </p>
          )}
        </div>
        <div>
          <label htmlFor="board-content" className="mb-2 block font-medium">내용</label>
          <textarea
            id="board-content"
            name="content"
            rows={12}
            value={form.content}
            onChange={handleChange}
            maxLength={CONTENT_MAX}
            className={`${fieldClass} resize-y`}
            aria-invalid={Boolean(errors.content)}
            aria-describedby={errors.content
              ? 'content-count content-error' : 'content-count'}
          />
          <p id="content-count" className="mt-1 text-right text-xs text-gray-400">
            {form.content.length} / {CONTENT_MAX}
          </p>
          {errors.content && (
            <p id="content-error" role="alert" className="mt-1 text-sm text-red-400">
              {errors.content}
            </p>
          )}
        </div>
      </fieldset>
      <div className="flex flex-wrap justify-end gap-2">
        <Button variant="outline" onClick={onCancel} disabled={submitting}>취소</Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? '저장 중…' : submitLabel}
        </Button>
      </div>
    </form>
  );
}

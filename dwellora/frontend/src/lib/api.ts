import { API_BASE_URL } from './endpoints';

export class ApiError extends Error { constructor(public status: number, message: string, public details?: unknown) { super(message); } }

function messageFor(status: number) {
  return ({400:'The server rejected the submitted fields.',401:'Authentication is required.',403:'You do not have permission for this action.',404:'The requested resource was not found.',409:'This conflicts with an existing record.',422:'Some fields could not be processed.',500:'The server encountered an error.'} as Record<number,string>)[status] || 'The request could not be completed.';
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const started = performance.now();
  const token = localStorage.getItem('dwellora_token');
  const headers = new Headers(options.headers);
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers, credentials: 'include' });
    const text = await response.text();
    const data = text ? JSON.parse(text) : null;
    window.dispatchEvent(new CustomEvent('dwellora:api', { detail: { ok: response.ok, ms: Math.round(performance.now() - started) } }));
    if (!response.ok) throw new ApiError(response.status, messageFor(response.status), data);
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    window.dispatchEvent(new CustomEvent('dwellora:api', { detail: { ok: false, ms: Math.round(performance.now() - started) } }));
    throw new ApiError(0, 'Cannot reach the Django API. Check VITE_API_BASE_URL and CORS settings.');
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) => request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) => request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};

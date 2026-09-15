import axios from 'axios';
import { BASE_URL } from './config';

/**
 * Single axios instance used by every screen.
 * All backend endpoints are relative to BASE_URL (config.js).
 */
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // recognition can take a few seconds on large images
});

/**
 * Extracts a readable message from an axios error.
 * FastAPI wraps errors in an HTTPException with a `detail` field —
 * surface that (or the validation-error list) when present.
 */
export function getApiErrorMessage(error, fallback = 'Something went wrong') {
  if (error.response) {
    const detail = error.response.data && error.response.data.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      // FastAPI request-validation errors: [{ loc: [...], msg, type }, ...]
      return detail
        .map((d) => `${(d.loc || []).join('.')}: ${d.msg}`)
        .join('\n');
    }
    if (detail) return JSON.stringify(detail);
    return `Request failed with status ${error.response.status}`;
  }
  if (error.request) {
    return 'Cannot reach the server. Make sure the FastAPI backend is running and BASE_URL in config.js is your computer LAN IP.';
  }
  return error.message || fallback;
}

export default api;

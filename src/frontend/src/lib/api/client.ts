import { getAccessToken } from "@/lib/auth/storage";

/**
 * fetch к API с заголовком Authorization, если в localStorage есть JWT
 * (эндпоинты /zones, /records на бэкенде защищены OAuth2PasswordBearer).
 */
export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const headers = new Headers(init?.headers);
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(input, { ...init, headers });
}

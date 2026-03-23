export type JwtClaims = {
  sub?: string;
  role?: string;
  exp?: number;
};

/** Чтение полей JWT для UI (без проверки подписи; API проверяет токен). */
export function decodeJwtPayload(token: string | null): JwtClaims | null {
  if (!token) return null;
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const pad = (4 - (base64.length % 4)) % 4;
    const padded = base64 + "=".repeat(pad);
    const json = atob(padded);
    return JSON.parse(json) as JwtClaims;
  } catch {
    return null;
  }
}

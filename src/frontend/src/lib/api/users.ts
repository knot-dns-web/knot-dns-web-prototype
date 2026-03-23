import { apiFetch } from "@/lib/api/client";

export type UserOut = {
  username: string;
  role: string;
  email: string | null;
};

export async function fetchUsers(): Promise<UserOut[]> {
  const res = await apiFetch("/api/users");
  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    throw new Error(d.detail || "Не удалось загрузить пользователей");
  }
  return res.json();
}

export async function createUser(payload: {
  username: string;
  password: string;
  role: string;
  email?: string | null;
}): Promise<UserOut> {
  const res = await apiFetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: payload.username,
      password: payload.password,
      role: payload.role,
      email: payload.email || null,
    }),
  });
  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    throw new Error(d.detail || "Ошибка создания пользователя");
  }
  return res.json();
}

export async function updateUser(
  username: string,
  payload: {
    password?: string;
    role?: string;
    email?: string | null;
  },
): Promise<UserOut> {
  const body: Record<string, unknown> = {};
  if (payload.role !== undefined) body.role = payload.role;
  if (payload.email !== undefined) body.email = payload.email;
  if (payload.password) body.password = payload.password;

  const res = await apiFetch(`/api/users/${encodeURIComponent(username)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    throw new Error(d.detail || "Ошибка обновления пользователя");
  }
  return res.json();
}

export async function deleteUser(username: string): Promise<void> {
  const res = await apiFetch(`/api/users/${encodeURIComponent(username)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const d = await res.json().catch(() => ({}));
    throw new Error(d.detail || "Ошибка удаления пользователя");
  }
}

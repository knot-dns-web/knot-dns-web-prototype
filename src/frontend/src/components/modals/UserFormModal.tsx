"use client";

import { FormEvent, useEffect, useState } from "react";
import { Modal } from "@/components/ui/Modal";

export type UserFormValues = {
  username: string;
  password: string;
  role: string;
  email: string;
};

type UserFormModalProps = {
  open: boolean;
  onClose: () => void;
  mode: "create" | "edit";
  initial?: { username: string; role: string; email: string | null };
  onSubmit: (values: UserFormValues, mode: "create" | "edit") => Promise<void>;
};

export function UserFormModal({
  open,
  onClose,
  mode,
  initial,
  onSubmit,
}: UserFormModalProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setError(null);
    if (mode === "edit" && initial) {
      setUsername(initial.username);
      setPassword("");
      setRole(initial.role);
      setEmail(initial.email ?? "");
    } else {
      setUsername("");
      setPassword("");
      setRole("user");
      setEmail("");
    }
  }, [open, mode, initial]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (mode === "create" && !username.trim()) {
      setError("Введите никнейм");
      return;
    }
    if (mode === "create" && !password) {
      setError("Введите пароль");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit(
        {
          username: username.trim(),
          password,
          role,
          email: email.trim(),
        },
        mode,
      );
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={mode === "create" ? "Добавить пользователя" : "Редактировать пользователя"}
      size="md"
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
          >
            Отмена
          </button>
          <button
            type="submit"
            form="user-form"
            disabled={busy}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-500 disabled:opacity-50"
          >
            Завершить
          </button>
        </>
      }
    >
      <form id="user-form" onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Никнейм</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={mode === "edit"}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">
            Пароль {mode === "edit" ? "(оставьте пустым, чтобы не менять)" : ""}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            autoComplete="new-password"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Роль</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
          >
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Почта</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
          />
        </div>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
      </form>
    </Modal>
  );
}

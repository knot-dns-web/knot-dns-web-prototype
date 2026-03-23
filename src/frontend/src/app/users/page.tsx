"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useAuth } from "@/lib/auth/context";
import {
  fetchUsers,
  createUser,
  updateUser,
  deleteUser,
  type UserOut,
} from "@/lib/api/users";
import { UserFormModal } from "@/components/modals/UserFormModal";
import type { UserFormValues } from "@/components/modals/UserFormModal";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

export default function UsersPage() {
  const router = useRouter();
  const { isReady, isAuthenticated, isAdmin, username: currentUsername } =
    useAuth();
  const [users, setUsers] = useState<UserOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<UserOut | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<UserOut | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchUsers()
      .then(setUsers)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!isReady) return;
    if (!isAuthenticated) {
      router.replace("/auth");
      return;
    }
    if (!isAdmin) {
      router.replace("/control");
      return;
    }
    const id = window.setTimeout(() => load(), 0);
    return () => window.clearTimeout(id);
  }, [isReady, isAuthenticated, isAdmin, router, load]);

  const handleUserSubmit = async (
    values: UserFormValues,
    mode: "create" | "edit",
  ) => {
    if (mode === "create") {
      await createUser({
        username: values.username,
        password: values.password,
        role: values.role,
        email: values.email || null,
      });
    } else if (editing) {
      await updateUser(editing.username, {
        role: values.role,
        email: values.email || null,
        ...(values.password ? { password: values.password } : {}),
      });
    }
    load();
  };

  return (
    <div className="page min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <div className="px-8 md:px-16 py-16">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <h1 className="text-[30px] font-bold">Пользователи</h1>
          <button
            type="button"
            onClick={() => {
              setEditing(null);
              setModalMode("create");
              setModalOpen(true);
            }}
            className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold hover:bg-emerald-500"
          >
            Добавить пользователя
          </button>
        </div>

        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-14 rounded-lg bg-white/5 animate-pulse" />
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="text-red-400">{error}</div>
        )}

        {!loading && !error && (
          <>
            <div className="mb-2 grid grid-cols-[1fr_100px_1fr_auto] gap-4 px-4 text-sm text-slate-400 max-md:hidden">
              <span>Никнейм</span>
              <span>Роль</span>
              <span>Почта</span>
              <span />
            </div>
            <div className="space-y-2">
              {users.map((u) => (
                <div
                  key={u.username}
                  className="flex flex-col gap-2 rounded-lg bg-white/[0.07] px-4 py-3 text-white md:grid md:grid-cols-[1fr_100px_1fr_auto] md:items-center"
                >
                  <span className="font-medium">{u.username}</span>
                  <span className="text-slate-300">{u.role}</span>
                  <span className="text-slate-400 break-all">
                    {u.email ?? "—"}
                  </span>
                  <div className="flex gap-3 justify-end">
                    <button
                      type="button"
                      onClick={() => {
                        setEditing(u);
                        setModalMode("edit");
                        setModalOpen(true);
                      }}
                      className="text-sm text-emerald-400 hover:text-emerald-300"
                    >
                      Изменить
                    </button>
                    <button
                      type="button"
                      disabled={u.username === currentUsername}
                      onClick={() => setDeleteTarget(u)}
                      className="text-sm text-red-500 hover:text-red-400 disabled:opacity-40 disabled:pointer-events-none"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      <Footer />

      <UserFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        mode={modalMode}
        initial={
          editing
            ? {
                username: editing.username,
                role: editing.role,
                email: editing.email,
              }
            : undefined
        }
        onSubmit={handleUserSubmit}
      />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={async () => {
          if (!deleteTarget) return;
          try {
            await deleteUser(deleteTarget.username);
            load();
          } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Ошибка");
            throw e;
          }
        }}
        title="Удаление пользователя"
        message={
          deleteTarget
            ? `Удалить пользователя «${deleteTarget.username}»?`
            : ""
        }
        confirmLabel="Удалить"
      />
    </div>
  );
}

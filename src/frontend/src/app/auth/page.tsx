"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useAuth } from "@/lib/auth/context";

export default function AuthPage() {
  const router = useRouter();
  const { login, isAuthenticated, isReady } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isReady && isAuthenticated) {
      router.replace("/control");
    }
  }, [isReady, isAuthenticated, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const body = new URLSearchParams();
      body.set("username", username);
      body.set("password", password);

      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: body.toString(),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Неверный логин или пароль",
        );
      }

      if (!data.access_token) {
        throw new Error("Сервер не вернул токен");
      }

      login(data.access_token as string);
      router.push("/control");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    } finally {
      setSubmitting(false);
    }
  };

  if (!isReady || isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col bg-(--background)">
        <Header variant="minimal" />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-(--light-text)">Загрузка…</p>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="page min-h-screen">
      <Header variant="minimal" />

      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-10 lg:gap-14 w-full max-w-4xl">
          <div className="w-full max-w-md mx-auto lg:mx-0 rounded-lg bg-(--info-block) p-8">
            <h1 className="text-center text-xl font-bold mb-8">
              Авторизация
            </h1>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  htmlFor="auth-login"
                  className="block text-sm text-(--light-text) mb-2"
                >
                  Логин
                </label>
                <input
                  id="auth-login"
                  name="username"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded-lg bg-(--light-text)/20 px-3 py-2.5"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="auth-password"
                  className="block text-sm text-(--light-text) mb-2"
                >
                  Пароль
                </label>
                <input
                  id="auth-password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg bg-(--light-text)/20 px-3 py-2.5"
                  required
                />
              </div>

              {error ? (
                <p className="text-sm text-(--critical)" role="alert">
                  {error}
                </p>
              ) : null}

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="home-btn home-btn-primary"
                >
                  {submitting ? "Вход…" : "Войти"}
                </button>
              </div>
            </form>
          </div>

          <p className="text-(--light-text) text-center lg:text-left text-base lg:text-lg leading-relaxed lg:max-w-sm lg:flex-1 self-center">
            Для получения доступа к системе обратитесь к администратору
          </p>
        </div>
      </div>

      <Footer />
    </div>
  );
}

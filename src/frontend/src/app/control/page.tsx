"use client";

import Footer from "@/components/footer";
import Header from "@/components/header";
import Link from "next/link";
import { useAuth } from "@/lib/auth/context";

export default function ControlPage() {
  const { isAdmin } = useAuth();

  return (
    <div className="page min-h-screen">
      <Header />

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="grid grid-cols-3 gap-6 w-full max-w-3xl auto-rows-fr">
          <Link href="/zones" className="card col-start-1 row-start-1">
            Зоны
          </Link>

          <Link href="/records" className="card col-start-1 row-start-2">
            Записи
          </Link>

          <Link
            href="/logs"
            className="card col-start-2 row-start-1 row-span-2 px-4"
          >
            Просмотр истории изменений
          </Link>

          <button
            type="button"
            className="card col-start-3 row-start-1 row-span-2"
          >
            Настройки
          </button>

          {isAdmin ? (
            <>
              <Link
                href="/users"
                className="card col-start-1 row-start-3 min-h-24"
              >
                Управление пользователями
              </Link>
              <Link
                href="/control/server"
                className="card col-start-2 col-span-2 row-start-3 min-h-24"
              >
                Настройки сервера
              </Link>
            </>
          ) : null}
        </div>
      </div>

      <Footer />
    </div>
  );
}

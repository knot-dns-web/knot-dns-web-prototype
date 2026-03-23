"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useAuth } from "@/lib/auth/context";

export default function ServerSettingsPage() {
  const router = useRouter();
  const { isReady, isAuthenticated, isAdmin } = useAuth();

  useEffect(() => {
    if (!isReady) return;
    if (!isAuthenticated) {
      router.replace("/auth");
      return;
    }
    if (!isAdmin) {
      router.replace("/control");
    }
  }, [isReady, isAuthenticated, isAdmin, router]);

  return (
    <div className="page min-h-screen bg-slate-950 text-slate-100">
      <Header />
      <div className="px-8 md:px-16 py-16 max-w-2xl">
        <h1 className="text-[30px] font-bold mb-4">Настройки сервера</h1>
        <p className="text-slate-400">
          Раздел в разработке. Здесь будут параметры конфигурации Knot и
          связанных сервисов.
        </p>
      </div>
      <Footer />
    </div>
  );
}

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
    <div className="page min-h-screen">
      <Header />
      <div className="px-8 py-16 max-w-2xl">
        <h1 className="text-[30px] font-bold mb-4">Настройки сервера</h1>
        <p className="text-(--light-text)">
          Раздел в разработке...
        </p>
      </div>
      <Footer />
    </div>
  );
}

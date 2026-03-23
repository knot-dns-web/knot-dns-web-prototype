"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";

export default function StartManagementButton() {
  const router = useRouter();
  const { isAuthenticated, isReady } = useAuth();

  const handleClick = () => {
    if (!isReady) {
      router.push("/auth");
      return;
    }
    router.push(isAuthenticated ? "/control" : "/auth");
  };

  return (
    <button
      type="button"
      className="home-btn home-btn-primary"
      onClick={handleClick}
    >
      Начать управление
    </button>
  );
}

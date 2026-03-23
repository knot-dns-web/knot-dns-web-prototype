  "use client";

  import Link from "next/link";
  import { usePathname, useRouter } from "next/navigation";
  import { useAuth } from "@/lib/auth/context";

  interface HeaderProps {
    rightContent?: React.ReactNode;
    variant?: "default" | "minimal";
  }

  export default function Header({
    rightContent,
    variant = "default",
  }: HeaderProps) {
    const pathname = usePathname();
    const router = useRouter();
    const { isAuthenticated, isReady, logout, username } = useAuth();

    const isActive = (href: string) =>
      pathname === href || pathname.startsWith(href + "/");

    const managementHref =
      isReady && isAuthenticated ? "/control" : "/auth";

    const showZoneRecordsNav =
      variant !== "minimal" &&
      isAuthenticated &&
      (pathname.startsWith("/zones") || pathname === "/records");

    const handleLogout = () => {
      logout();
      router.push("/home");
    };

    return (
      <header className="app-glass fixed w-full flex items-center justify-between gap-4 px-6 py-2 border-b border-slate-800 bg-transparent z-50">
        <div className="flex flex-1 items-center gap-1">
          <Link
            href="/home"
            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
              isActive("/home")
                ? "text-(--accenture) bg-(--light-accenture)"
                : "text-(--light-text) hover:bg-(--hover)"
            }`}
          >
            Главная
          </Link>
          {variant !== "minimal" ? (
            <>
              <Link
                href={managementHref}
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                  pathname.startsWith("/control") ||
                  isActive("/zones") ||
                  isActive("/records") ||
                  isActive("/users")
                    ? "text-(--accenture) bg-(--light-accenture)"
                    : "text-(--light-text) hover:bg-(--hover)"
                }`}
              >
                Управление
              </Link>
              <Link
                href="/books"
                className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                  isActive("/books")
                    ? "text-(--accenture) bg-(--light-accenture)"
                    : "text-(--light-text) hover:bg-(--hover)"
                }`}
              >
                Справочники
              </Link>
            </>
          ) : null}
        </div>

        {variant === "minimal" ? null : rightContent ?? (
          <div className="flex items-center gap-3">
            {showZoneRecordsNav ? (
              <div className="hidden sm:flex items-end rounded-t-lg border border-b-0 border-slate-600/80 overflow-hidden">
                <Link
                  href="/zones"
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    pathname.startsWith("/zones")
                      ? "bg-slate-900/80 text-teal-400 border-r border-slate-600/80"
                      : "bg-slate-900/40 text-slate-400 hover:text-slate-200 border-r border-slate-600/80"
                  }`}
                >
                  Зоны
                </Link>
                <Link
                  href="/records"
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    pathname === "/records"
                      ? "bg-slate-900/80 text-teal-400"
                      : "bg-slate-900/40 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Записи
                </Link>
              </div>
            ) : null}
            {isReady && isAuthenticated && username ? (
              <span
                className="max-w-35 truncate text-sm text-(--light-text)"
                title={username}
              >
                {username}
              </span>
            ) : null}
            {isReady && isAuthenticated ? (
              <button
                type="button"
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-md text-sm transition-colors text-(--light-text) hover:bg-(--hover)"
              >
                Выйти
              </button>
            ) : (
              <Link
                href="/auth"
                className="px-3 py-1.5 rounded-md text-sm transition-colors text-(--light-text) hover:bg-(--hover)"      
              >
                Авторизация
              </Link>
            )}
          </div>
        )}
      </header>
    );
  }

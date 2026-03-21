"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
    const pathname = usePathname();

    const isActive = (href: string) => pathname === href;

    return (
    <header className="app-glass fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-6 py-3 border-b border-slate-800 bg-transparent">
      <nav className="flex items-center gap-1">
        <Link 
          href="/home" 
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            isActive("/") 
              ? "text-emerald-500 bg-slate-900/50" 
              : "text-slate-400 hover:text-slate-200 hover:bg-white/10"
          }`}
        >
          Главная
        </Link>
        <Link 
          href="/control" 
          className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
            isActive("/control")
              ? "text-emerald-500 bg-slate-900/50"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/10"
          }`}
        >
          Управление
        </Link>
        <Link 
          href="/books" 
          className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
            isActive("/books")
              ? "text-emerald-500 bg-slate-900/50"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/10"
          }`}
        >
          Справочники
        </Link>
      </nav>
      
      <div>
        <Link 
          href="/auth" 
          className="text-slate-400 hover:text-slate-200 text-sm px-3 py-1.5 rounded-md transition-colors hover:bg-white/10"
        >
          Авторизация
        </Link>
      </div>
    </header>
  );
}
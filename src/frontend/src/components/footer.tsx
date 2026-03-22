import { Github } from 'lucide-react';
import Link from 'next/link';

export default function Footer() {
    return (
    <footer className="app-glass fixed bottom-0 w-full border-t border-slate-800 bg-transparent">
      <div className="mx-auto p-4 flex justify-end">
        <Link 
          href="https://github.com/knot-dns-web" 
          className="flex items-center gap-2 text-slate-500 hover:text-slate-300 text-xs transition-colors"
        >
          <span>Наш GitHub</span>
          <Github size={14} />
        </Link>
      </div>
    </footer>
  );
}
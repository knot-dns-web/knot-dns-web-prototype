import { Github } from 'lucide-react';

export default function Footer() {
    return (
    <footer className="app-glass fixed bottom-0 left-0 right-0 z-50 w-full border-t border-slate-800 bg-transparent">
      <div className="max-w-5xl mx-auto p-4 flex justify-end">
        <a 
          href="#" 
          className="flex items-center gap-2 text-slate-500 hover:text-slate-300 text-xs transition-colors"
        >
          <span>Наш GitHub</span>
          <Github size={14} />
        </a>
      </div>
    </footer>
  );
}
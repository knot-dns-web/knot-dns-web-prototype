"use client";

import { useEffect, type ReactNode } from "react";

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  /** Ширина контента */
  size?: "md" | "lg";
};

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  size = "md",
}: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const maxW = size === "lg" ? "max-w-xl" : "max-w-md";

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-slate-950/55 backdrop-blur-md"
        aria-label="Закрыть"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className={`relative z-10 w-full ${maxW} rounded-xl border border-white/10 bg-slate-900/90 shadow-2xl shadow-black/50`}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="border-b border-white/10 px-5 py-4">
          <h2 id="modal-title" className="text-lg font-semibold text-white">
            {title}
          </h2>
        </div>
        <div className="px-5 py-4 text-slate-200">{children}</div>
        {footer ? (
          <div className="flex justify-end gap-2 border-t border-white/10 px-5 py-3">
            {footer}
          </div>
        ) : null}
      </div>
    </div>
  );
}

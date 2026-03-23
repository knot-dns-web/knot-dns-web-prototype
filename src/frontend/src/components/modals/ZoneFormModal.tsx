"use client";

import { FormEvent, useEffect, useState } from "react";
import { Modal } from "@/components/ui/Modal";

type ZoneFormModalProps = {
  open: boolean;
  onClose: () => void;
  onSubmit: (name: string) => Promise<void>;
};

export function ZoneFormModal({ open, onClose, onSubmit }: ZoneFormModalProps) {
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setName("");
      setError(null);
    }
  }, [open]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Введите название зоны");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit(trimmed);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Создание зоны"
      size="md"
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
          >
            Отмена
          </button>
          <button
            type="submit"
            form="zone-form"
            disabled={busy}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-500 disabled:opacity-50"
          >
            Завершить
          </button>
        </>
      }
    >
      <form id="zone-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="zone-name" className="mb-1 block text-sm text-slate-400">
            Название
          </label>
          <input
            id="zone-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            placeholder="example.com."
            autoFocus
          />
        </div>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
      </form>
    </Modal>
  );
}

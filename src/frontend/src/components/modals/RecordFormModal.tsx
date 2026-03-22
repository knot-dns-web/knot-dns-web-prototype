"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { DNS_RECORD_TYPES } from "@/lib/dns/recordTypes";
import type { DnsRecord } from "@/lib/api/records";

export type RecordFormValues = {
  zone: string;
  owner: string;
  type: string;
  ttl: number;
  data: string;
};

type RecordFormModalProps = {
  open: boolean;
  onClose: () => void;
  zones: string[];
  /** Если задано — зона фиксирована (страница конкретной зоны) */
  fixedZone?: string | null;
  /** Редактирование: исходная запись (wire owner) */
  initial?: DnsRecord | null;
  onSubmit: (
    values: RecordFormValues,
    initial: DnsRecord | null,
  ) => Promise<void>;
};

const emptyValues: RecordFormValues = {
  zone: "",
  owner: "@",
  type: "A",
  ttl: 3600,
  data: "",
};

export function RecordFormModal({
  open,
  onClose,
  zones,
  fixedZone,
  initial,
  onSubmit,
}: RecordFormModalProps) {
  const [values, setValues] = useState<RecordFormValues>(emptyValues);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setError(null);
    if (initial) {
      setValues({
        zone: initial.zone,
        owner: initial.owner,
        type: initial.type,
        ttl: initial.ttl,
        data: initial.data,
      });
    } else {
      setValues({
        ...emptyValues,
        zone: fixedZone ?? zones[0] ?? "",
      });
    }
  }, [open, initial, fixedZone, zones]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!values.zone.trim()) {
      setError("Укажите зону");
      return;
    }
    if (!values.type.trim()) {
      setError("Укажите тип");
      return;
    }
    if (!Number.isFinite(values.ttl) || values.ttl <= 0) {
      setError("TTL должен быть положительным числом");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit(values, initial ?? null);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setBusy(false);
    }
  };

  const zoneLocked = Boolean(fixedZone);
  const zoneReadOnly = Boolean(initial);

  const typeOptions = useMemo(() => {
    const set = new Set<string>([...DNS_RECORD_TYPES]);
    if (values.type) set.add(values.type);
    return Array.from(set);
  }, [values.type]);

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={initial ? "Редактирование записи" : "Создание записи"}
      size="lg"
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
            form="record-form"
            disabled={busy}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-500 disabled:opacity-50"
          >
            Завершить
          </button>
        </>
      }
    >
      <form id="record-form" onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="mb-1 block text-sm text-slate-400">Зона</label>
          {zoneReadOnly ? (
            <input
              readOnly
              value={values.zone}
              className="w-full cursor-not-allowed rounded-lg border border-slate-600/40 bg-slate-800/50 px-3 py-2 text-slate-400"
            />
          ) : zoneLocked ? (
            <input
              readOnly
              value={fixedZone ?? ""}
              className="w-full cursor-not-allowed rounded-lg border border-slate-600/40 bg-slate-800/50 px-3 py-2 text-slate-400"
            />
          ) : (
            <select
              value={values.zone}
              onChange={(e) =>
                setValues((v) => ({ ...v, zone: e.target.value }))
              }
              className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              {zones.map((z) => (
                <option key={z} value={z}>
                  {z}
                </option>
              ))}
            </select>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Владелец</label>
          <input
            value={values.owner}
            onChange={(e) =>
              setValues((v) => ({ ...v, owner: e.target.value }))
            }
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            placeholder="@ или имя (www)"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm text-slate-400">Тип</label>
            <select
              value={values.type}
              onChange={(e) =>
                setValues((v) => ({ ...v, type: e.target.value }))
              }
              className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            >
              {typeOptions.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-slate-400">TTL</label>
            <input
              type="number"
              min={1}
              value={values.ttl}
              onChange={(e) =>
                setValues((v) => ({
                  ...v,
                  ttl: Number(e.target.value) || 0,
                }))
              }
              className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-400">Данные</label>
          <textarea
            value={values.data}
            onChange={(e) =>
              setValues((v) => ({ ...v, data: e.target.value }))
            }
            rows={3}
            className="w-full rounded-lg border border-slate-600/50 bg-slate-800/80 px-3 py-2 text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
          />
        </div>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
      </form>
    </Modal>
  );
}

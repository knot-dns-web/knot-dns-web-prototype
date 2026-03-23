"use client";

import { useState } from "react";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useAllRecords } from "@/lib/hooks/all-records";
import { useZones } from "@/lib/hooks/zones";
import { RecordFormModal } from "@/components/modals/RecordFormModal";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import type { DnsRecord } from "@/lib/api/records";
import type { RecordFormValues } from "@/components/modals/RecordFormModal";
import { ownerDisplay } from "@/lib/dns/zone";
import { Pencil, Trash2 } from "lucide-react";

export default function RecordsPage() {
  const { zones } = useZones();
  const {
    records,
    loading,
    error,
    addRecord,
    patchRecord,
    removeRecord,
  } = useAllRecords();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DnsRecord | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DnsRecord | null>(null);

  const handleSubmit = async (
    values: RecordFormValues,
    initial: DnsRecord | null,
  ) => {
    if (initial) {
      await patchRecord(
        {
          zone: initial.zone,
          owner: values.owner,
          type: values.type,
          ttl: values.ttl,
          data: values.data,
        },
        initial,
      );
    } else {
      await addRecord({
        zone: values.zone,
        owner: values.owner,
        type: values.type,
        ttl: values.ttl,
        data: values.data,
      });
    }
  };

  const sorted = [...records].sort((a, b) => {
    const z = a.zone.localeCompare(b.zone, "ru");
    if (z !== 0) return z;
    const o = a.owner.localeCompare(b.owner, "ru");
    if (o !== 0) return o;
    return a.type.localeCompare(b.type, "ru");
  });

  return (
    <div className="page min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <div className="px-8 md:px-16 py-16">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <h1 className="text-[30px] font-bold">Записи</h1>
          <button
            type="button"
            onClick={() => {
              setEditing(null);
              setModalOpen(true);
            }}
            className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold hover:bg-emerald-500"
          >
            Добавить запись
          </button>
        </div>

        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 rounded-lg bg-white/5 animate-pulse" />
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="text-red-400">{error}</div>
        )}

        {!loading && !error && sorted.length === 0 && (
          <p className="text-slate-400">Нет записей.</p>
        )}

        {!loading && !error && sorted.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-white/[0.04] text-slate-400">
                  <th className="px-4 py-3 font-medium">Зона</th>
                  <th className="px-4 py-3 font-medium">Владелец</th>
                  <th className="px-4 py-3 font-medium">Тип</th>
                  <th className="px-4 py-3 font-medium">TTL</th>
                  <th className="px-4 py-3 font-medium">Данные</th>
                  <th className="px-4 py-3 w-24" />
                </tr>
              </thead>
              <tbody>
                {sorted.map((r, idx) => (
                  <tr
                    key={`${r.zone}-${r.owner}-${r.type}-${r.data}-${idx}`}
                    className="border-b border-white/5 hover:bg-white/[0.03]"
                  >
                    <td className="px-4 py-3">{r.zone}</td>
                    <td className="px-4 py-3">{ownerDisplay(r.owner, r.zone)}</td>
                    <td className="px-4 py-3">{r.type}</td>
                    <td className="px-4 py-3">{r.ttl}</td>
                    <td className="px-4 py-3 max-w-xs break-all">{r.data}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setEditing(r);
                            setModalOpen(true);
                          }}
                          className="text-slate-400 hover:text-emerald-400"
                          aria-label="Редактировать"
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          type="button"
                          onClick={() => setDeleteTarget(r)}
                          className="text-red-500 hover:text-red-400"
                          aria-label="Удалить"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Footer />

      <RecordFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        zones={zones}
        fixedZone={null}
        initial={editing}
        onSubmit={handleSubmit}
      />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={async () => {
          if (!deleteTarget) return;
          try {
            await removeRecord(deleteTarget);
          } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Ошибка удаления");
            throw e;
          }
        }}
        title="Удаление записи"
        message={
          deleteTarget
            ? `Удалить запись ${deleteTarget.type} в зоне «${deleteTarget.zone}»?`
            : ""
        }
        confirmLabel="Удалить"
      />
    </div>
  );
}

"use client";

import { useMemo, useState } from "react";
import { ArrowLeft, Pencil, Trash2 } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useRecords } from "@/lib/hooks/records";
import { ownerDisplay } from "@/lib/dns/zone";
import { RecordFormModal } from "@/components/modals/RecordFormModal";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useZones } from "@/lib/hooks/zones";
import type { DnsRecord } from "@/lib/api/records";
import type { RecordFormValues } from "@/components/modals/RecordFormModal";

type TypeGroup = {
  ttl: number;
  items: DnsRecord[];
};

export default function ZoneRecordsPage() {
  const router = useRouter();
  const params = useParams<{ zoneName: string }>();
  const zoneName = decodeURIComponent(params.zoneName);
  const { zones } = useZones();

  const {
    records,
    loading,
    error,
    addRecord,
    patchRecord,
    removeRecord,
  } = useRecords(zoneName);

  const [recordModalOpen, setRecordModalOpen] = useState(false);
  const [editing, setEditing] = useState<DnsRecord | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DnsRecord | null>(null);

  const groupedRecords = useMemo(() => {
    const grouped = new Map<string, Map<string, TypeGroup>>();

    for (const record of records) {
      const displayOwner = ownerDisplay(record.owner, zoneName);
      const type = record.type || "UNKNOWN";

      if (!grouped.has(displayOwner)) grouped.set(displayOwner, new Map());
      const byType = grouped.get(displayOwner)!;

      if (!byType.has(type)) {
        byType.set(type, {
          ttl: record.ttl,
          items: [],
        });
      }

      byType.get(type)!.items.push(record);
    }

    return Array.from(grouped.entries())
      .sort(([a], [b]) => a.localeCompare(b, "ru"))
      .map(([owner, types]) => ({
        owner,
        types: Array.from(types.entries())
          .sort(([a], [b]) => a.localeCompare(b, "ru"))
          .map(([type, payload]) => ({
            type,
            ...payload,
          })),
      }));
  }, [records, zoneName]);

  const handleRecordSubmit = async (
    values: RecordFormValues,
    initial: DnsRecord | null,
  ) => {
    if (initial) {
      await patchRecord(
        {
          owner: values.owner,
          type: values.type,
          ttl: values.ttl,
          data: values.data,
        },
        initial,
      );
    } else {
      await addRecord({
        owner: values.owner,
        type: values.type,
        ttl: values.ttl,
        data: values.data,
      });
    }
  };

  return (
    <div className="page">
      <Header />

      <div className="px-8 md:px-16 py-16">
        <div className="flex items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => router.push("/zones")}
              className="text-slate-300 hover:text-white transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-[30px] font-bold">{zoneName}</h1>
          </div>

          <button
            type="button"
            onClick={() => {
              setEditing(null);
              setRecordModalOpen(true);
            }}
            className="px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 transition-colors text-sm font-semibold"
          >
            Добавить запись
          </button>
        </div>

        {loading && (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, idx) => (
              <div key={idx} className="h-24 rounded-lg bg-white/5 animate-pulse" />
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="text-red-400">{error}</div>
        )}

        {!loading && !error && groupedRecords.length === 0 && (
          <div className="text-slate-400">В этой зоне пока нет записей.</div>
        )}

        {!loading && !error && groupedRecords.length > 0 && (
          <div className="space-y-4">
            {groupedRecords.map((domainGroup) => (
              <div key={domainGroup.owner} className="rounded-lg bg-white/[0.06] p-3">
                <div className="text-lg font-semibold mb-2">{domainGroup.owner}</div>

                <div className="space-y-2">
                  {domainGroup.types.map((typeGroup) => (
                    <div
                      key={`${domainGroup.owner}-${typeGroup.type}`}
                      className="rounded-md bg-black/20 p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold">
                          {typeGroup.type}{" "}
                          <span className="text-slate-400 text-sm">
                            TTL: {typeGroup.ttl}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        {typeGroup.items.map((record, idx) => (
                          <div
                            key={`${record.zone}-${record.owner}-${record.type}-${record.data}-${idx}`}
                            className="flex items-center justify-between gap-2 rounded-md bg-white/[0.04] px-3 py-2"
                          >
                            <span className="min-w-0 flex-1 break-all">{record.data}</span>
                            <div className="flex shrink-0 items-center gap-2">
                              <button
                                type="button"
                                onClick={() => {
                                  setEditing(record);
                                  setRecordModalOpen(true);
                                }}
                                className="text-slate-400 hover:text-emerald-400 transition-colors"
                                aria-label="Редактировать"
                              >
                                <Pencil size={16} />
                              </button>
                              <button
                                type="button"
                                onClick={() => setDeleteTarget(record)}
                                className="text-red-500 hover:text-red-400 transition-colors"
                                aria-label="Удалить"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Footer />

      <RecordFormModal
        open={recordModalOpen}
        onClose={() => {
          setRecordModalOpen(false);
          setEditing(null);
        }}
        zones={zones}
        fixedZone={zoneName}
        initial={editing}
        onSubmit={handleRecordSubmit}
      />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={async () => {
          if (!deleteTarget) return;
          try {
            await removeRecord(
              deleteTarget.owner,
              deleteTarget.type,
              deleteTarget.data,
            );
          } catch (e: unknown) {
            alert(e instanceof Error ? e.message : "Ошибка удаления");
            throw e;
          }
        }}
        title="Удаление записи"
        message={
          deleteTarget
            ? `Удалить запись ${deleteTarget.type} (${deleteTarget.data}) в зоне «${zoneName}»?`
            : ""
        }
        confirmLabel="Удалить"
      />
    </div>
  );
}

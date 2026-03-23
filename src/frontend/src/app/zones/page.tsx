"use client";

import { useState, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ZonesTableHeader from "@/app/zones/ZonesTableHeader";
import ZonesTableRows from "@/app/zones/ZonesTableRows";
import { useZones } from "@/lib/hooks/zones";
import { ZoneFormModal } from "@/components/modals/ZoneFormModal";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

export default function ZonesPage() {
  const router = useRouter();
  const {
    zones,
    loading,
    error,
    addZone,
    removeZone,
  } = useZones();

  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [zoneModalOpen, setZoneModalOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const handleAddZone = async (name: string) => {
    await addZone(name);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await removeZone(deleteTarget);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Ошибка удаления");
      throw e;
    }
  };

  const handleOpenZone = useCallback(
    (name: string) => {
      router.push(`/zones/${encodeURIComponent(name)}`);
    },
    [router],
  );

  const sortedZones = useMemo(() => {
    return [...zones].sort((a, b) =>
      sortDirection === "asc"
        ? a.localeCompare(b, "ru")
        : b.localeCompare(a, "ru"),
    );
  }, [zones, sortDirection]);

  return (
    <div className="page">
      <Header />

      <div className="px-8 md:px-16 py-16">
        <h1 className="text-[30px] font-bold mb-8">Зоны</h1>

        <ZonesTableHeader
          sortDirection={sortDirection}
          onSort={() =>
            setSortDirection((p) => (p === "asc" ? "desc" : "asc"))
          }
          onAddZone={() => setZoneModalOpen(true)}
        />

        {error ? (
          <div className="text-(--critical)">{error}</div>
        ) : (
          <ZonesTableRows
            zones={sortedZones}
            loading={loading}
            onDelete={(name) => setDeleteTarget(name)}
            onOpen={handleOpenZone}
          />
        )}
      </div>

      <Footer />

      <ZoneFormModal
        open={zoneModalOpen}
        onClose={() => setZoneModalOpen(false)}
        onSubmit={handleAddZone}
      />

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Удаление зоны"
        message={
          deleteTarget
            ? `Удалить зону «${deleteTarget}»? Это действие нельзя отменить`
            : ""
        }
        confirmLabel="Удалить"
      />
    </div>
  );
}

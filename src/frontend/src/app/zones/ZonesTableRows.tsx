import { Trash } from "lucide-react";

interface ZonesTableRowsProps {
  zones: string[];
  loading: boolean;
  onDelete: (name: string) => void;
  onOpen: (name: string) => void;
}

export default function ZonesTableRows({
  zones,
  loading,
  onDelete,
  onOpen,
}: ZonesTableRowsProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="w-full h-14 bg-(--info-block) rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {zones.map((zone) => (
        <div
          key={zone}
          onClick={() => onOpen(zone)}
          className="flex items-center justify-between w-full px-6 py-4
                     bg-(--info-block) rounded-lg text-2xl
                     hover:bg-(--hover) transition-colors cursor-pointer"
        >
          <span>{zone}</span>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(zone);
            }}
            className="text-(--critical)"
          >
            <Trash size={18} />
          </button>
        </div>
      ))}
    </div>
  );
}
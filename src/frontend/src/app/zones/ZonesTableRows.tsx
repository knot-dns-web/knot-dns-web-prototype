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
          <div key={i} className="w-full h-14 bg-white/5 rounded-lg animate-pulse" />
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
                     bg-white/[0.07] rounded-lg text-white text-2xl
                     hover:bg-white/10 transition-colors cursor-pointer"
        >
          <span>{zone}</span>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(zone);
            }}
            className="text-red-500 hover:text-red-400 transition-colors"
          >
            <Trash size={18} />
          </button>
        </div>
      ))}
    </div>
  );
}
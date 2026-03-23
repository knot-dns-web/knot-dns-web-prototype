import { Triangle } from "lucide-react";

interface ZonesTableHeaderProps {
  sortDirection: "asc" | "desc";
  onSort: () => void;
  onAddZone?: () => void;
}

export default function ZonesTableHeader({
  sortDirection,
  onSort,
  onAddZone,
}: ZonesTableHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-2">
      <button
        onClick={onSort}
        className="flex items-center gap-2 text-[20px] hover:opacity-80 transition-opacity ml-19"
      >
        <span>Название</span>

        <Triangle
          size={14}
          className={`transition-transform duration-200 ${
            sortDirection === "desc" ? "rotate-180" : ""
          }`}
        />
      </button>

      <button
        onClick={onAddZone}
        className="px-4 py-2 rounded-md bg-(--accenture) hover:bg-(hover-accenture) transition-colors text-sm"
      >
        Добавить зону
      </button>
    </div>
  );
}
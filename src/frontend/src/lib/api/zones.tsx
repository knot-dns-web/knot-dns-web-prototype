import { apiFetch } from "@/lib/api/client";

export async function fetchZones(): Promise<string[]> {
  const response = await apiFetch("/api/zones");

  if (!response.ok) {
    throw new Error("Ошибка загрузки зон");
  }

  const data = await response.json();

  return data.zones || [];
}

export async function createZone(name: string): Promise<void> {
  const response = await apiFetch("/api/zones", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Ошибка создания зоны");
  }
}

export async function deleteZone(zoneName: string): Promise<void> {
  const response = await apiFetch(`/api/zones/${encodeURIComponent(zoneName)}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Ошибка удаления зоны");
  }
}
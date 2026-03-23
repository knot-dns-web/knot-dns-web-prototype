import { apiFetch } from "@/lib/api/client";

export interface DnsRecord {
  zone: string;
  owner: string;
  type: string;
  ttl: number;
  data: string;
}

/**
 * Ответ Knot/libknot часто вложенный, напр. { zone: { "ccc.": [ ... ] } }.
 * Собираем пары (имя_зоны, массив записей) с любого уровня вложенности.
 */
function collectZoneRecordArrays(
  payload: unknown,
  depth = 0,
): Map<string, unknown[]> {
  const out = new Map<string, unknown[]>();

  if (depth > 8 || payload === null || typeof payload !== "object") {
    return out;
  }

  if (Array.isArray(payload)) {
    return out;
  }

  for (const [key, value] of Object.entries(payload)) {
    if (Array.isArray(value)) {
      const prev = out.get(key) ?? [];
      out.set(key, [...prev, ...value]);
    } else if (value !== null && typeof value === "object") {
      const inner = collectZoneRecordArrays(value, depth + 1);
      for (const [z, rows] of inner) {
        const prev = out.get(z) ?? [];
        out.set(z, [...prev, ...rows]);
      }
    }
  }

  return out;
}

function parseRecordLine(zone: string, line: string): DnsRecord | null {
  const parts = line.trim().split(/\s+/);
  if (parts.length < 5) return null;

  const owner = parts[0];
  const ttl = Number(parts[1]);
  const type = parts[3];
  const data = parts.slice(4).join(" ");

  return {
    zone,
    owner,
    type,
    ttl: Number.isFinite(ttl) ? ttl : 0,
    data,
  };
}

function normalizeRecord(raw: unknown, defaultZone?: string): DnsRecord | null {
  if (!raw || typeof raw !== "object") return null;
  const candidate = raw as Record<string, unknown>;

  const zone = String(
    candidate.zone ?? candidate.zone_name ?? defaultZone ?? "",
  );
  const owner = String(candidate.owner ?? candidate.name ?? "@");
  const type = String(candidate.type ?? candidate.rtype ?? "UNKNOWN");
  const ttl = Number(candidate.ttl ?? 0);
  const data = String(candidate.data ?? candidate.value ?? "");

  if (!zone) return null;

  return {
    zone,
    owner,
    type,
    ttl: Number.isFinite(ttl) ? ttl : 0,
    data,
  };
}

function normalizeRecords(recordsPayload: unknown): DnsRecord[] {
  if (Array.isArray(recordsPayload)) {
    return recordsPayload
      .map((row) => normalizeRecord(row))
      .filter((record): record is DnsRecord => record !== null);
  }

  if (!recordsPayload || typeof recordsPayload !== "object") {
    return [];
  }

  const buckets = collectZoneRecordArrays(recordsPayload);
  const records: DnsRecord[] = [];

  for (const [zoneName, zoneRecords] of buckets) {
    for (const record of zoneRecords) {
      if (typeof record === "string") {
        const parsed = parseRecordLine(zoneName, record);
        if (parsed) records.push(parsed);
        continue;
      }

      const normalized = normalizeRecord(record, zoneName);
      if (normalized) records.push(normalized);
    }
  }

  return records;
}

export async function fetchRecords(): Promise<DnsRecord[]> {
  const response = await apiFetch("/api/records");

  if (!response.ok) {
    throw new Error("Ошибка загрузки записей");
  }

  const data = await response.json();
  return normalizeRecords(data.records);
}

export async function createRecord(payload: {
  zone: string;
  owner: string;
  type: string;
  ttl: number;
  data: string;
}): Promise<void> {
  const response = await apiFetch("/api/records", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Ошибка создания записи");
  }
}

export async function updateRecord(
  zone: string,
  payload: {
    old_owner: string;
    old_type: string;
    old_data: string | null;
    owner: string;
    type: string;
    ttl: number;
    data: string;
  },
): Promise<void> {
  const response = await apiFetch(
    `/api/records/${encodeURIComponent(zone)}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Ошибка обновления записи");
  }
}

export async function deleteRecord(
  zone: string,
  owner: string,
  type: string,
  data?: string | null,
): Promise<void> {
  const params = new URLSearchParams();
  if (data != null && data !== "") {
    params.set("data", data);
  }
  const qs = params.toString();
  const base = `/api/records/${encodeURIComponent(zone)}/${encodeURIComponent(owner)}/${encodeURIComponent(type)}`;
  const response = await apiFetch(qs ? `${base}?${qs}` : base, {
    method: "DELETE",
  });

  if (!response.ok) {
    const dataJson = await response.json();
    throw new Error(dataJson.detail || "Ошибка удаления записи");
  }
}

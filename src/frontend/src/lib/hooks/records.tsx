import { useCallback, useEffect, useState } from "react";
import {
  createRecord,
  deleteRecord,
  fetchRecords,
  updateRecord,
  type DnsRecord,
} from "../api/records";
import { ownerForApi, zoneNamesEqual } from "@/lib/dns/zone";

export function useRecords(zoneName: string) {
  const [records, setRecords] = useState<DnsRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRecords = useCallback(() => {
    setLoading(true);
    setError(null);

    fetchRecords()
      .then((allRecords) => {
        setRecords(
          allRecords.filter((record) => zoneNamesEqual(record.zone, zoneName)),
        );
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [zoneName]);

  useEffect(() => {
    if (!zoneName) return;
    const id = window.setTimeout(() => loadRecords(), 0);
    return () => window.clearTimeout(id);
  }, [zoneName, loadRecords]);

  const addRecord = useCallback(async (payload: Omit<DnsRecord, "zone">) => {
    await createRecord({
      zone: zoneName,
      ...payload,
      owner: ownerForApi(payload.owner, zoneName),
    });
    loadRecords();
  }, [zoneName, loadRecords]);

  const patchRecord = useCallback(
    async (values: Omit<DnsRecord, "zone">, initial: DnsRecord) => {
      await updateRecord(zoneName, {
        old_owner: initial.owner,
        old_type: initial.type,
        old_data: initial.data,
        owner: ownerForApi(values.owner, zoneName),
        type: values.type,
        ttl: values.ttl,
        data: values.data,
      });
      loadRecords();
    },
    [zoneName, loadRecords],
  );

  const removeRecord = useCallback(
    async (owner: string, type: string, data?: string | null) => {
      await deleteRecord(zoneName, owner, type, data);
      loadRecords();
    },
    [zoneName, loadRecords],
  );

  return {
    records,
    loading,
    error,
    reload: loadRecords,
    addRecord,
    patchRecord,
    removeRecord,
  };
}

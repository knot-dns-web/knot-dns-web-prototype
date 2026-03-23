import { useCallback, useEffect, useState } from "react";
import {
  createRecord,
  deleteRecord,
  fetchRecords,
  updateRecord,
  type DnsRecord,
} from "../api/records";
import { ownerForApi } from "@/lib/dns/zone";

export function useAllRecords() {
  const [records, setRecords] = useState<DnsRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchRecords()
      .then(setRecords)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const addRecord = useCallback(
    async (values: Omit<DnsRecord, "zone"> & { zone: string }) => {
      await createRecord({
        zone: values.zone,
        owner: ownerForApi(values.owner, values.zone),
        type: values.type,
        ttl: values.ttl,
        data: values.data,
      });
      reload();
    },
    [reload],
  );

  const patchRecord = useCallback(
    async (values: DnsRecord, initial: DnsRecord) => {
      await updateRecord(initial.zone, {
        old_owner: initial.owner,
        old_type: initial.type,
        old_data: initial.data,
        owner: ownerForApi(values.owner, initial.zone),
        type: values.type,
        ttl: values.ttl,
        data: values.data,
      });
      reload();
    },
    [reload],
  );

  const removeRecord = useCallback(
    async (r: DnsRecord) => {
      await deleteRecord(r.zone, r.owner, r.type, r.data);
      reload();
    },
    [reload],
  );

  return {
    records,
    loading,
    error,
    reload,
    addRecord,
    patchRecord,
    removeRecord,
  };
}

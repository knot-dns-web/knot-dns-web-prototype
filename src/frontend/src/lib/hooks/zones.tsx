import { useEffect, useState, useCallback } from "react";
import { fetchZones, createZone, deleteZone } from "../api/zones";

export function useZones() {
  const [zones, setZones] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadZones = useCallback(() => {
    setLoading(true);
    setError(null);

    fetchZones()
      .then(setZones)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const id = window.setTimeout(() => loadZones(), 0);
    return () => window.clearTimeout(id);
  }, [loadZones]);

  const addZone = useCallback(async (name: string) => {
    await createZone(name);
    loadZones();
  }, [loadZones]);

  const removeZone = useCallback(async (name: string) => {
    await deleteZone(name);
    loadZones();
  }, [loadZones]);

  return {
    zones,
    loading,
    error,
    reload: loadZones,
    addZone,
    removeZone,
  };
}
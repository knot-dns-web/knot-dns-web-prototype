def _is_rtype_payload(obj: object) -> bool:
    return isinstance(obj, dict) and "data" in obj

def knot_zone_block_to_records(block: object) -> list[dict]:
    if not isinstance(block, dict):
        return []

    out: list[dict] = []

    for zone_name, z_node in block.items():
        if not isinstance(z_node, dict) or not z_node:
            continue

        sample = next(iter(z_node.values()))

        if isinstance(sample, dict) and sample:
            try:
                inner = next(iter(sample.values()))
            except StopIteration:
                continue
            if _is_rtype_payload(inner):
                for owner, types_map in z_node.items():
                    if not isinstance(types_map, dict):
                        continue
                    for rtype, payload in types_map.items():
                        if not _is_rtype_payload(payload):
                            continue
                        ttl_raw = payload.get("ttl", 0)
                        try:
                            ttl = int(ttl_raw)
                        except (TypeError, ValueError):
                            ttl = 0
                        data_list = payload["data"]
                        if not isinstance(data_list, list):
                            data_list = [data_list]
                        for d in data_list:
                            out.append(
                                {
                                    "zone": str(zone_name),
                                    "owner": str(owner),
                                    "type": str(rtype),
                                    "ttl": ttl,
                                    "data": "" if d is None else str(d),
                                }
                            )
                continue

        if isinstance(sample, str):
            for rtype, data in z_node.items():
                    out.append(
                        {
                            "zone": str(zone_name),
                            "owner": str(zone_name),
                            "type": str(rtype),
                            "ttl": 0,
                            "data": str(data),
                        }
                    )

    return out

def _dns_name_equal(a: str, b: str) -> bool:
    x = (a or "").strip().lower().rstrip(".")
    y = (b or "").strip().lower().rstrip(".")
    return bool(x) and x == y

def normalize_knot_zone_fqdn(zone: str) -> str:
    z = (zone or "").strip()
    if not z or z == ".":
        return z
    if not z.endswith("."):
        return z + "."
    return z

def normalize_knot_owner(owner: str, zone_fqdn: str) -> str:
    z = normalize_knot_zone_fqdn(zone_fqdn)
    o = (owner or "").strip()
    if o in ("", "@"):
        return z
    if _dns_name_equal(o, z):
        return z
    return o.strip()

def normalize_knot_rr_type(rtype: str) -> str:
    return (rtype or "").strip().upper()

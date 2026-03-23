export function dnsNameCanonical(s: string): string {
  return s.trim().toLowerCase();
}

export function zoneNamesEqual(a: string, b: string): boolean {
  const x = dnsNameCanonical(a).replace(/\.+$/, "");
  const y = dnsNameCanonical(b).replace(/\.+$/, "");
  return x === y;
}

export function isApexOwner(owner: string, zoneName: string): boolean {
  const o = owner.trim();
  if (o === "" || o === "@") return true;
  return zoneNamesEqual(o, zoneName);
}

export function ownerDisplay(owner: string, zoneName: string): string {
  return isApexOwner(owner, zoneName) ? "@" : owner;
}

export function ownerForApi(owner: string, zoneName: string): string {
  const o = owner.trim();
  if (o === "" || o === "@") return zoneName;
  if (zoneNamesEqual(o, zoneName)) return zoneName;
  return owner;
}

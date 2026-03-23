/**
 * Нормализация DNS-имён для сравнения (зона в Knot часто с точкой в конце: "ccc.").
 */
export function dnsNameCanonical(s: string): string {
  return s.trim().toLowerCase();
}

/** Сравнение зон: ccc ≈ ccc. ≈ CCC. */
export function zoneNamesEqual(a: string, b: string): boolean {
  const x = dnsNameCanonical(a).replace(/\.+$/, "");
  const y = dnsNameCanonical(b).replace(/\.+$/, "");
  return x === y;
}

/** Apex в Knot хранится как FQDN зоны (например "ccc."), а не "@". */
export function isApexOwner(owner: string, zoneName: string): boolean {
  const o = owner.trim();
  if (o === "" || o === "@") return true;
  return zoneNamesEqual(o, zoneName);
}

/** Подпись блока в UI: для корня показываем "@". */
export function ownerDisplay(owner: string, zoneName: string): string {
  return isApexOwner(owner, zoneName) ? "@" : owner;
}

/**
 * Для API (zone-set / delete): @ и имя, совпадающее с зоной, → как в хранилище (имя зоны из списка).
 */
export function ownerForApi(owner: string, zoneName: string): string {
  const o = owner.trim();
  if (o === "" || o === "@") return zoneName;
  if (zoneNamesEqual(o, zoneName)) return zoneName;
  return owner;
}

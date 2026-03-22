/** Распространённые типы RR для выпадающего списка */
export const DNS_RECORD_TYPES = [
  "A",
  "AAAA",
  "CNAME",
  "MX",
  "NS",
  "TXT",
  "SOA",
  "PTR",
  "SRV",
  "CAA",
  "TLSA",
  "SSHFP",
] as const;

export type DnsRecordType = (typeof DNS_RECORD_TYPES)[number];

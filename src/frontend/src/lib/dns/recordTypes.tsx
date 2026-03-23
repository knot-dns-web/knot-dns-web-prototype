export const DNS_RECORD_TYPES = [
  "A",
  "AAAA",
  "CNAME",
  "MX",
  "NS",
  "TXT",
  "SOA",
  "PTR",
] as const;

export type DnsRecordType = (typeof DNS_RECORD_TYPES)[number];

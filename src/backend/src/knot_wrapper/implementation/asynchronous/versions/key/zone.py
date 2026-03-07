from dataclasses import dataclass

@dataclass(frozen=True)
class ZoneKey:
    zone: str
    owner: str
    type: str
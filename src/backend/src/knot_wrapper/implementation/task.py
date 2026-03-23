
from pydantic import BaseModel
from enum import Enum

class DNSTaskType(Enum):
    conf_set = "conf-set"
    conf_unset = "conf-unset"
    zone_set = "zone_set"
    zone_unset = "zone_unset"
    zone_backup = "zone-bacup"
    zone_restore = "zone-restore"

class DNSCommitType(Enum):
    conf = "conf"
    zone = "zone"

class DNSCommand(BaseModel):
    type: DNSTaskType
    data: dict[str, str | None]

class DNSCommit(BaseModel):
    type: DNSCommitType
    zone_name: str | None
    tasks: list[DNSCommand]
    versions: dict[str, int | None]
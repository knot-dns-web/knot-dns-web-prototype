from libknot.control import KnotCtl

def get_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    owner: str | None = None,
    type: str | None = None
):
    ctl.send_block(
        cmd="zone-read",
        zone=zone, # type: ignore
        owner=owner, # type: ignore
        rtype=type # type: ignore
    )
    return ctl.receive_block()

def set_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    owner: str | None = None,
    type: str | None = None,
    ttl: str | None = None,
    data: str | None = None
):
    ctl.send_block(
        cmd="zone-set",
        zone=zone, # type: ignore
        owner=owner, # type: ignore
        rtype=type, # type: ignore
        ttl=ttl, # type: ignore
        data=data # type: ignore
    )
    ctl.receive_block()

def unset_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    owner: str | None = None,
    type: str | None = None,
    data: str | None = None
):
    ctl.send_block(
        cmd="zone-unset",
        zone=zone, # type: ignore
        owner=owner, # type: ignore
        rtype=type, # type: ignore
        data=data # type: ignore
    )
    ctl.receive_block()

def status_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    filters: str | None = None 
):
    ctl.send_block(
        cmd="zone-status",
        zone=zone, # type: ignore
        filters=filters # type: ignore
    )
    return ctl.receive_block()

def backup_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    dir_path: str | None = None,
    filters: str | None = None
):
    ctl.send_block(
        cmd="zone-backup", 
        zone=zone, # type: ignore
        data=dir_path, # type: ignore
        filters=filters # type: ignore
    )
    ctl.receive_block()

def restore_zone(
    ctl: KnotCtl,
    zone: str | None = None,
    dir_path: str | None = None
):
    ctl.send_block(
        cmd="zone-restore", 
        zone=zone, # type: ignore
        data=dir_path # type: ignore
    )
    ctl.receive_block()
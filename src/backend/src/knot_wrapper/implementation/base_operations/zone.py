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
    result = ctl.receive_block()
    return result

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
    data: str | None = None):
    ctl.send_block(
        cmd="zone-unset",
        zone=zone, # type: ignore
        owner=owner, # type: ignore
        rtype=type, # type: ignore
        data=data # type: ignore
    )
    ctl.receive_block()
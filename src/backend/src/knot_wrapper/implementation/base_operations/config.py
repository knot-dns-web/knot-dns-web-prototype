from libknot.control import KnotCtl

def get_config(
    ctl: KnotCtl,
    section: str | None = None,
    identifier: str | None = None,
    item: str | None = None,
    flags: str | None = None,
    filters: str | None = None
):
    ctl.send_block(
        cmd="conf-read",
        section=section, # type: ignore
        identifier=identifier, # type: ignore
        item=item, # type: ignore
        flags=flags, # type: ignore
        filters=filters # type: ignore
    )
    result = ctl.receive_block()
    return result

def set_config(
    ctl: KnotCtl,
    section: str | None = None,
    identifier: str | None = None,
    item: str | None = None,
    data: str | None = None
):
    ctl.send_block(
        cmd="conf-set",
        section=section, # type: ignore
        identifier=identifier, # type: ignore
        item=item, # type: ignore
        data=data # type: ignore
    )
    ctl.receive_block()

def unset_config(
    ctl: KnotCtl,
    section: str | None = None,
    identifier: str | None = None,
    item: str | None = None
):
    ctl.send_block(
        cmd="conf-unset",
        section=section, # type: ignore
        identifier=identifier, # type: ignore
        item=item # type: ignore
    )
    ctl.receive_block()
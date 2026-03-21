from ...knot_wrapper.example import (
    get_all_records,
    add_record,
    remove_record
)


class RecordService:

    async def list_records(self):
        return await get_all_records()

    async def create_record(self, zone, owner, rtype, ttl, data):
        await add_record(zone, owner, rtype, str(ttl), data)

    async def delete_record(self, zone, owner, rtype):
        await remove_record(zone, owner, rtype)
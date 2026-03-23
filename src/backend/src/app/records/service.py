from ...knot_wrapper.implementation import (
    get_knot_zone_transaction
)

from libknot.control import KnotCtl
import os

default_knot_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
redis_path = "redis://redis:6379"
CHANNEL_NAME = "DNSCommitAsync"

class RecordService:

    async def list_records(self):        
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, None) as transaction:
            results = await transaction.get()

            return results

    async def create_record(self, zone, owner, rtype, ttl, data):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, zone) as transaction:
            await transaction.set(zone, owner, rtype, str(ttl), data)
            await transaction.commit()

    async def delete_record(self, zone, owner, rtype):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, zone) as transaction:
            await transaction.unset(zone, owner, rtype)
            await transaction.commit()

'''
{
  "zone": "aaa.",
  "owner": "@",
  "type": "MX",
  "ttl": 3600,
  "data": "10 mail.example.com."
}
'''

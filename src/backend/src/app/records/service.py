from ...knot_wrapper.implementation import (
    get_knot_zone_transaction
)

from libknot.control import KnotCtl
import os

from .knot_normalize import (
    knot_zone_block_to_records,
    normalize_knot_owner,
    normalize_knot_rr_type,
    normalize_knot_zone_fqdn,
)

default_knot_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
redis_path = "redis://redis:6379"
CHANNEL_NAME = "DNSCommitAsync"

class RecordService:

    async def list_records(self):        
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, None) as transaction:
            results = transaction.get()
            return knot_zone_block_to_records(results)

    async def create_record(self, zone, owner, rtype, ttl, data):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        z = normalize_knot_zone_fqdn(zone)
        own = normalize_knot_owner(owner, z)
        rt = normalize_knot_rr_type(rtype)

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, z) as transaction:
            await transaction.set(z, own, rt, str(ttl), data)
            await transaction.commit()

    async def delete_record(self, zone, owner, rtype, data=None):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        z = normalize_knot_zone_fqdn(zone)
        own = normalize_knot_owner(owner, z)
        rt = normalize_knot_rr_type(rtype)
        unset_data = data if data not in (None, "") else None

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, z) as transaction:
            await transaction.unset(z, own, rt, unset_data)
            await transaction.commit()

    async def update_record(
        self,
        zone,
        old_owner,
        old_type,
        old_data,
        new_owner,
        new_type,
        ttl,
        new_data,
    ):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        z = normalize_knot_zone_fqdn(zone)
        oo = normalize_knot_owner(old_owner, z)
        ot = normalize_knot_rr_type(old_type)
        no = normalize_knot_owner(new_owner, z)
        nt = normalize_knot_rr_type(new_type)
        unset_data = old_data if old_data not in (None, "") else None

        async with get_knot_zone_transaction(ctl, redis_path, CHANNEL_NAME, z) as transaction:
            await transaction.unset(z, oo, ot, unset_data)
            await transaction.set(z, no, nt, str(ttl), new_data)
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

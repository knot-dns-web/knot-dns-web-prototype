from ...knot_wrapper.implementation.synchronous import (
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

    def list_records(self):        
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        with get_knot_zone_transaction(ctl, None) as transaction:
            results = transaction.get()
            return knot_zone_block_to_records(results)

    def create_record(self, zone, owner, rtype, ttl, data):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        z = normalize_knot_zone_fqdn(zone)
        own = normalize_knot_owner(owner, z)
        rt = normalize_knot_rr_type(rtype)

        with get_knot_zone_transaction(ctl, z) as transaction:
            transaction.set(z, own, rt, str(ttl), data)
            transaction.commit()

    def delete_record(self, zone, owner, rtype, data=None):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        z = normalize_knot_zone_fqdn(zone)
        own = normalize_knot_owner(owner, z)
        rt = normalize_knot_rr_type(rtype)
        unset_data = data if data not in (None, "") else None

        with get_knot_zone_transaction(ctl, z) as transaction:
            transaction.unset(z, own, rt, unset_data)
            transaction.commit()

    def update_record(
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

        with get_knot_zone_transaction(ctl, z) as transaction:
            transaction.unset(z, oo, ot, unset_data)
            transaction.set(z, no, nt, str(ttl), new_data)
            transaction.commit()

'''
{
  "zone": "aaa.",
  "owner": "@",
  "type": "MX",
  "ttl": 3600,
  "data": "10 mail.example.com."
}
'''

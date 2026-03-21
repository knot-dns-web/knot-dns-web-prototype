from ...knot_wrapper.implementation.synchronous import (
    get_knot_zone_transaction
)

from libknot.control import KnotCtl
import os

default_knot_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")
redis_path = "redis://redis:6379"
CHANNEL_NAME = "DNSCommitAsync"

class RecordService:

    def list_records(self):        
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        with get_knot_zone_transaction(ctl, None) as transaction:
            results = transaction.get()

            return results

    def create_record(self, zone, owner, rtype, ttl, data):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        with get_knot_zone_transaction(ctl, zone) as transaction:
            transaction.set(zone, owner, rtype, str(ttl), data)
            transaction.commit()

    def delete_record(self, zone, owner, rtype):
        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        with get_knot_zone_transaction(ctl, zone) as transaction:
            transaction.unset(zone, owner, rtype)
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

from ...knot_wrapper.example import (
    get_all_records,
    add_record,
    remove_record
)


class RecordService:

    def list_records(self):
        return get_all_records()

    def create_record(self, zone, owner, rtype, ttl, data):
        add_record(zone, owner, rtype, str(ttl), data)

    def delete_record(self, zone, owner, rtype):
        remove_record(zone, owner, rtype)
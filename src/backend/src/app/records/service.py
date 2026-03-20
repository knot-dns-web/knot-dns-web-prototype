from ...knot_wrapper.transaction import get_knot_connection, get_knot_zone_transaction

# from ...knot_wrapper.example import (
#     get_all_records,
#     add_record,
#     remove_record
# )

class RecordService:

    def list_records(self, user):        
        with get_knot_connection() as connection:
            with get_knot_zone_transaction(connection, None) as transaction:
                results = transaction.get()

                return results

    def create_record(self, zone, owner, rtype, ttl, data, user):
        with get_knot_connection() as connection:
                with get_knot_zone_transaction(connection, zone) as transaction:
                    transaction.set(zone, owner, rtype, ttl, data)
                    transaction.commit()

    def delete_record(self, zone, owner, rtype, user):
        with get_knot_connection() as connection:
            with get_knot_zone_transaction(connection, zone) as transaction:
                transaction.unset(zone, owner, rtype)
                transaction.commit()
        
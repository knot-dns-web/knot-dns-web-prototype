from ...knot_wrapper.example import (
    get_all_zones,
    add_zone,
    remove_zone
)


class ZoneService:

    def list_zones(self):
        return get_all_zones()

    def create_zone(self, name: str):
        add_zone(name)

    def delete_zone(self, name: str):
        remove_zone(name)
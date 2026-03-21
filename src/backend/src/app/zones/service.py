from ...knot_wrapper.transaction import (
    get_knot_connection,
    get_knot_config_transaction,
    get_knot_zone_transaction
)

from ...knot_wrapper.example import (
    get_all_zones,
    add_zone,
    remove_zone
)

from .core import validate_zone_name, generate_serial


class ZoneService:

    def create_zone(self, name: str):

        validate_zone_name(name)
        serial = generate_serial()

        with get_knot_connection() as connection:

            # создаём зону
            with get_knot_config_transaction(connection) as transaction:
                transaction.set("zone", name)
                transaction.commit()

            # добавляем записи NS и SOA
            with get_knot_zone_transaction(connection, name) as transaction:

                # Убираем точку из имени зоны для формирования имен NS серверов
                zone_without_dot = name.rstrip('.')
                
                # Формируем имена с одной точкой в конце
                ns1 = f"ns1.{zone_without_dot}."
                ns2 = f"ns2.{zone_without_dot}."

                transaction.set(zone_without_dot, "@", "NS", "3600", ns1)
                transaction.set(zone_without_dot, "@", "NS", "3600", ns2)

                transaction.set(zone_without_dot, "ns1", "A", "3600", "127.0.0.1")
                transaction.set(zone_without_dot, "ns2", "A", "3600", "127.0.0.1")

                soa_data = (
                    f"ns1.{zone_without_dot}. hostmaster.{zone_without_dot}. "
                    f"{serial} 7200 3600 1209600 3600"
                )

                transaction.set(zone_without_dot, "@", "SOA", "3600", soa_data)
                transaction.commit()
    
    async def list_zones(self):
        return await get_all_zones()

    # def create_zone(self, name: str):
    #     add_zone(name)

    def delete_zone(self, name: str):
        remove_zone(name)
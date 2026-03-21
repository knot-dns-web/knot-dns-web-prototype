from ...knot_wrapper.example import (
    get_all_zones,
    add_zone,
    remove_zone,
    get_knot_config_transaction,
    get_knot_zone_transaction
)
import os

from libknot.control import KnotCtl

from .core import validate_zone_name, generate_serial

default_knot_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")

redis_path = "redis://redis:6379"

CHANNEL_NAME = "DNSCommitAsync"

class ZoneService:

    async def create_zone(self, name: str):
        global default_knot_path, redis_path

        validate_zone_name(name)
        serial = generate_serial()

        ctl = KnotCtl()
        ctl.connect(default_knot_path)

        # создаём зону
        async with get_knot_config_transaction(ctl, redis_path, CHANNEL_NAME) as transaction:
            await transaction.set("zone", name)
            await transaction.commit()
        
        # добавляем записи NS и SOA
        async with get_knot_zone_transaction(ctl, redis_path, name) as transaction:

            # Убираем точку из имени зоны для формирования имен NS серверов
            zone_without_dot = name.rstrip('.')
            
            # Формируем имена с одной точкой в конце
            ns1 = f"ns1.{zone_without_dot}."
            ns2 = f"ns2.{zone_without_dot}."

            await transaction.set(zone_without_dot, "@", "NS", "3600", ns1)
            await transaction.set(zone_without_dot, "@", "NS", "3600", ns2)

            await transaction.set(zone_without_dot, "ns1", "A", "3600", "127.0.0.1")
            await transaction.set(zone_without_dot, "ns2", "A", "3600", "127.0.0.1")

            soa_data = (
                f"ns1.{zone_without_dot}. hostmaster.{zone_without_dot}. "
                f"{serial} 7200 3600 1209600 3600"
            )

            await transaction.set(zone_without_dot, "@", "SOA", "3600", soa_data)
            await transaction.commit()
        

    async def list_zones(self):
        return await get_all_zones()

    # def create_zone(self, name: str):
    #     add_zone(name)

    async def delete_zone(self, name: str):
        await remove_zone(name)
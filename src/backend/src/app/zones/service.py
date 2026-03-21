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
from typing import Any

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
    
    def list_zones(self):
        with get_knot_connection() as connection:
            with get_knot_config_transaction(connection) as transaction:
                result = transaction.get(section="zone")
                if len(result) == 0:
                    return tuple()
                zones_dict: dict[str, Any] = result['zone']
                zones = tuple((name for name in zones_dict))

                return zones

    def delete_zone(self, name: str):
        with get_knot_connection() as connection:
            with get_knot_config_transaction(connection) as transaction:
                transaction.unset("zone", name)
                transaction.commit()

    def export_zone(self, name: str):
        with get_knot_connection() as connection:
            with get_knot_zone_transaction(connection, name) as transaction:
                records_data = transaction.get()
        
        print(f"DEBUG records_data: {records_data}")
        
        if not records_data:
            raise ValueError("Zone is empty")
        
        lines = []
        
        # Проходим по всем owner'ам на 1-м уровне
        for owner_name, owner_data in records_data.items():
            display_owner = '@' if owner_name.rstrip('.') == name.rstrip('.') else owner_name.rstrip('.')
            
            # Проходим по записям внутри owner'а (2-й уровень)
            for inner_owner, rrsets in owner_data.items():
                for rtype, rrdata in rrsets.items():
                    ttl = rrdata.get('ttl', '3600')
                    data_list = rrdata.get('data', [])
                    
                    for data_item in data_list:
                        lines.append(f"{display_owner} {ttl} IN {rtype} {data_item}")
        
        if not lines:
            raise ValueError("No records found in zone")

        return '\n'.join(lines)


    def import_zone(self, name: str, content: str):

        validate_zone_name(name)

        with get_knot_connection() as connection:

            # создаём зону
            with get_knot_config_transaction(connection) as transaction:
                transaction.set("zone", name)
                transaction.commit()

            # добавляем записи
            with get_knot_zone_transaction(connection, name) as transaction:

                for line in content.splitlines():
                    line = line.strip()

                    if not line or line.startswith(";"):
                        continue

                    parts = line.split()

                    if len(parts) < 5:
                        continue

                    owner, ttl, _, rtype, *data = parts
                    data = " ".join(data)

                    transaction.set(name.rstrip("."), owner, rtype, ttl, data)

                transaction.commit()

"""
{
  "name": "example.com",
  "content": "@ 3600 IN SOA ns1.example.com. hostmaster.example.com. 2024031901 7200 3600 1209600 3600\n@ 3600 IN NS ns1.example.com.\n@ 3600 IN NS ns2.example.com.\nns1 3600 IN A 127.0.0.1\nns2 3600 IN A 127.0.0.1\nwww 3600 IN A 192.168.1.10"
}
"""

from typing import Any
import threading
import os

from .implementation.asynchronous.service import *
from .transaction import get_knot_config_transaction, get_knot_zone_transaction, get_knot_connection, set_knot_connection_path

from .implementation.asynchronous.service.processor import global_processor

default_knot_path = os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")

def get_all_zones():
    with get_knot_connection() as connection:
        with get_knot_config_transaction(connection) as transaction:
            result = transaction.get(section="zone")
            if len(result) == 0:
                return tuple()
            zones_dict: dict[str, Any] = result['zone']
            zones = tuple((name for name in zones_dict))
            return zones

def add_zone(zone_name: str):
    with get_knot_connection() as connection:
        with get_knot_config_transaction(connection) as transaction:
            transaction.set("zone", zone_name)

def remove_zone(zone_name: str):
    with get_knot_connection() as connection:
        with get_knot_config_transaction(connection) as transaction:
            transaction.unset("zone", zone_name)

def get_all_records():
    with get_knot_connection() as connection:
        with get_knot_zone_transaction(connection, None) as transaction:
            results = transaction.get()
            return results
        
def add_record(zone_name: str, owner: str, rtype: str, ttl: str, data: str):
    with get_knot_connection() as connection:
        with get_knot_zone_transaction(connection, zone_name) as transaction:
            transaction.set(zone_name, owner, rtype, ttl, data)

def remove_record(zone_name: str, owner: str, rtype: str):
    with get_knot_connection() as connection:
        with get_knot_zone_transaction(connection, zone_name) as transaction:
            transaction.unset(zone_name, owner, rtype)

menu_choice = \
"""
Menu
1. Get all zones
2. Add zone
3. Remove zone
4. Get all records
5. Add record
6. Remove record
"""

def start_processor():
    global_processor.run()

def menu():
    while True:
        print("")
        print(menu_choice)
        text = input()
        items = text.split()
        if len(items) == 0:
            continue
        if items[0] == "exit":
            break
        listitem = int(text[0])
        match listitem:
            case 1:
                zones = get_all_zones()
                print("\n".join(zones))
            case 2:
                if len(items) < 2:
                    print("This command require 2 parameters")
                    continue
                zone_name = items[1]
                add_zone(zone_name)
            case 3:
                if len(items) < 2:
                    print("This command require 2 parameters")
                    continue
                zone_name = items[1]
                remove_zone(zone_name)
            case 4:
                records = get_all_records()
                print("\n".join(records))
            case 5:
                if len(items) < 6:
                    print("This command require 6 parameters")
                    continue
                zone_name = items[1]
                owner = items[2]
                rtype = items[3]
                ttl = items[4]
                data = items[5]

                add_record(zone_name, owner, rtype, ttl, data)
            case 6:
                if len(items) < 4:
                    print("This command require 4 parameters")
                    continue
                zone_name = items[1]
                owner = items[2]
                rtype = items[3]

                remove_record(zone_name, owner, rtype)

def main():
    global menu_choice, default_knot_path

    set_knot_connection_path(default_knot_path)

    thread = threading.Thread(target=menu)
    thread.start()

    start_processor()

if __name__ == "__main__":
    main()
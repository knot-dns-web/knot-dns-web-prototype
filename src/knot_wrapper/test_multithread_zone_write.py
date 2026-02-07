import threading
import time
from libknot.control import KnotCtl

SOCKET = "/run/knot/knot.sock"
ZONES = ["example1.com", "example2.com"]

def write(zone_name):
    ctl = KnotCtl()
    try:
        ctl.connect(SOCKET)
        ctl.set_timeout(20)
        
        print(f"[Worker {zone_name}] начало записи")
        ctl.send_block(cmd="zone-begin", zone=zone_name)
        ctl.receive_block()

        for i in range(3):
            print(f"[Worker {zone_name}] добавление записи {i}")
            ctl.send_block(cmd="zone-set", zone=zone_name, 
                           owner=f"test{i}", rtype="A", data="1.1.1.1")
            ctl.receive_block()
            time.sleep(1) 

        ctl.send_block(cmd="zone-commit", zone=zone_name)
        ctl.receive_block()
        print(f"[Worker {zone_name}] завершение записи")
        
    except Exception as e:
        print(f"[Worker {zone_name}] ОШИБКА: {e}")
    finally:
        ctl.close()

def init():
    ctl = KnotCtl()
    try:
        ctl.connect(SOCKET)

        try:
            ctl.send_block(cmd="conf-abort")
            ctl.receive_block()
        except:
            pass

        ctl.send_block(cmd="conf-begin")
        ctl.receive_block()
        ctl.send_block(cmd="conf-set", section="control", item="timeout", data="10")
        ctl.receive_block()
        ctl.send_block(cmd="conf-commit")
        ctl.receive_block()

        for zone in ZONES:
            try:
                ctl.send_block(cmd="zone-abort", zone=zone)
                ctl.receive_block()
            except:
                pass

        for zone in ZONES:
            ctl.send_block(cmd="zone-begin", zone=zone)
            ctl.receive_block()

            for i in range(1000):
                try:
                    ctl.send_block(cmd="zone-unset", zone=zone, owner=f"test{i}", rtype="A", data="1.1.1.1")
                    ctl.receive_block()
                except:
                    pass
            ctl.send_block(cmd="zone-commit", zone=zone)
            ctl.receive_block()
    finally:
        ctl.close()

init()

threads: list[threading.Thread] = []
for zone in ZONES:
    t = threading.Thread(target=write, args=(zone,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
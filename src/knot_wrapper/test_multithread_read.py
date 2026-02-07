import threading
import time
from libknot.control import KnotCtl

SOCKET = "/run/knot/knot.sock"
ZONE = "example.com"

WRITER_FIRST = False

def reader(thread_id):
    ctl = KnotCtl()
    try:
        ctl.connect(SOCKET)
        for _ in range(2):
            print(f"[Reader {thread_id}] начал чтение")
            ctl.send_block(cmd="zone-read", zone=ZONE)
            result = ctl.receive_block()

            # Имитируем нагрузку
            time.sleep(0.5)
            print(f"[Reader {thread_id}] завершил чтение")
    finally:
        ctl.close()

def writer():
    ctl = KnotCtl()
    ctl.set_timeout(10)
    try:
        ctl.connect(SOCKET)
        print("[Writer] начал запись")
        ctl.send_block(cmd="zone-begin", zone=ZONE)
        ctl.receive_block()

        for i in range(1000):
            ctl.send_block(cmd="zone-set", zone=ZONE, owner=f"test{i}", rtype="A", data="1.2.3.4")
            ctl.receive_block()

            # Имитируем нагрузку
            if i == 500:
                if WRITER_FIRST:
                    time.sleep(0.8)
                else:
                    time.sleep(3)

        ctl.send_block(cmd="zone-commit", zone=ZONE)
        ctl.receive_block()
        print("[Writer] завершение записи")
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

        try:
            ctl.send_block(cmd="zone-abort", zone=ZONE)
            ctl.receive_block()
        except:
            pass
        ctl.send_block(cmd="zone-begin", zone=ZONE)
        ctl.receive_block()

        for i in range(1000):
            try:
                ctl.send_block(cmd="zone-unset", zone=ZONE, owner=f"test{i}", rtype="A", data="1.2.3.4")
                ctl.receive_block()
            except:
                pass
        ctl.send_block(cmd="zone-commit", zone=ZONE)
        ctl.receive_block()
    finally:
        ctl.close()

init()

# 1. Запускаем читателей
readers = [threading.Thread(target=reader, args=(i,)) for i in range(5)]
for r in readers:
    r.start()

# 2. Запускаем писателя
write_thread = threading.Thread(target=writer)
write_thread.start()

for r in readers:
    r.join()
write_thread.join()
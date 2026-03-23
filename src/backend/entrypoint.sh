#!/bin/sh

knotd -C /var/lib/knot -s /run/knot/knot.sock -d
#knotd -c /etc/knot/knot.conf -d

if [ -z "$DEBUG" ]; then
    exec python -m uvicorn src.src.app.main:app --reload --host 0.0.0.0 --port 8000
fi

sleep infinity
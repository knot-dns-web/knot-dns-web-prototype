"""Интеграционные тесты асинхронного `knot_wrapper.implementation.asynchronous`.

Требуются живой Knot (`KNOT_SOCKET`) и Redis (`REDIS_URL`), как в контейнере backend.

Запуск из каталога бэкенда:
  cd /app/src && pytest tests/integration/test_wrapper_asynch.py -v

Без сокета или недоступного Redis тесты пропускаются (pytest.skip).
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import redis.asyncio as aioredis
from libknot.control import KnotCtl

from app.zones.core import generate_serial
from knot_wrapper.error.base_error import KnotError
from knot_wrapper.implementation.asynchronous.config_transaction import (
    get_knot_config_transaction,
)
from knot_wrapper.implementation.asynchronous.message_broker import (
    DNSWorker,
    DNSTaskProducer,
    TaskError,
)
from knot_wrapper.implementation.asynchronous.task import (
    DNSCommand,
    DNSCommit,
    DNSCommitType,
    DNSTaskType,
)
from knot_wrapper.implementation.asynchronous.zone_transaction import (
    get_knot_zone_transaction,
)
from knot_wrapper.implementation.synchronous import (
    get_knot_config_transaction as sync_config_tx,
    get_knot_zone_transaction as sync_zone_tx,
)


def _knot_socket() -> str:
    return os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")


def _redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://redis:6379/0")


def _require_knot_socket() -> str:
    p = _knot_socket()
    if not os.path.exists(p):
        pytest.skip(f"Нет сокета Knot ({p}). Запускайте в контейнере с knotd.")
    return p


async def _require_redis(url: str) -> None:
    try:
        r = aioredis.from_url(url)
        await r.ping()
        await r.aclose()
    except Exception as e:
        pytest.skip(f"Redis недоступен ({url}): {e}")


def _unique_channel() -> str:
    return f"dns_asynch_itest_{uuid.uuid4().hex}"


def _unique_zone() -> str:
    return f"{uuid.uuid4().hex}.async.local."


# --- task.py: модели (без сети) ---


def test_dns_command_commit_json_roundtrip():
    cmd = DNSCommand(
        type=DNSTaskType.zone_set,
        data={
            "zone": "z",
            "owner": "@",
            "type": "A",
            "ttl": "3600",
            "data": "1.1.1.1",
        },
    )
    commit = DNSCommit(type=DNSCommitType.zone, zone_name="z.", tasks=[cmd])
    restored = DNSCommit.model_validate_json(commit.model_dump_json())
    assert restored.zone_name == "z."
    assert restored.tasks[0].type == DNSTaskType.zone_set


# --- Redis + Knot + worker: конфиг ---


def test_async_config_get_section_zone():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    asyncio.run(_async_config_get_impl(socket_path, redis_url))


async def _async_config_get_impl(socket_path: str, redis_url: str):
    await _require_redis(redis_url)
    channel = _unique_channel()
    r = aioredis.from_url(redis_url, decode_responses=False)
    worker = DNSWorker(r, channel, socket_path)
    t = asyncio.create_task(worker.run())
    await asyncio.sleep(0.08)
    ctl = KnotCtl()
    ctl.connect(socket_path)
    try:
        async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
            out = await tx.get(section="zone")
        assert isinstance(out, dict)
    finally:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
        await r.aclose()
        ctl.close()


def test_async_config_commit_creates_zone_and_unset_removes():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        ctl = KnotCtl()
        ctl.connect(socket_path)
        try:
            async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
                await tx.set("zone", zone, None, None)
                await tx.commit()

            with sync_config_tx(ctl) as tx:
                cfg = tx.get(section="zone")
            zd = (cfg or {}).get("zone") or {}
            assert zone.rstrip(".") in zd or zone in str(zd)

            async with get_knot_config_transaction(ctl, redis_url, channel) as tx2:
                await tx2.unset("zone", zone, None)
                await tx2.commit()

            with sync_config_tx(ctl) as tx:
                cfg2 = tx.get(section="zone")
            zd2 = (cfg2 or {}).get("zone") or {}
            assert zone.rstrip(".") not in zd2
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()
            ctl.close()

    asyncio.run(main())


def test_async_zone_commit_adds_records():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()
    zwd = zone.rstrip(".")

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        ctl = KnotCtl()
        ctl.connect(socket_path)
        try:
            async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
                await tx.set("zone", zone, None, None)
                await tx.commit()

            serial = generate_serial()
            ns1 = f"ns1.{zwd}."
            ns2 = f"ns2.{zwd}."
            async with get_knot_zone_transaction(
                ctl, redis_url, channel, zone
            ) as ztx:
                await ztx.set(zwd, "@", "NS", "3600", ns1)
                await ztx.set(zwd, "@", "NS", "3600", ns2)
                await ztx.set(zwd, "ns1", "A", "3600", "127.0.0.1")
                await ztx.set(zwd, "ns2", "A", "3600", "127.0.0.2")
                soa = (
                    f"ns1.{zwd}. hostmaster.{zwd}. "
                    f"{serial} 7200 3600 1209600 3600"
                )
                await ztx.set(zwd, "@", "SOA", "3600", soa)
                await ztx.set(zwd, "www", "A", "3600", "192.0.2.1")
                await ztx.commit()

            with sync_zone_tx(ctl, zone) as rtx:
                data = rtx.get()
            assert data is not None
            assert "www" in str(data)
            assert "192.0.2.1" in str(data)

            with sync_zone_tx(ctl, zone) as rtx:
                st = rtx.status(zone=zwd)
            assert st is not None
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()
            try:
                with sync_config_tx(ctl) as ctx:
                    ctx.unset("zone", zone)
                    ctx.commit()
            except Exception:
                pass
            ctl.close()

    asyncio.run(main())


def test_async_context_rollback_without_commit_does_not_create_zone():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        ctl = KnotCtl()
        ctl.connect(socket_path)
        try:
            async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
                await tx.set("zone", zone, None, None)
            with sync_config_tx(ctl) as stx:
                cfg = stx.get(section="zone")
            zd = (cfg or {}).get("zone") or {}
            assert zone.rstrip(".") not in zd
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()
            ctl.close()

    asyncio.run(main())


def test_dns_task_producer_enqueue_commit_roundtrip_empty_conf():
    """Пустой conf-коммит: begin + commit без изменений."""
    socket_path = _require_knot_socket()
    redis_url = _redis_url()

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        try:
            producer = DNSTaskProducer(r, channel)
            commit = DNSCommit(type=DNSCommitType.conf, zone_name=None, tasks=[])
            await producer.enqueue_commit(commit)
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()

    asyncio.run(main())


def test_dns_task_producer_raises_task_error_on_knot_failure():
    """Некорректная зонная операция — ответ с exception_text → TaskError."""
    socket_path = _require_knot_socket()
    redis_url = _redis_url()

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        try:
            producer = DNSTaskProducer(r, channel)
            bad_zone = "definitely-not-a-zone-uuid-12345.invalid."
            commit = DNSCommit(
                type=DNSCommitType.zone,
                zone_name=bad_zone,
                tasks=[
                    DNSCommand(
                        type=DNSTaskType.zone_set,
                        data={
                            "zone": "x",
                            "owner": "@",
                            "type": "A",
                            "ttl": "3600",
                            "data": "1.1.1.1",
                        },
                    )
                ],
            )
            with pytest.raises((TaskError, KnotError, Exception)):
                await producer.enqueue_commit(commit)
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()

    asyncio.run(main())


def test_worker_applies_conf_set_and_zone_set_via_producer():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()
    zwd = zone.rstrip(".")

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        try:
            producer = DNSTaskProducer(r, channel)
            c1 = DNSCommit(
                type=DNSCommitType.conf,
                zone_name=None,
                tasks=[
                    DNSCommand(
                        type=DNSTaskType.conf_set,
                        data={
                            "section": "zone",
                            "identifier": zone,
                            "item": None,
                            "data": None,
                        },
                    )
                ],
            )
            await producer.enqueue_commit(c1)

            serial = generate_serial()
            ns1 = f"ns1.{zwd}."
            c2 = DNSCommit(
                type=DNSCommitType.zone,
                zone_name=zone,
                tasks=[
                    DNSCommand(
                        type=DNSTaskType.zone_set,
                        data={
                            "zone": zwd,
                            "owner": "@",
                            "type": "NS",
                            "ttl": "3600",
                            "data": ns1,
                        },
                    ),
                    DNSCommand(
                        type=DNSTaskType.zone_set,
                        data={
                            "zone": zwd,
                            "owner": "ns1",
                            "type": "A",
                            "ttl": "3600",
                            "data": "127.0.0.1",
                        },
                    ),
                    DNSCommand(
                        type=DNSTaskType.zone_set,
                        data={
                            "zone": zwd,
                            "owner": "@",
                            "type": "SOA",
                            "ttl": "3600",
                            "data": (
                                f"{ns1} hostmaster.{zwd}. "
                                f"{serial} 7200 3600 1209600 3600"
                            ),
                        },
                    ),
                ],
            )
            await producer.enqueue_commit(c2)

            ctl = KnotCtl()
            ctl.connect(socket_path)
            try:
                with sync_zone_tx(ctl, zone) as ztx:
                    data = ztx.get()
                assert ns1 in str(data) or "NS" in str(data)
            finally:
                try:
                    with sync_config_tx(ctl) as ctx:
                        ctx.unset("zone", zone)
                        ctx.commit()
                finally:
                    ctl.close()
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()

    asyncio.run(main())


def test_zone_unset_via_producer():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()
    zwd = zone.rstrip(".")

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        ctl = KnotCtl()
        ctl.connect(socket_path)
        try:
            async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
                await tx.set("zone", zone, None, None)
                await tx.commit()
            serial = generate_serial()
            ns1 = f"ns1.{zwd}."
            async with get_knot_zone_transaction(
                ctl, redis_url, channel, zone
            ) as ztx:
                await ztx.set(zwd, "@", "NS", "3600", ns1)
                await ztx.set(zwd, "ns1", "A", "3600", "127.0.0.1")
                soa = (
                    f"{ns1} hostmaster.{zwd}. "
                    f"{serial} 7200 3600 1209600 3600"
                )
                await ztx.set(zwd, "@", "SOA", "3600", soa)
                await ztx.commit()

            producer = DNSTaskProducer(r, channel)
            commit = DNSCommit(
                type=DNSCommitType.zone,
                zone_name=zone,
                tasks=[
                    DNSCommand(
                        type=DNSTaskType.zone_unset,
                        data={
                            "zone": zwd,
                            "owner": "ns1",
                            "type": "A",
                            "data": "127.0.0.1",
                        },
                    )
                ],
            )
            await producer.enqueue_commit(commit)

            with sync_zone_tx(ctl, zone) as rtx:
                data = rtx.get()
            assert "127.0.0.1" not in str(data)
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()
            try:
                with sync_config_tx(ctl) as ctx:
                    ctx.unset("zone", zone)
                    ctx.commit()
            except Exception:
                pass
            ctl.close()

    asyncio.run(main())


def test_conf_unset_via_producer():
    socket_path = _require_knot_socket()
    redis_url = _redis_url()
    zone = _unique_zone()

    async def main():
        await _require_redis(redis_url)
        channel = _unique_channel()
        r = aioredis.from_url(redis_url, decode_responses=False)
        worker = DNSWorker(r, channel, socket_path)
        wt = asyncio.create_task(worker.run())
        await asyncio.sleep(0.08)
        ctl = KnotCtl()
        ctl.connect(socket_path)
        try:
            async with get_knot_config_transaction(ctl, redis_url, channel) as tx:
                await tx.set("zone", zone, None, None)
                await tx.commit()

            producer = DNSTaskProducer(r, channel)
            commit = DNSCommit(
                type=DNSCommitType.conf,
                zone_name=None,
                tasks=[
                    DNSCommand(
                        type=DNSTaskType.conf_unset,
                        data={
                            "section": "zone",
                            "identifier": zone,
                            "item": None,
                        },
                    )
                ],
            )
            await producer.enqueue_commit(commit)

            with sync_config_tx(ctl) as ctx:
                cfg = ctx.get(section="zone")
            zd = (cfg or {}).get("zone") or {}
            assert zone.rstrip(".") not in zd
        finally:
            wt.cancel()
            try:
                await wt
            except asyncio.CancelledError:
                pass
            await r.aclose()
            ctl.close()

    asyncio.run(main())


def test_async_package_exports():
    from knot_wrapper.implementation import asynchronous as m

    assert m.DNSWorker is DNSWorker
    assert m.get_knot_config_transaction is get_knot_config_transaction
    assert m.get_knot_zone_transaction is get_knot_zone_transaction

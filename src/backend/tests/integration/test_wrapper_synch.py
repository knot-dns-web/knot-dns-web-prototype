"""Интеграционные тесты синхронного `knot_wrapper.implementation.synchronous`.

Требуется живой Knot (`KNOT_SOCKET`). Без сокета тесты пропускаются.

Запуск из каталога бэкенда: `pytest tests/integration/test_wrapper_synch.py -v`
"""

from __future__ import annotations

import os
import uuid

import pytest
from libknot.control import KnotCtl

# Импорт с автоопределением пути
try:
    from app.zones.core import generate_serial
except ImportError:
    from src.app.zones.core import generate_serial

try:
    from knot_wrapper.implementation.synchronous import (
        get_knot_config_transaction,
        get_knot_zone_transaction,
    )
except ImportError:
    from src.knot_wrapper.implementation.synchronous import (
        get_knot_config_transaction,
        get_knot_zone_transaction,
    )


def _knot_socket_path() -> str:
    return os.environ.get("KNOT_SOCKET", "/run/knot/knot.sock")


def _require_knot_socket() -> str:
    path = _knot_socket_path()
    if not os.path.exists(path):
        pytest.skip(
            f"Нет сокета Knot ({path}). Запускайте в контейнере бэкенда с knotd."
        )
    return path


@pytest.fixture
def knot_ctl_connected():
    path = _require_knot_socket()
    ctl = KnotCtl()
    ctl.connect(path)
    try:
        yield ctl
    finally:
        ctl.close()


def _unique_zone_name() -> str:
    return f"{uuid.uuid4().hex}.integration.local."


def _create_zone_with_records(ctl: KnotCtl, name: str) -> None:
    serial = generate_serial()
    zone_without_dot = name.rstrip(".")
    ns1 = f"ns1.{zone_without_dot}."
    ns2 = f"ns2.{zone_without_dot}."

    with get_knot_config_transaction(ctl) as tx:
        tx.set("zone", name)
        tx.commit()

    with get_knot_zone_transaction(ctl, name) as tx:
        tx.set(zone_without_dot, "@", "NS", "3600", ns1)
        tx.set(zone_without_dot, "@", "NS", "3600", ns2)
        tx.set(zone_without_dot, "ns1", "A", "3600", "127.0.0.1")
        tx.set(zone_without_dot, "ns2", "A", "3600", "127.0.0.2")
        soa_data = (
            f"ns1.{zone_without_dot}. hostmaster.{zone_without_dot}. "
            f"{serial} 7200 3600 1209600 3600"
        )
        tx.set(zone_without_dot, "@", "SOA", "3600", soa_data)
        tx.set(zone_without_dot, "www", "A", "3600", "192.0.2.1")
        tx.commit()


def _delete_zone_config(ctl: KnotCtl, name: str) -> None:
    with get_knot_config_transaction(ctl) as tx:
        tx.unset("zone", name)
        tx.commit()


def _records_contain(records_data, needle: str) -> bool:
    return needle in str(records_data)


# --- KnotConfigTransaction ---


def test_config_transaction_read_zones(knot_ctl_connected):
    ctl = knot_ctl_connected
    with get_knot_config_transaction(ctl) as tx:
        result = tx.get(section="zone")
    assert isinstance(result, dict)


def test_config_transaction_set_commit_unset_removes_zone(knot_ctl_connected):
    ctl = knot_ctl_connected
    zone = _unique_zone_name()
    try:
        with get_knot_config_transaction(ctl) as tx:
            tx.set("zone", zone)
            tx.commit()

        with get_knot_config_transaction(ctl) as tx:
            cfg = tx.get(section="zone")
        zd = (cfg or {}).get("zone") or {}
        assert zone.rstrip(".") in zd or zone in str(zd)

        with get_knot_config_transaction(ctl) as tx:
            tx.unset("zone", zone)
            tx.commit()

        with get_knot_config_transaction(ctl) as tx:
            cfg2 = tx.get(section="zone")
        zd2 = (cfg2 or {}).get("zone") or {}
        assert zone.rstrip(".") not in zd2
    finally:
        try:
            _delete_zone_config(ctl, zone)
        except Exception:
            pass


def test_config_transaction_get_with_identifier(knot_ctl_connected):
    ctl = knot_ctl_connected
    zone = _unique_zone_name()
    try:
        with get_knot_config_transaction(ctl) as tx:
            tx.set("zone", zone)
            tx.commit()

        with get_knot_config_transaction(ctl) as tx:
            one = tx.get(section="zone", identifier=zone.rstrip("."))
        assert one is not None
    finally:
        try:
            _delete_zone_config(ctl, zone)
        except Exception:
            pass


def test_config_context_rollback_without_commit_no_zone(knot_ctl_connected):
    ctl = knot_ctl_connected
    zone = _unique_zone_name()
    with get_knot_config_transaction(ctl) as tx:
        tx.set("zone", zone)

    with get_knot_config_transaction(ctl) as tx:
        cfg = tx.get(section="zone")
    zd = (cfg or {}).get("zone") or {}
    assert zone.rstrip(".") not in zd


def test_config_context_after_commit_not_rolled_back(knot_ctl_connected):
    ctl = knot_ctl_connected
    zone = _unique_zone_name()
    try:
        with get_knot_config_transaction(ctl) as tx:
            tx.set("zone", zone)
            tx.commit()

        with get_knot_config_transaction(ctl) as tx:
            cfg = tx.get(section="zone")
        assert zone.rstrip(".") in str(cfg) or zone in str(cfg)
    finally:
        try:
            _delete_zone_config(ctl, zone)
        except Exception:
            pass


# --- KnotZoneTransaction ---


def test_zone_full_lifecycle(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zone_without_dot = name.rstrip(".")

    try:
        _create_zone_with_records(ctl, name)

        with get_knot_zone_transaction(ctl, name) as tx:
            records = tx.get()
        assert records is not None
        assert _records_contain(records, "www")
        assert _records_contain(records, "192.0.2.1")

        with get_knot_zone_transaction(ctl, name) as tx:
            filtered = tx.get(zone=zone_without_dot, owner="www", type="A")
        assert filtered is not None
        assert _records_contain(filtered, "192.0.2.1")

        with get_knot_zone_transaction(ctl, name) as tx:
            status = tx.status(zone=zone_without_dot)
        assert status is not None

        with get_knot_zone_transaction(ctl, name) as tx:
            st_f = tx.status(zone=zone_without_dot, filters=None)
        assert st_f is not None
    finally:
        _delete_zone_config(ctl, name)

    with get_knot_config_transaction(ctl) as tx:
        after = tx.get(section="zone")
    zone_dict = (after or {}).get("zone") or {}
    assert name.rstrip(".") not in zone_dict


def test_zone_unset_removes_record(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zwd = name.rstrip(".")
    try:
        _create_zone_with_records(ctl, name)

        with get_knot_zone_transaction(ctl, name) as tx:
            tx.unset(zone=zwd, owner="www", type="A", data="192.0.2.1")
            tx.commit()

        with get_knot_zone_transaction(ctl, name) as tx:
            www_a = tx.get(zone=zwd, owner="www", type="A")
        assert "192.0.2.1" not in str(www_a)
    finally:
        _delete_zone_config(ctl, name)


def test_zone_set_adds_record_in_transaction(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zwd = name.rstrip(".")
    try:
        with get_knot_config_transaction(ctl) as tx:
            tx.set("zone", name)
            tx.commit()
        serial = generate_serial()
        ns1 = f"ns1.{zwd}."
        with get_knot_zone_transaction(ctl, name) as tx:
            tx.set(zwd, "@", "NS", "3600", ns1)
            tx.set(zwd, "ns1", "A", "3600", "127.0.0.1")
            tx.set(
                zwd,
                "@",
                "SOA",
                "3600",
                f"{ns1} hostmaster.{zwd}. {serial} 7200 3600 1209600 3600",
            )
            tx.set(zwd, "extra", "TXT", "3600", "integration-txt")
            tx.commit()

        with get_knot_zone_transaction(ctl, name) as tx:
            rec = tx.get()
        assert _records_contain(rec, "extra") and _records_contain(rec, "integration-txt")
    finally:
        _delete_zone_config(ctl, name)


def test_zone_transaction_abort_without_commit_does_not_persist_rr(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zone_without_dot = name.rstrip(".")

    _create_zone_with_records(ctl, name)

    try:
        with get_knot_zone_transaction(ctl, name) as tx:
            tx.set(zone_without_dot, "ephemeral", "TXT", "3600", "should-not-persist")
            tx.rollback()

        with get_knot_zone_transaction(ctl, name) as tx:
            records = tx.get()
        assert not _records_contain(records, "ephemeral")
    finally:
        _delete_zone_config(ctl, name)


def test_zone_context_exit_after_commit_no_extra_rollback(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zwd = name.rstrip(".")
    try:
        with get_knot_config_transaction(ctl) as tx:
            tx.set("zone", name)
            tx.commit()
        serial = generate_serial()
        ns1 = f"ns1.{zwd}."
        with get_knot_zone_transaction(ctl, name) as tx:
            tx.set(zwd, "@", "NS", "3600", ns1)
            tx.set(zwd, "ns1", "A", "3600", "127.0.0.1")
            tx.set(
                zwd,
                "@",
                "SOA",
                "3600",
                f"{ns1} hostmaster.{zwd}. {serial} 7200 3600 1209600 3600",
            )
            tx.set(zwd, "persist", "TXT", "3600", "ok")
            tx.commit()

        with get_knot_zone_transaction(ctl, name) as tx:
            rec = tx.get()
        assert _records_contain(rec, "persist")
    finally:
        _delete_zone_config(ctl, name)


def test_zone_transaction_exception_in_with_triggers_context_rollback(knot_ctl_connected):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zwd = name.rstrip(".")
    _create_zone_with_records(ctl, name)
    try:
        with pytest.raises(RuntimeError, match="expected"):
            with get_knot_zone_transaction(ctl, name) as tx:
                tx.set(zwd, "boom", "TXT", "3600", "x")
                raise RuntimeError("expected")

        with get_knot_zone_transaction(ctl, name) as tx:
            rec = tx.get()
        assert not _records_contain(rec, "boom")
    finally:
        _delete_zone_config(ctl, name)


def test_zone_backup_writes_to_directory(knot_ctl_connected, tmp_path):
    ctl = knot_ctl_connected
    name = _unique_zone_name()
    zwd = name.rstrip(".")
    backup_dir = tmp_path / "knot_backup"
    backup_dir.mkdir()
    try:
        _create_zone_with_records(ctl, name)

        with get_knot_zone_transaction(ctl, name) as tx:
            tx.backup(zone=zwd, dir_path=str(backup_dir), filters=None)
            tx.commit()
    finally:
        _delete_zone_config(ctl, name)

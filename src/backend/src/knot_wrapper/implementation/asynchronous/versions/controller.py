from typing import Hashable, Any

from datetime import datetime, timezone

from threading import Lock

class VersionsController:
    def __init__(self) -> None:
        self.version: dict[Any, int] = dict()
        self.timestamp: dict[Any, datetime] = dict()

        self.controller_lock = Lock()

    def is_existed(
        self,
        key: Hashable
    ):
        with self.controller_lock:
            return key in self.version

    def get_version(
        self,
        key: Hashable
    ):
        with self.controller_lock:
            if not self.is_existed(key):
                raise KeyError
            version = self.version[key]
            return version

    def get_timestamp(
        self,
        key: Hashable
    ):
        with self.controller_lock:
            if not self.is_existed(key):
                raise KeyError
            timestamp = self.timestamp[key]
            return timestamp

    def versify(
        self,
        key: Hashable,
        start_version: int = 1,
        timestamp: datetime | None = None
    ):
        with self.controller_lock:
            if self.is_existed(key):
                raise KeyError
            
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)

            self.version[key] = start_version
            self.timestamp[key] = timestamp

    def diversify(
        self,
        key: Hashable
    ):
        with self.controller_lock:
            if not self.is_existed(key):
                raise KeyError
            del self.version[key]
            del self.timestamp[key]

    def up_version(
        self,
        key: Hashable,
        timestamp: datetime | None = None
    ):
        with self.controller_lock:
            if not self.is_existed(key):
                raise KeyError
            
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)

            self.version[key] += 1
            self.timestamp[key] = timestamp

    def is_valid_version(
        self,
        key: Hashable,
        compared_version: int
    ):
        with self.controller_lock:
            if not self.is_existed(key):
                raise KeyError
            
            version = self.version[key]
            return version > compared_version
        
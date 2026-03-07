from typing import Hashable

from .controller import VersionsController

from .errors import StaleDataError

class VersionsStorage:
    def __init__(self) -> None:
        self.version: dict[Hashable, int] = dict()

    def is_existed(
        self,
        key: Hashable
    ):
        return key in self.version
    
    def clear(self):
        self.version.clear()

    def get_version(
        self,
        key: Hashable
    ):
        if not self.is_existed(key):
            raise KeyError
        
        version = self.version[key]
        return version

    def try_object(
        self,
        controller: VersionsController,
        key: Hashable
    ):
        if not self.is_existed(key):
            version = controller.get_version(key)
            self.version[key] = version
        else:
            current_version = self.version[key]
            if not controller.is_valid_version(key, current_version):
                raise StaleDataError(key)
            
    def update_object(
        self,
        controller: VersionsController,
        key: Hashable
    ):
        pass
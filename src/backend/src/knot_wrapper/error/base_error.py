from libknot.control import KnotCtlError, KnotCtlData, KnotCtlDataIdx

from pydantic import BaseModel

from .raw_error_type import KnotErrorType

error_types_mapping = {KnotErrorType[name].value: KnotErrorType[name] for name in KnotErrorType._member_names_}

class KnotErrorData(BaseModel):
    command: str
    flags: str
    error: str
    section: str
    item: str
    id: str
    zone: str
    owner: str
    ttl: str
    type: str
    data: str
    filters: str

    @classmethod
    def from_raw_error_data(cls, data: KnotCtlData):
        return KnotErrorData(
            command = data[KnotCtlDataIdx.COMMAND],
            flags = data[KnotCtlDataIdx.FLAGS],
            error = data[KnotCtlDataIdx.ERROR],
            section = data[KnotCtlDataIdx.SECTION],
            item = data[KnotCtlDataIdx.ITEM],
            id = data[KnotCtlDataIdx.ID],
            zone = data[KnotCtlDataIdx.ZONE],
            owner = data[KnotCtlDataIdx.OWNER],
            ttl = data[KnotCtlDataIdx.TTL],
            type = data[KnotCtlDataIdx.TYPE],
            data = data[KnotCtlDataIdx.DATA],
            filters = data[KnotCtlDataIdx.FILTERS]
        )

class KnotError(Exception):
    def __init__(self, error_type: KnotErrorType, data: KnotErrorData):
        self.error_type = error_type
        self.data = data

    @classmethod
    def from_raw_error(cls, raw_error: KnotCtlError):
        global error_types_mapping

        error_str_id = raw_error.data[KnotCtlDataIdx.ERROR]
        if error_str_id not in error_types_mapping:
            error_type = KnotErrorType.UNKNOWN
        else:
            error_type = error_types_mapping[error_str_id]

        error_data = KnotErrorData.from_raw_error_data(raw_error.data)
        return KnotError(
            error_type,
            error_data
        )

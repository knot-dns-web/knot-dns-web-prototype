from libknot.control import KnotCtlError, KnotCtlData, KnotCtlDataIdx

from .raw_error_type import KnotErrorType
from .error import KnotError

error_types_mapping = {KnotErrorType[name].value: KnotErrorType[name] for name in KnotErrorType._member_names_}

class KnotErrorData:
    def __init__(
        self,
        command,
        flags,
        error,
        section,
        item,
        id,
        zone,
        owner,
        ttl,
        type,
        data,
        filters
    ):
        self.command = command
        self.flags = flags
        self.error = error
        self.section = section
        self.item = item
        self.id = id
        self.zone = zone
        self.owner = owner
        self.ttl = ttl
        self.type = type
        self.data = data
        self.filters = filters

    @classmethod
    def from_raw_error_data(cls, data: KnotCtlData):
        return KnotErrorData(
            data[KnotCtlDataIdx.COMMAND],
            data[KnotCtlDataIdx.FLAGS],
            data[KnotCtlDataIdx.ERROR],
            data[KnotCtlDataIdx.SECTION],
            data[KnotCtlDataIdx.ITEM],
            data[KnotCtlDataIdx.ID],
            data[KnotCtlDataIdx.ZONE],
            data[KnotCtlDataIdx.OWNER],
            data[KnotCtlDataIdx.TTL],
            data[KnotCtlDataIdx.TYPE],
            data[KnotCtlDataIdx.DATA],
            data[KnotCtlDataIdx.FILTERS]
        )

class KnotBaseError(KnotError):
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
        return KnotBaseError(error_type, error_data)

class KnotError(Exception):
    pass

class InvalidParameter(KnotError):
    pass

class TemplateDoesNotExist(KnotError):
    pass

class ZoneAlreadyExists(KnotError):
    pass

class ZoneDoesNotExist(KnotError):
    pass

import configparser
from pdj.misc import PdjException

class ParameterStoreInterface:
    NO_DEFAULT_VALUE = object()
    def get(self, param: str, default=NO_DEFAULT_VALUE):
        raise PdjException("unimplemented parameter store")

class BasicStore(ParameterStoreInterface):
    def __init__(self, store):
        self.store = store

    def get(self, param: str, default=ParameterStoreInterface.NO_DEFAULT_VALUE):
        if param in self.store:
            return self.store[param]
        if default == ParameterStoreInterface.NO_DEFAULT_VALUE:
            raise PdjException("param [{}] not found".format(param))
        else:
            return default

class DictStore(BasicStore):
    def __init__(self, store: dict):
        self.store = store
    
class SectionProxyStore(BasicStore):
    def __init__(self, store: configparser.SectionProxy):
        self.store = store

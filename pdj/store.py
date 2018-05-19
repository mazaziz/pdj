import configparser
from pdj.misc import PdjException

class AbstractParameterStore:
    NO_DEFAULT_VALUE = object()
    def get(self, name: str, default=NO_DEFAULT_VALUE):
        raise PdjException("unimplemented parameter store method")

class BasicStore(AbstractParameterStore):
    def __init__(self, store):
        self.store = store

    def get(self, name: str, default=AbstractParameterStore.NO_DEFAULT_VALUE):
        if name in self.store:
            return self.store[name]
        if default == AbstractParameterStore.NO_DEFAULT_VALUE:
            raise PdjException("param [{}] not found".format(name))
        else:
            return default

class DictStore(BasicStore):
    def __init__(self, store: dict):
        self.store = store
    
class SectionProxyStore(BasicStore):
    def __init__(self, store: configparser.SectionProxy):
        self.store = store

def load(params):
    if isinstance(params, dict):
        return DictStore(params)
    if isinstance(params, configparser.SectionProxy):
        return SectionProxyStore(params)
    raise PdjException("invalid params type [{}]".format(type(params)))

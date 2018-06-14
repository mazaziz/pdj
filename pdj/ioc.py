import importlib
from pdj.misc import PdjException, parse_import_path
from pdj.params import ParameterStoreInterface

class Container:
    def __init__(self, schema: dict, params: ParameterStoreInterface):
        self.schema = schema
        self.params = params
        self.cache = {}

    def _compose_arg_from_dict(self, argdef: dict):
        try:
            argtype = argdef["type"]
        except KeyError:
            raise PdjException("missing required attribute [type] in arg definition")
        if argtype == "service":
            return self.get(argdef["service"])
        if argtype == "param":
            return self.params.get(argdef["param"], argdef.get("default", ParameterStoreInterface.NO_DEFAULT_VALUE))
        raise PdjException("invalid arg type [{}]".format(argtype))
    
    def _compose_arg_from_string(self, argdef: str):
        if 0 == len(argdef):
            raise PdjException("arg definition string must not be empty")
        op = argdef[0]
        token = argdef[1:]
        if "&" == op:
            if "container" == token:
                return self
            if "schema" == token:
                return self.schema
            if "params" == token:
                return self.params
            raise PdjException("unknown reference [{}] in arg definition".format(argdef))
        if "@" == op:
            return self.get(token)
        if "$" == op:
            return self.params.get(token)
        if "'" == op:
            return token
        raise PdjException("invalid leading character in string argdef [{}]".format(argdef))

    def _compose_arg(self, argdef):
        if isinstance(argdef, (type(None), int, bool, float)):
            return argdef
        if isinstance(argdef, str):
            return self._compose_arg_from_string(argdef)
        if isinstance(argdef, dict):
            return self._compose_arg_from_dict(argdef)
        raise PdjException("invalid arg definition type [{}]".format(type(argdef)))

    def _compose_args(self, argsdef: list):
        if not isinstance(argsdef, list):
            raise PdjException("args must be a list")
        args = []
        kwargs = {}
        for argdef in argsdef:
            if isinstance(argdef, dict) and "name" in argdef:
                kwargs[argdef["name"]] = self._compose_arg(argdef)
            else:
                args.append(self._compose_arg(argdef))
        return args, kwargs

    def _comppose_service(self, name: str, sdef: dict):
        if "class" in sdef:
            module, class_name = parse_import_path(sdef["class"])
            attr = getattr(importlib.import_module(module), class_name)
            args, kwargs = self._compose_args(sdef.get("args", []))
            return attr(*args, **kwargs)
        if "func" in sdef:
            module, func_name = parse_import_path(sdef["func"])
            attr = getattr(importlib.import_module(module), func_name)
            args, kwargs = self._compose_args(sdef.get("args", []))
            return attr(*args, **kwargs)
        raise PdjException("invalid definition for service [{}]".format(name))

    def register(self, service: str, value):
        if service in self.schema:
            raise PdjException("cant register service [{}] since it is already in schema".format(service))
        if service in self.cache:
            raise PdjException("service [{}] was already registered".format(service))
        self.cache[service] = value

    def get(self, service: str):
        if service in self.cache:
            return self.cache[service]
        if service not in self.schema:
            raise PdjException("undefined service [{}]".format(service))
        value = self._comppose_service(service, self.schema[service])
        if self.schema[service].get("cache", True):
            self.cache[service] = value
        return value
    
    def __call__(self, key):
        return self.get(key)

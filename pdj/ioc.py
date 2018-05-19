import os
import json
import importlib
from pdj.misc import PdjException, explode_class_path
from pdj.store import AbstractParameterStore

class Container:
    def __init__(self, config: dict, params: AbstractParameterStore):
        self.config = config
        self.params = params
        self.cache = {}

    def _build_arg_from_dict(self, conf: dict):
        if "type" not in conf:
            raise PdjException("missing required arg attribute: type")
        if "service" == conf["type"]:
            return self.get(conf["service"])
        if "param" == conf["type"]:
            if self.params is None:
                raise PdjException("parameter store is not initialized")
            if "default" in conf:
                return self.params.get(conf["param"], default=conf["default"])
            else:
                return self.params.get(conf["param"])
        raise PdjException("invalid arg type [{}]".format(conf["type"]))
    
    def _build_arg_from_str(self, conf: str):
        if 0 == len(conf):
            raise PdjException("empty string argument is not allowed")
        op = conf[0]
        token = conf[1:]
        if "@" == op:
            return self.get(token)
        if "$" == op:
            return self._build_arg_from_dict({
                "type": "param",
                "param": token
            })
        if "'" == op:
            return token
        raise PdjException("invalid leading character in string argument [{}]".format(conf))

    def _build_arg(self, conf):
        if isinstance(conf, (type(None), int, bool, float)):
            return conf
        if isinstance(conf, str):
            return self._build_arg_from_str(conf)
        if isinstance(conf, dict):
            return self._build_arg_from_dict(conf)
        raise PdjException("invalid arg type [{}]".format(type(conf)))

    def _build_args(self, conf):
        if not isinstance(conf, list):
            raise PdjException("args must be a list")
        args = []
        kwargs = {}
        for arg_conf in conf:
            if isinstance(arg_conf, dict) and "name" in arg_conf:
                kwargs[arg_conf["name"]] = self._build_arg(arg_conf)
            else:
                args.append(self._build_arg(arg_conf))
        return args, kwargs

    def _build_service(self, name: str, conf: dict):
        if "class" in conf:
            module, class_name = explode_class_path(conf["class"])
            attr = getattr(importlib.import_module(module), class_name)
            args, kwargs = self._build_args(conf.get("args", []))
            return attr(*args, **kwargs)
        raise PdjException("invalid configuration for service [{}]".format(name))
    
    def get(self, service: str):
        if service in self.cache:
            return self.cache[service]
        if service not in self.config:
            raise PdjException("undefined service [{}]".format(service))
        value = self._build_service(service, self.config[service])
        if self.config[service].get("cache", True):
            self.cache[service] = value
        return value
    
    def __getitem__(self, key):
        return self.get(key)

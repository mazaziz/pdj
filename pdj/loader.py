import os
import json
import configparser
from pdj.ioc import Container
from pdj.misc import PdjException
import pdj.params

def load_json(path: str):
    with open(path, "r") as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError as e:
            raise PdjException("error while loading json file [{}]".format(path))

def load_schema(path: str) -> dict:
    if not os.path.exists(path):
        raise PdjException("schema path [{}] not found".format(path))
    if os.path.isfile(path):
        return load_json(path)
    if not os.path.isdir(path):
        raise PdjException("schema path must be a regular file or directory [{}]".format(path))
    import glob
    schema = {}
    for jpath in glob.iglob("{}/**/*.json".format(path), recursive=True):
        schema[jpath[1+len(path):-5]] = load_json(jpath)
    return schema

def load_params(obj) -> pdj.params.ParameterStoreInterface:
    if isinstance(obj, pdj.params.ParameterStoreInterface):
        return obj
    if isinstance(obj, dict):
        return pdj.params.DictStore(obj)
    if isinstance(obj, configparser.SectionProxy):
        return pdj.params.SectionProxyStore(obj)
    raise PdjException("invalid params value type [{}]".format(type(obj)))

def load_container(schema, params) -> Container:
    if isinstance(schema, str):
        schema = load_schema(os.path.abspath(schema))
    elif not isinstance(schema, dict):
        raise PdjException("invalid schema type [{}]".format(type(schema)))
    if params is None:
        return Container(schema, pdj.params.DictStore({}))
    return Container(schema, load_params(params))

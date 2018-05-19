import os
import json
import configparser
from pdj.ioc import Container
from pdj.misc import PdjException
from pdj.store import load as load_store

def load_json(path: str):
    with open(path, "r") as fh:
        try:
            return json.load(fh)
        except json.decoder.JSONDecodeError as e:
            raise PdjException("error while loading json file [{}]".format(path))

def load_conf(path: str) -> dict:
    if not os.path.exists(path):
        raise PdjException("config path [{}] not found".format(path))
    if os.path.isfile(path):
        return load_json(path)
    if not os.path.isdir(path):
        raise PdjException("config path must be a regular file or directory [{}]".format(path))
    import glob
    config = {}
    for jpath in glob.iglob("{}/**/*.json".format(path), recursive=True):
        config[jpath[1+len(path):-5]] = load_json(jpath)
    return config

def load_container(config, params=None) -> Container:
    if isinstance(config, str):
        config = load_conf(os.path.abspath(config))
    elif not isinstance(config, dict):
        raise PdjException("invalid config type [{}]".format(type(config)))
    if params is None:
        return Container(config, None)
    return Container(config, load_store(params))

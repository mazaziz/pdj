class PdjException(Exception):
    pass

def parse_import_path(path: str):
    i = path.rfind(".")
    if i == -1:
        return "__main__", path
    else:
        return path[:i], path[i+1:]

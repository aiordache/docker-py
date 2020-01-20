import os
import json
import hashlib

from docker import utils
from docker.constants import IS_WINDOWS_PLATFORM
from docker.constants import DEFAULT_UNIX_SOCKET
from docker.utils.config import find_config_file

CONTEXTS_DIR = os.path.join(os.path.dirname(
    find_config_file() or ""), "contexts")
METADATA_DIR = os.path.join(CONTEXTS_DIR, "meta")
TLS_DIR = os.path.join(CONTEXTS_DIR, "tls")
METAFILE = "meta.json"


def get_current_context_name():
    name = "default"
    docker_cfg_path = find_config_file()
    if docker_cfg_path:
        try:
            cfg = open(docker_cfg_path, "r")
            name = json.load(cfg).get("currentContext")
        except Exception:
            return "default"
    return name


def get_context_id(name):
    return hashlib.sha256(name.encode('utf-8')).hexdigest()


def get_meta_dir(name):
    return os.path.join(METADATA_DIR, get_context_id(name))


def get_meta_file(name):
    return os.path.join(get_meta_dir(name), METAFILE)


def get_tls_dir(name, endpoint=""):
    return os.path.join(TLS_DIR, get_context_id(name), endpoint)


def get_context_host(path=None):
    host = utils.parse_host(path, IS_WINDOWS_PLATFORM)
    if host == DEFAULT_UNIX_SOCKET:
        # remove http+ from default docker socket url
        return host.strip("http+")
    return host

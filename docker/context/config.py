import os, hashlib, base64
from .. import utils

CONTEXTS_DIR = os.path.join(os.path.dirname(utils.find_docker_config_file()), "contexts")
METADATA_DIR = os.path.join(CONTEXTS_DIR, "meta")
TLS_DIR      = os.path.join(CONTEXTS_DIR, "tls")
METAFILE     = "meta.json"

get_context_id = lambda name: hashlib.sha256(name.encode('utf-8')).hexdigest()
get_meta_dir   = lambda name: os.path.join(METADATA_DIR, get_context_id(name))
get_meta_file  = lambda name: os.path.join(get_meta_dir(name), METAFILE)
get_tls_dir    = lambda name, endpoint = "": os.path.join(TLS_DIR, get_context_id(name), endpoint)



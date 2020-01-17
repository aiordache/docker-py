import os, json
from shutil import copyfile, rmtree
from .. import utils
from ..constants import IS_WINDOWS_PLATFORM
from ..types.base import DictType
from ..tls import TLSConfig 
from .config import get_meta_dir, get_meta_file, get_tls_dir


class Context:
    """A context."""
    def __init__(self, name, orchestrator = "swarm", endpoints = None):
        if not name:
            raise Exception("Name not provided")
        self.name = name
        self.orchestrator = orchestrator
        self.endpoints = {
            "docker": {
                "Host": utils.parse_host(None, IS_WINDOWS_PLATFORM),
                "SkipTLSVerify": False 
            }
        } if not endpoints else endpoints
        self.tls_cfg = {}
        self.meta_path = "IN MEMORY"
        self.tls_path = "IN MEMORY"

    def set_endpoint(self, name, host = None, tls_cfg = None, skip_tls_verify = False, def_namespace = None):
        if not name:
            return
        self.endpoints[name] = {
            "Host": utils.parse_host(host, IS_WINDOWS_PLATFORM),
            "SkipTLSVerify": skip_tls_verify
        }
        if def_namespace != None:
            self.endpoints[name]["DefaultNamespace"] = def_namespace
        
        if tls_cfg:
            self.tls_cfg[name] = tls_cfg

    def inspect(self):
        return self.__call__()

    @classmethod
    def load_context(cls, name):
        name, orchestrator, endpoints = Context.load_meta(name)
        if name:
            instance = cls(name, orchestrator, endpoints)
            instance.load_certs()
            instance.meta_path = get_meta_dir(name)
            return instance
        return None
    
    @classmethod
    def load_meta(self, name):
        # load metadata
        metadata = {}
        meta_file = get_meta_file(name)
        if os.path.isfile(meta_file):
            with open(meta_file) as f:
                try:
                    with open(meta_file) as f:
                        metadata = json.load(f)
                    for k, v in metadata["Endpoints"].items():
                        metadata["Endpoints"][k]["SkipTLSVerify"] = bool(v["SkipTLSVerify"])
                except (IOError, KeyError, ValueError) as e:
                    # unknown format
                    raise Exception("Detected corrupted meta file for context {} : {}".format(name, e))

            return metadata["Name"], metadata["Metadata"]["StackOrchestrator"], metadata["Endpoints"]
        return None, None, None
    
    def load_certs(self):
        certs = {}
         # set certs
        tls_dir = get_tls_dir(self.name)
        for endpoint in self.endpoints.keys():
            #get extension
            if not os.path.isdir(os.path.join(tls_dir, endpoint)): continue

            ca_cert = None
            cert = None
            key = None
            for filename in os.listdir(os.path.join(tls_dir, endpoint)):
                if filename.startswith("ca"):
                    ca_cert = os.path.join(tls_dir, endpoint, filename)
                elif filename.startswith("cert"):
                    cert = os.path.join(tls_dir, endpoint, filename)
                elif filename.startswith("key"):
                    key = os.path.join(tls_dir, endpoint, filename)
            if all([ca_cert, cert, key]):
                certs[endpoint] = TLSConfig(client_cert = (cert, key), ca_cert = ca_cert)
        self.tls_cfg = certs
        self.tls_path = get_tls_dir(self.name)



    def save(self):
        # save metadata
        meta_dir = get_meta_dir(self.name)
        if not os.path.isdir(meta_dir):
            os.makedirs(meta_dir)
        with open(get_meta_file(self.name), "w") as f:
            f.write(json.dumps(self.Metadata))
        # save certs
        tls_dir = get_tls_dir(self.name)
        for endpoint, tls in self.tls_cfg.items():
            if not os.path.isdir(os.path.join(tls_dir, endpoint)):
                os.makedirs(os.path.join(tls_dir, endpoint))
        
            #get extension
            ca_file = tls.ca_cert
            if ca_file:
                copyfile(ca_file, os.path.join(tls_dir, endpoint, os.path.basename(ca_file)))
            
            if tls.cert:
                cert_file, key_file = tls.cert
                copyfile(cert_file, os.path.join(tls_dir, endpoint, os.path.basename(cert_file)))
                copyfile(key_file, os.path.join(tls_dir, endpoint, os.path.basename(key_file)))
        
        self.meta_path = get_meta_dir(self.name)
        self.tls_path = get_tls_dir(self.name)

    def cleanup(self):
        if os.path.isdir(self.meta_path):
            rmtree(self.meta_path)
        
        if os.path.isdir(self.tls_path):
            rmtree(self.tls_path)

    def __repr__(self):
        return "<%s: '%s'>" % (self.__class__.__name__, self.name)

    def __str__(self):
        return  json.dumps(self.__call__(), indent=2)

    def __call__(self):
        result = self.Metadata
        result.update(self.TLSMaterial)
        result.update(self.Storage)
        return result

    @property
    def Name(self):
        return self.name
    
    @property
    def Host(self):
        if self.orchestrator == "swarm":
            return self.endpoints["docker"]["Host"]
        return self.endpoints[self.orchestrator]["Host"]

    @property
    def Orchestrator(self):
        return self.orchestrator
    
    @property
    def Metadata(self):
        return {
            "Name": self.name,
            "Metadata": { 
                "StackOrchestrator": self.orchestrator
            },
            "Endpoints": self.endpoints
        }

    @property
    def TLSMaterial(self):
        certs = {}
        for endpoint, tls in self.tls_cfg.items():
            cert, key = tls.cert
            certs[endpoint] = list(map(os.path.basename, [tls.ca_cert, cert, key]))
            
        return {
            "TLSMaterial": certs
        }

    @property
    def Storage(self):
        return {
            "Storage": {
                "MetadataPath": self.meta_path,
                "TLSPath": self.tls_path
            }}

    


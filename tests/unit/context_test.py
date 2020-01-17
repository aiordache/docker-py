import json, os, sys
import unittest
import docker
from docker.context import ContextAPI, Context, config
import six

import pytest

from functools import wraps

def windows(fn):
    @wraps(fn)
    def func(*args, **kwargs): 
        if sys.platform == "win32":
            fn(*args, **kwargs)
    return func

def linux(fn):
    @wraps(fn)
    def func(*args, **kwargs): 
        if sys.platform != "win32":
            fn(*args, **kwargs)
    return func

class BaseContextTest(unittest.TestCase):
    @linux
    def test_url_compatibility_on_linux(self):
        c = Context("test")
        assert c.Host == "unix:///var/run/docker.sock"

    @windows
    def test_url_compatibility_on_windows(self):
        c = Context("test")
        assert c.Host == "npipe:////./pipe/docker_engine"

    def test_fail_on_default_context_create(self):
        failed = False
        try:
            ContextAPI.create_context("default")
        except docker.errors.ContextException as err:
            assert '"default" is a reserved context name' in err.msg
            failed = True

        assert failed is True

    def test_default_in_context_list(self):
        found = False
        ctx = ContextAPI.contexts()
        for c in ctx:
            if c.Name == "default":
                found = True
        assert found is True
    
    def test_context_inspect_without_params(self):
        ctx = ContextAPI.inspect_context()
        assert ctx["Name"] == "default"
        assert ctx["Metadata"]["StackOrchestrator"] == "swarm"
        assert ctx["Endpoints"]["docker"]["Host"] in ["unix:///var/run/docker.sock", "npipe:////./pipe/docker_engine"]

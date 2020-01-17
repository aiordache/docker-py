
import os, sys, json, tempfile
import pytest

import docker
from docker import errors
from docker.context import ContextAPI
from docker.tls import TLSConfig
from .base import BaseAPIIntegrationTest


class ContextLifecycleTest(BaseAPIIntegrationTest):
    def test_lifecycle(self):
        # check there is no context 'test'
        ctx = ContextAPI.get_context("test")
        assert ctx is None

        success = False
        ca = tempfile.NamedTemporaryFile(prefix="/tmp/certs/ca.pem", mode = "r")
        cert = tempfile.NamedTemporaryFile(prefix="/tmp/certs/cert.pem", mode = "r")
        key = tempfile.NamedTemporaryFile(prefix="/tmp/certs/key.pem", mode = "r")
        # create context 'test
        docker_tls = TLSConfig(client_cert = ("/tmp/certs/cert.pem", "/tmp/certs/key.pem"),ca_cert = "/tmp/certs/ca.pem")
        ContextAPI.create_context("test", host = "/var/usr...", tls_cfg=docker_tls)

        ca.close()
        cert.close()
        key.close()
        #check for a context 'test' in the context store
        contexts = ContextAPI.contexts()
        for ctx in contexts:
            if ctx.Name == "test":
                success = True

        assert success is True
        # retrieve a context object for 'test' 
        ctx = ContextAPI.get_context("test")
        assert ctx is not None
        # remove context
        remove = False
        ContextAPI.remove_context("test")
        try:
            ctx = ContextAPI.inspect_context("test")
        except errors.ContextNotFound:
            remove = True
        assert remove is True
        # check there is no 'test' context in store
        ctx = ContextAPI.get_context("test")
        assert ctx is None
        

    def test_context_remove(self):
        success = False
        ContextAPI.create_context("test")
        inspect = ContextAPI.inspect_context("test")
        if inspect["Name"] == "test":
            success = True
        assert success is True

        removed = False
        ContextAPI.remove_context("test")
        try:
            ctx = ContextAPI.inspect_context("test")
        except errors.ContextNotFound:
            removed = True
        assert removed is True
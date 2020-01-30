import json

from docker import APIClient
from docker import ContextAPI
from docker import TLSConfig

def test_get_current_context():
    ctx = ContextAPI.get_current_context()

    print(json.dumps(ctx.inspect(), indent = 2))

    # get list with running containers data
    client = APIClient(base_url=ctx.Host, tls=ctx.TLSConfig)
    containers = client.containers()
    print("Running container IDs:")
    for c in containers:
        print("\t{}".format(c['Id']))


def test_create_docker_context():
    tls = TLSConfig(
        client_cert=("/tmp/certs/cert.pem", "/tmp/certs/key.pem"), 
        ca_cert="/tmp/certs/ca.pem",
    )
    ctx = ContextAPI.create_context("test", tls_cfg=tls)
    print(json.dumps(ctx.inspect(), indent = 2))

def test_remove_docker_context():
    ContextAPI.remove_context("test")


def test_get_docker_context():
    ctx = ContextAPI.get_context("kind")
    print(json.dumps(ctx.inspect(), indent = 2))


def test_inspect_docker_context():
    inspect = ContextAPI.inspect_context("dind")
    print(json.dumps(inspect, indent = 2))


if __name__ == "__main__":
    test_get_current_context()
    test_create_docker_context()
    test_remove_docker_context()
    test_get_docker_context()
    test_inspect_docker_context()




import os, json
from .. import errors
from .config import METADATA_DIR, METAFILE
from .context import Context

class ContextAPI(object):
    """Context API.
    Contains methods for context management: create, list, remove, get, inspect.
    """
    DEFAULT_CONTEXT = Context("default")

    @classmethod
    def create_context(cls, name, orchestrator = "swarm", endpoint = None, host = None, tls_cfg = None, default_namespace = None, skip_tls_verify = False):
        """Creates a new context. 
        Returns:
            (Context): a Context object.
        Raises:
            :py:class:`docker.errors.MissingContextParameter`
                If a context name is not provided.
            :py:class:`docker.errors.ContextAlreadyExists`
                If a context with the name already exists.
            :py:class:`docker.errors.ContextException`
                If name is default.

        Example:

        >>> import docker
        >>> ctx = docker.ContextAPI.create_context(name='test')
        >>> print(ctx)
        {
            "Name": "test",
            "Metadata": {
                "StackOrchestrator": "swarm"
            },
            "Endpoints": {
                "docker": {
                    "Host": "unix:///var/run/docker.sock",
                    "SkipTLSVerify": false
                }
            },
            "TLSMaterial": {},
            "Storage": {
                "MetadataPath": "IN MEMORY",
                "TLSPath": "IN MEMORY"
            }
        }
        """
        if not name:
            raise errors.MissingContextParameter("name")
        if name == "default":
            raise errors.ContextException('"default" is a reserved context name')
        # load the context to check if it already exists
        ctx = Context.load_context(name)
        if ctx:
            raise errors.ContextAlreadyExists(name)

        ctx = Context(name, orchestrator)
        if endpoint:
            ctx.set_endpoint(endpoint, host, tls_cfg, skip_tls_verify = skip_tls_verify, def_namespace=default_namespace)
        ctx.save()
        return ctx

    @classmethod
    def contexts(self):
        """Context list.
        Returns:
            (Context): List of context objects.
        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        #load from local disk
        names = []
        for dirname, dirnames, fnames in os.walk(METADATA_DIR):
            for filename in fnames + dirnames:
                if filename == METAFILE:
                    try:
                        data = json.load(open(os.path.join(dirname, filename), "r"))
                        names.append(data["Name"])
                    except:
                         raise errors.ContextException("Failed to load metafile {}".format(filename))
        
        contexts = [ContextAPI.DEFAULT_CONTEXT]
        for name in names:
             contexts.append(Context.load_context(name))
        return contexts

    

    @classmethod
    def remove_context(cls, name):
        """Remove a context. Similar to the ``docker context rm`` command.

        Args:
            name (str): The name of the context

        Raises:
            :py:class:`docker.errors.MissingContextParameter`
                If a context name is not provided.
            :py:class:`docker.errors.ContextNotFound`
                If a context with the name does not exist.
            :py:class:`docker.errors.ContextException`
                If name is default.

        Example:

        >>> import docker
        >>> docker.ContextAPI.remove_context(name='test')
        >>> 
        """
        if not name:
            raise errors.MissingContextParameter("name")
        if name == "default": raise errors.ContextException('context "default" cannot be removed')
        # load the context to check if it already exists
        ctx = Context.load_context(name)
        if not ctx:
            raise errors.ContextNotFound(name)

        ctx.cleanup()
        
    @classmethod
    def get_context(cls, name = "default"):
        """Retrieves a context object.
        Args:
            name (str): The name of the context

        Raises:
            :py:class:`docker.errors.MissingContextParameter`
                If a context name is not provided.

        Example:

        >>> import docker
        >>> ctx = docker.ContextAPI.get_context(name='test')
        >>> print(ctx)
        {
            "Name": "test",
            "Metadata": {
                "StackOrchestrator": "swarm"
            },
            "Endpoints": {
                "docker": {
                "Host": "unix:///var/run/docker.sock",
                "SkipTLSVerify": false
                }
            },
            "TLSMaterial": {},
            "Storage": {
                "MetadataPath": "/home/user/.docker/contexts/meta/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                "TLSPath": "/home/user/.docker/contexts/tls/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08/"
            }
        }
        """
        if not name:
            raise errors.MissingContextParameter("name")
        if name == "default": return ContextAPI.DEFAULT_CONTEXT
        # load the context to check if it already exists
        ctx = Context.load_context(name)
        return ctx
        
    @classmethod
    def inspect_context(cls, name = "default"):
        """Remove a context. Similar to the ``docker context inspect`` command.

        Args:
            name (str): The name of the context

        Raises:
            :py:class:`docker.errors.MissingContextParameter`
                If a context name is not provided.
            :py:class:`docker.errors.ContextNotFound`
                If a context with the name does not exist.

        Example:

        >>> import docker
        >>> docker.ContextAPI.remove_context(name='test')
        >>>
        """
        if not name:
            raise errors.MissingContextParameter("name")
        if name == "default": return ContextAPI.DEFAULT_CONTEXT()
        # load the context to check if it already exists
        ctx = Context.load_context(name)
        if not ctx:
            raise errors.ContextNotFound(name)

        return ctx()
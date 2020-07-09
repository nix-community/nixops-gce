import os.path
import nixops.plugins
from nixops.plugins import Plugin


class NixopsGCPPlugin(Plugin):
    @staticmethod
    def nixexprs():
        return [os.path.dirname(os.path.abspath(__file__)) + "/nix"]

    @staticmethod
    def load():
        return [
            "nixops_gcp.resources",
            "nixops_gcp.backends.gce",
        ]


@nixops.plugins.hookimpl
def plugin():
    return NixopsGCPPlugin()

from typing import Sequence
from nixops.resources import ResourceOptions
from typing import Union
from typing import Optional


class GceRouteOptions(ResourceOptions):
    accessKey: str
    description: Optional[str]
    destination: Optional[str]
    name: str
    network: str
    nextHop: Optional[str]
    priority: int
    project: str
    serviceAccount: str
    tags: Optional[Sequence[str]]

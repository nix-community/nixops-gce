from typing import Union
from nixops.resources import ResourceOptions
from typing import Optional


class GceHttpHealthCheckOptions(ResourceOptions):
    accessKey: str
    checkInterval: int
    description: Optional[str]
    healthyThreshold: int
    host: Optional[str]
    name: str
    path: str
    port: int
    project: str
    serviceAccount: str
    timeout: int
    unhealthyThreshold: int

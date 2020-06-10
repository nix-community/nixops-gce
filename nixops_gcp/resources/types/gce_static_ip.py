from typing import Optional
from typing import Union
from nixops.resources import ResourceOptions


class GceStaticIpOptions(ResourceOptions):
    accessKey: str
    ipAddress: Optional[str]
    name: str
    project: str
    publicIPv4: Optional[str]
    region: str
    serviceAccount: str

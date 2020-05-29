from nixops.resources import ResourceOptions
from typing import Union
from typing import Optional


class GceForwardingRuleOptions(ResourceOptions):
    accessKey: str
    description: Optional[str]
    ipAddress: Optional[str]
    name: str
    portRange: Optional[str]
    project: str
    protocol: str
    publicIPv4: Optional[str]
    region: str
    serviceAccount: str
    targetPool: str

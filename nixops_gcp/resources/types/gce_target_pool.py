from typing import Union
from nixops.resources import ResourceOptions
from typing import Optional
from typing import Sequence


class GceTargetPoolOptions(ResourceOptions):
    accessKey: str
    healthCheck: Optional[str]
    machines: Sequence[str]
    name: str
    project: str
    region: str
    serviceAccount: str

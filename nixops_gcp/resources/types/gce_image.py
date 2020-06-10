from nixops.resources import ResourceOptions
from typing import Optional
from typing import Union


class GceImageOptions(ResourceOptions):
    accessKey: str
    description: Optional[str]
    name: str
    project: str
    serviceAccount: str
    sourceUri: str

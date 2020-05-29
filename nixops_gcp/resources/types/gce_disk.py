from typing import Optional
from typing import Union
from nixops.resources import ResourceOptions


class GceDiskOptions(ResourceOptions):
    accessKey: str
    diskType: str
    image: Optional[str]
    name: str
    project: str
    publicImageProject: Optional[str]
    region: str
    serviceAccount: str
    size: Optional[int]
    snapshot: Optional[str]

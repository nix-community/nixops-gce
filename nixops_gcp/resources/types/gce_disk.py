from typing import Optional
from nixops.resources import ResourceOptions

from nixops_gcp.backends.options import ImageOptions


class GceDiskOptions(ResourceOptions):
    accessKey: str
    diskType: str
    image: ImageOptions
    name: str
    project: str
    region: str
    serviceAccount: str
    size: Optional[int]
    snapshot: Optional[str]

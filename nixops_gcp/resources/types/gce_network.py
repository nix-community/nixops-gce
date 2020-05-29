from typing import Sequence
from nixops.resources import ResourceOptions
from typing import Mapping
from typing import Optional
from typing import Union


class FirewallOptions(ResourceOptions):
    allowed: Mapping[str, Optional[Sequence[Union[int, str]]]]
    sourceRanges: Optional[Sequence[str]]
    sourceTags: Sequence[str]
    targetTags: Sequence[str]


class GceNetworkOptions(ResourceOptions):
    accessKey: str
    addressRange: str
    firewall: Mapping[str, FirewallOptions]
    name: str
    project: str
    serviceAccount: str

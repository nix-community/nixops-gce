from nixops.resources import ResourceOptions
from typing_extensions import Literal
from typing import Sequence
from typing import Optional
from typing import Union
from typing import Mapping


class GCEDiskOptions(ResourceOptions):
    disk_name: Optional[str]
    disk: Optional[str]
    snapshot: Optional[str]
    image: Optional[str]
    publicImageProject: Optional[str]
    size: Optional[int]
    diskType: Union[Literal["standard"], Literal["ssd"]]
    readOnly: bool
    bootDisk: bool
    deleteOnTermination: bool
    encrypt: bool
    cipher: str
    keySize: int
    passphrase: str


class FilesystemsOptions(GCEDiskOptions):
    gce: GCEDiskOptions


class SchedulingOptions(ResourceOptions):
    automaticRestart: bool
    onHostMaintenance: str
    preemptible: bool


class InstanceserviceAccountOptions(ResourceOptions):
    email: str
    scopes: Sequence[str]


class GceOptions(ResourceOptions):
    accessKey: str
    blockDeviceMapping: Mapping[str, GCEDiskOptions]
    bootstrapImage: str
    canIpForward: bool
    instanceServiceAccount: InstanceserviceAccountOptions
    instanceType: str
    ipAddress: Optional[str]
    labels: Mapping[str, str]
    machineName: str
    metadata: Mapping[str, str]
    network: Optional[str]
    project: str
    region: str
    rootDiskSize: Optional[int]
    rootDiskType: str
    scheduling: SchedulingOptions
    serviceAccount: str
    subnet: Optional[str]
    tags: Sequence[str]
    fileSystems: Mapping[str, FilesystemsOptions]

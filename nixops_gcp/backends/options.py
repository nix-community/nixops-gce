from nixops.resources import (
    ResourceOptions,
    ResourceEval,
)
from typing_extensions import Literal
from typing import (
    Sequence,
    Optional,
    Union,
    Mapping,
)


class ImageOptions(ResourceOptions):
    name: Optional[Union[str, ResourceEval]]
    family: Optional[str]
    project: Optional[str]


class GCEDiskOptions(ResourceOptions):
    disk_name: Optional[str]
    disk: Optional[str]
    snapshot: Optional[str]
    image: ImageOptions
    size: Optional[int]
    diskType: Literal["standard", "ssd"]
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
    bootstrapImage: ImageOptions
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
    fileSystems: Optional[Mapping[str, FilesystemsOptions]]

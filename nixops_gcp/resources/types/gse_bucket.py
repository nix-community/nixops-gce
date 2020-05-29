from nixops.resources import ResourceOptions
from typing import Union
from typing import Sequence
from typing import Optional


class WebsiteOptions(ResourceOptions):
    mainPageSuffix: Optional[str]
    notFoundPage: Optional[str]


class VersioningOptions(ResourceOptions):
    enabled: bool


class LoggingOptions(ResourceOptions):
    logBucket: Optional[str]
    logObjectPrefix: Optional[str]


class ConditionsOptions(ResourceOptions):
    age: Optional[int]
    createdBefore: Optional[str]
    isLive: Optional[bool]
    numberOfNewerVersions: Optional[int]


class LifecycleOptions(ResourceOptions):
    action: str
    conditions: ConditionsOptions


class CorsOptions(ResourceOptions):
    maxAgeSeconds: Optional[int]
    methods: Sequence[str]
    origins: Sequence[str]
    responseHeaders: Sequence[str]


class GseBucketOptions(ResourceOptions):
    accessKey: str
    cors: Sequence[CorsOptions]
    lifecycle: Sequence[LifecycleOptions]
    location: str
    logging: LoggingOptions
    name: str
    project: str
    serviceAccount: str
    storageClass: str
    versioning: VersioningOptions
    website: WebsiteOptions

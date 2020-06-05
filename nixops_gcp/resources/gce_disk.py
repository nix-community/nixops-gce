# -*- coding: utf-8 -*-

# Automatic provisioning of GCE Persistent Disks.

import os
import libcloud.common.google
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from nixops.util import attr_property
from nixops_gcp.gcp_common import (
    ResourceDefinition,
    ResourceState,
    optional_string,
    optional_int,
)
from nixops_gcp.resources.gce_image import GCEImageState
from .types.gce_disk import GceDiskOptions


class GCEDiskDefinition(ResourceDefinition):
    """Definition of a GCE Persistent Disk"""

    config: GceDiskOptions

    @classmethod
    def get_type(cls):
        return "gce-disk"

    @classmethod
    def get_resource_type(cls):
        return "gceDisks"

    def __init__(self, name, config):
        super().__init__(name, config)
        self.disk_name = self.config.name
        self.region = self.config.region
        self.size = self.config.size
        self.snapshot = self.config.snapshot
        self.image = self.config.image
        self.public_image_project = self.config.publicImageProject
        self.disk_type = self.config.diskType

    def show_type(self):
        return "{0} [{1}]".format(self.get_type(), self.region)


class GCEDiskState(ResourceState):
    """State of a GCE Persistent Disk"""

    region = attr_property("gce.region", None)
    size = attr_property("gce.size", None, int)
    disk_name = attr_property("gce.disk_name", None)
    disk_type = attr_property("gce.diskType", None)

    @classmethod
    def get_type(cls):
        return "gce-disk"

    def __init__(self, depl, name, id):
        ResourceState.__init__(self, depl, name, id)

    def show_type(self):
        s = super().show_type()
        if self.state == self.UP:
            s = "{0} [{1}; {2} GiB]".format(s, self.region, self.size)
        return s

    @property
    def resource_id(self):
        return self.disk_name

    nix_name = "gceDisks"

    @property
    def full_name(self):
        return "GCE disk '{0}'".format(self.disk_name)

    def disk(self):
        return self.connect().ex_get_volume(self.disk_name, self.region)

    def create(self, defn, check, allow_reboot, allow_recreate):
        self.no_change(defn.size and self.size != defn.size, "size")
        self.no_property_change(defn, "disk_type")
        self.no_project_change(defn)
        self.no_region_change(defn)

        self.copy_credentials(defn)
        self.disk_name = defn.disk_name

        if check:
            try:
                disk = self.disk()
                if self.state == self.UP:
                    self.handle_changed_property(
                        "region", disk.extra["zone"].name, can_fix=False
                    )
                    self.handle_changed_property(
                        "disk_type", disk.extra["type"][3:], can_fix=False
                    )
                    self.handle_changed_property("size", int(disk.size), can_fix=False)
                else:
                    self.warn_not_supposed_to_exist(valuable_data=True)
                    self.confirm_destroy(disk, self.full_name)

            except libcloud.common.google.ResourceNotFoundError:
                self.warn_missing_resource()

        if self.state != self.UP:
            extra_msg = (
                " from snapshot '{0}'".format(defn.snapshot)
                if defn.snapshot
                else " from image '{0}'".format(defn.image)
                if defn.image
                else " marked as public. "
                if defn.public_image_project
                else ""
            )
            self.log(
                "creating GCE disk of {0} GiB{1}...".format(
                    defn.size if defn.size else "auto", extra_msg
                )
            )

            # Retrieve GCENodeImage based on family name and project
            if defn.public_image_project:
                try:
                    img = self.connect().ex_get_image_from_family(
                        image_family=defn.image,
                        ex_project_list=[defn.public_image_project],
                        ex_standard_projects=False,
                    )
                except libcloud.common.google.ResourceNotFoundError:
                    raise Exception(
                        "Image family {0} not found in project {1}".format(
                            defn.image, defn.public_image_project
                        )
                    )
                except libcloud.common.google.GoogleBaseError as ex:
                    if ex.value["reason"] == "forbidden":
                        raise Exception(
                            "Image from image family {0} has not been set to public in project {1}".format(
                                defn.image, defn.public_image_project
                            )
                        )
                    else:
                        raise Exception(ex.value["message"])
            else:
                img = defn.image

            try:
                volume = self.connect().create_volume(
                    size=defn.size,
                    name=defn.disk_name,
                    location=defn.region,
                    snapshot=defn.snapshot,
                    image=img,
                    use_existing=False,
                    ex_disk_type="pd-" + defn.disk_type,
                    ex_image_family=None,
                )
            except libcloud.common.google.ResourceExistsError:
                raise Exception(
                    "tried creating a disk that already exists; "
                    "please run 'deploy --check' to fix this"
                )
            self.state = self.UP
            self.region = defn.region
            self.size = volume.size
            self.disk_type = defn.disk_type

    def destroy(self, wipe=False):
        if self.state == self.UP:
            try:
                return self.confirm_destroy(self.disk(), self.full_name, abort=False)
            except libcloud.common.google.ResourceNotFoundError:
                self.warn(
                    "tried to destroy {0} which didn't exist".format(self.full_name)
                )
        return True

    def create_after(self, resources, defn):
        return {r for r in resources if isinstance(r, GCEImageState)}

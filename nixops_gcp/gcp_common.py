# -*- coding: utf-8 -*-

import os
import re

from nixops.util import attr_property
import nixops.resources

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.common.google import (
    ResourceNotFoundError,
    GoogleBaseError,
)


def optional_string(elem):
    return elem.get("value") if elem is not None else None


def optional_int(elem):
    return int(elem.get("value")) if elem is not None else None


def optional_bool(elem):
    return elem.get("value") == "true" if elem is not None else None


def ensure_not_empty(value, name):
    if not value:
        raise Exception("{0} must not be empty".format(name))


def ensure_positive(value, name):
    if value <= 0:
        raise Exception("{0} must be a positive integer".format(name))


def retrieve_gce_image(_conn, img):
    """
    Retrieve GCENodeImage based on family or name of the image
    Takes object as imageOptions submodule : {'project', 'name', 'family'}
    Returns the image object to be used for disks creation
    """
    if img.name or img.family:
        # libcloud expects project to be empty list or a list of projects
        if not img.project:
            project = None
        else:
            project = [img.project]
        if img.family:
            """ Retrieve the latest image from the specified image family
            Optionally from a different project """
            try:
                image = _conn.ex_get_image_from_family(
                    image_family=img.family,
                    ex_project_list=project,
                    ex_standard_projects=False,
                )
            except ResourceNotFoundError:
                raise Exception("Image family '{0}' was not found..".format(img.family))
            except GoogleBaseError as ex:
                if ex.value["reason"] == "forbidden":
                    raise Exception(
                        "Image family '{0}' has not been made public in project '{1}'".format(
                            img.family, img.project
                        )
                    )
                if ex.value["reason"] == "accessNotConfigured":
                    raise Exception(
                        "Project '{0}' does not exist or the Compute Engine API is disabled".format(
                            img.project
                        )
                    )
                raise Exception(ex.value["message"])
        else:
            """ Retrieve the image object using the name, partial name
            or full path of a GCE image,
            Optionally from a different project
            """
            try:
                """
                For image name, we need to specify the full image path because we cannot list images in a different project
                Ref : https://cloud.google.com/compute/docs/images/managing-access-custom-images#share-images-publicly
                Example :
                https://www.googleapis.com/compute/v1/projects/project-operations/global/images/nixos-18091228a4c4cbb613c-x86-64-linux
                """
                image_full_path = img.name
                if project:
                    image_full_path = "https://www.googleapis.com/compute/v1/projects/{prj}/global/images/{img}".format(
                        prj=img.project, img=img.name
                    )
                image = _conn.ex_get_image(
                    partial_name=image_full_path,
                    ex_project_list=project,
                    ex_standard_projects=False,
                )
            except ResourceNotFoundError:
                raise Exception("Image '{0}' was not found..".format(img.name))
            except GoogleBaseError as ex:
                if ex.value["reason"] == "forbidden":
                    raise Exception(
                        "Image '{0}' has not been made public in project '{1}'".format(
                            img.name, img.project
                        )
                    )
                if ex.value["reason"] == "accessNotConfigured":
                    raise Exception(
                        "Project '{0}' does not exist or the Compute Engine API is disabled".format(
                            img.project
                        )
                    )
                raise Exception(ex.value["message"])
        return image
    if img.project:
        raise Exception(
            "Specify image name or image family alongside the project '{0}'..".format(
                img.project
            )
        )


class ResourceDefinition(nixops.resources.ResourceDefinition):
    def __init__(self, name, config):
        super().__init__(name, config)

        res_name: str
        if hasattr(self.config, "gce") and hasattr(self.config.gce, "machineName"):
            res_name = self.config.gce.machineName
        else:
            res_name = self.config.name

        if (
            len(res_name) > 63
            or re.match("[a-z]([-a-z0-9]{0,61}[a-z0-9])?$", res_name) is None
        ):
            raise Exception(
                "resource name ‘{0}‘ must be 1-63 characters long and "
                "match the regular expression [a-z]([-a-z0-9]*[a-z0-9])? which "
                "means the first character must be a lowercase letter, and all "
                "following characters must be a dash, lowercase letter, or digit, "
                "except the last character, which cannot be a dash. You may set a different name using the resource 'name' option.".format(res_name)
            )

        if hasattr(self.config, "gce") and hasattr(self.config.gce, "project"):
            self.project = self.config.gce.project
        else:
            self.project = self.config.project
        if hasattr(self.config, "gce") and hasattr(self.config.gce, "serviceAccount"):
            self.service_account = self.config.gce.serviceAccount
        else:
            self.service_account = self.config.serviceAccount
        if hasattr(self.config, "gce") and hasattr(self.config.gce, "accessKey"):
            self.access_key_path = self.config.gce.accessKey
        else:
            self.access_key_path = self.config.accessKey


class ResourceState(nixops.resources.ResourceState):

    project = attr_property("gce.project", None)
    service_account = attr_property("gce.serviceAccount", None)
    access_key_path = attr_property("gce.accessKey", None)

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn = None

    def connect(self):
        if not self._conn:
            self._conn = get_driver(Provider.GCE)(
                self.service_account, self.access_key_path, project=self.project
            )
        return self._conn

    @property
    def credentials_prefix(self):
        return "resources.{0}.$NAME".format(self.nix_name)

    def defn_project(self, defn):
        project = defn.project or os.environ.get("GCE_PROJECT")
        if not project:
            raise Exception(
                "please set '{0}.project' or $GCE_PROJECT".format(
                    self.credentials_prefix
                )
            )
        return project

    def defn_service_account(self, defn):
        service_account = defn.service_account or os.environ.get("GCE_SERVICE_ACCOUNT")
        if not service_account:
            raise Exception(
                "please set '{0}.serviceAccount' or $GCE_SERVICE_ACCOUNT".format(
                    self.credentials_prefix
                )
            )
        return service_account

    def defn_access_key_path(self, defn):
        access_key_path = defn.access_key_path or os.environ.get("ACCESS_KEY_PATH")
        if not access_key_path:
            raise Exception(
                "please set '{0}.accessKey' or $ACCESS_KEY_PATH".format(
                    self.credentials_prefix
                )
            )
        return access_key_path

    def copy_credentials(self, defn):
        self.project = self.defn_project(defn)
        self.service_account = self.defn_service_account(defn)
        self.access_key_path = self.defn_access_key_path(defn)

    def is_deployed(self):
        return self.state == self.UP

    def no_change(self, condition, property_name):
        if self.is_deployed() and condition:
            raise Exception(
                "cannot change the {0} of a deployed {1}".format(
                    property_name, self.full_name
                )
            )

    def no_property_change(self, defn, name):
        self.no_change(
            getattr(self, name) != getattr(defn, name), name.replace("_", " ")
        )

    def no_project_change(self, defn):
        self.no_change(self.project != self.defn_project(defn), "project")

    def no_region_change(self, defn):
        self.no_change(self.region != defn.region, "region")

    def warn_missing_resource(self):
        if self.state == self.UP:
            self.warn(
                "{0} is supposed to exist, but is missing; recreating...".format(
                    self.full_name
                )
            )
            self.state = self.MISSING

    def confirm_destroy(self, resource, res_name, abort=True):
        if self.depl.logger.confirm(
            "are you sure you want to destroy {0}?".format(res_name)
        ):
            self.log("destroying...")
            resource.destroy()
            return True
        else:
            if abort:
                raise Exception("can't proceed further")
            else:
                return False

    def warn_if_changed(
        self, expected_state, actual_state, name, resource_name=None, can_fix=True
    ):
        if expected_state != actual_state:
            self.warn(
                "{0} {1} has changed to '{2}'; expected it to be '{3}'{4}".format(
                    resource_name or self.full_name,
                    name,
                    actual_state,
                    expected_state,
                    "" if can_fix else "; cannot fix this automatically",
                )
            )
        return actual_state

    # use warn_if_changed for a very typical use case of dealing
    # with changed properties which are stored in attributes
    # with user-friendly names
    def handle_changed_property(
        self, name, actual_state, property_name=None, can_fix=True
    ):
        self.warn_if_changed(
            getattr(self, name),
            actual_state,
            property_name or name.replace("_", " "),
            can_fix=can_fix,
        )
        if can_fix:
            setattr(self, name, actual_state)

    def warn_not_supposed_to_exist(
        self, resource_name=None, valuable_data=False, valuable_resource=False
    ):
        valuables = " or ".join(
            [
                d
                for d in [valuable_data and "data", valuable_resource and "resource"]
                if d
            ]
        )
        valuable_msg = (
            "; however, this also could be a resource name collision, "
            "and valuable {0} could be lost; before proceeding, "
            "please ensure that this isn't so".format(valuables)
            if valuables
            else ""
        )
        self.warn(
            "{0} exists, but isn't supposed to; probably, this is the result "
            "of a botched creation attempt and can be fixed by deletion{1}".format(
                resource_name or self.full_name, valuable_msg
            )
        )

    # API to handle copying properties from definition to state
    # after resource is created or updated and checking that
    # the state is out of sync with the definition
    def copy_properties(self, defn):
        for attr in self.defn_properties:
            setattr(self, attr, getattr(defn, attr))

    def properties_changed(self, defn):
        return any(
            getattr(self, attr) != getattr(defn, attr) for attr in self.defn_properties
        )

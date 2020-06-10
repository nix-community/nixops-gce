# -*- coding: utf-8 -*-

# Automatic provisioning of GCE Networks.

import os
import libcloud.common.google
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from nixops.util import attr_property
from nixops_gcp.gcp_common import ResourceDefinition, ResourceState
from .types.gce_network import GceNetworkOptions, FirewallOptions


def normalize_list(tags):
    return sorted(tags or [])


class GCENetworkDefinition(ResourceDefinition):
    """Definition of a GCE Network"""

    config: GceNetworkOptions

    @classmethod
    def get_type(cls):
        return "gce-network"

    @classmethod
    def get_resource_type(cls):
        return "gceNetworks"

    def __init__(self, name, config):
        super().__init__(name, config)

        self.network_name = self.config.name
        self.address_range = self.config.addressRange

        def parse_allowed(x):
            if x is None:
                return []
            else:
                return [str(v) for v in x]

        def parse_fw(x_name: str, x: FirewallOptions):
            result = dict(x)
            result["sourceRanges"] = list(x.sourceRanges or []) or ["0.0.0.0/0"]
            result["allowed"] = {
                name: parse_allowed(a) for name, a in x.allowed.items()
            }

            if len(result["allowed"]) == 0:
                raise Exception(
                    "Firewall rule '{0}' in network '{1}' "
                    "must provide at least one protocol/port specification".format(
                        x_name, self.network_name
                    )
                )
            if len(result["sourceRanges"]) == 0 and len(result["sourceTags"]) == 0:
                raise Exception(
                    "Firewall rule '{0}' in network '{1}' "
                    "must specify at least one source range or tag".format(
                        x_name, self.network_name
                    )
                )
            return result

        self.firewall = {k: parse_fw(k, v) for k, v in self.config.firewall.items()}

    def show_type(self):
        return "{0} [{1}]".format(self.get_type(), self.address_range)


class GCENetworkState(ResourceState):
    """State of a GCE Network"""

    address_range = attr_property("gce.addressRange", None)
    network_name = attr_property("gce.network_name", None)

    firewall = attr_property("gce.firewall", {}, "json")

    @classmethod
    def get_type(cls):
        return "gce-network"

    def __init__(self, depl, name, id):
        ResourceState.__init__(self, depl, name, id)

    def show_type(self):
        s = super(GCENetworkState, self).show_type()
        if self.state == self.UP:
            s = "{0} [{1}]".format(s, self.address_range)
        return s

    @property
    def resource_id(self):
        return self.network_name

    nix_name = "gceNetworks"

    @property
    def full_name(self):
        return "GCE network '{0}'".format(self.network_name)

    def network(self):
        return self.connect().ex_get_network(self.network_name)

    def update_firewall(self, k, v):
        x = self.firewall
        if v == None:
            x.pop(k, None)
        else:
            x[k] = v
        self.firewall = x

    def firewall_name(self, name):
        return "{0}-{1}".format(self.network_name, name)

    def full_firewall_name(self, name):
        return "GCE firewall '{0}'".format(self.firewall_name(name))

    def warn_if_firewall_changed(
        self, fw_name, expected_state, actual_state, name, can_fix=True
    ):
        return self.warn_if_changed(
            expected_state,
            actual_state,
            name,
            resource_name=self.full_firewall_name(fw_name),
            can_fix=can_fix,
        )

    def destroy_firewall(self, fwname):
        self.log("destroying {0}...".format(self.full_firewall_name(fwname)))
        try:
            fw_n = self.firewall_name(fwname)
            self.connect().ex_get_firewall(fw_n).destroy()
        except libcloud.common.google.ResourceNotFoundError:
            self.warn(
                "tried to destroy {0} which didn't exist".format(
                    self.full_firewall_name(fwname)
                )
            )
        self.update_firewall(fwname, None)

    def create(self, defn, check, allow_reboot, allow_recreate):
        self.no_property_change(defn, "address_range")
        self.no_project_change(defn)

        self.copy_credentials(defn)
        self.network_name = defn.network_name

        if check:
            try:
                network = self.network()
                if self.state == self.UP:
                    self.handle_changed_property(
                        "address_range", network.cidr, can_fix=False
                    )
                else:
                    self.warn_not_supposed_to_exist()
                    self.confirm_destroy(network, self.full_name)

            except libcloud.common.google.ResourceNotFoundError:
                self.warn_missing_resource()

        if self.state != self.UP:
            self.log("creating {0}...".format(self.full_name))
            try:
                network = self.connect().ex_create_network(
                    defn.network_name, defn.address_range
                )
            except libcloud.common.google.ResourceExistsError:
                raise Exception(
                    "tried creating a network that already exists; "
                    "please run 'deploy --check' to fix this"
                )
            self.state = self.UP
            self.address_range = defn.address_range

        # handle firewall rules
        def trans_allowed(attrs):
            return [
                dict(
                    [("IPProtocol", proto)]
                    + ([("ports", ports)] if ports is not None else [])
                )
                for proto, ports in attrs.items()
            ]

        if check:
            firewalls = [
                f
                for f in self.connect().ex_list_firewalls()
                if f.network.name == defn.network_name
            ]

            # delete stray rules and mark changed ones for update
            for fw in firewalls:
                fw_name = next(
                    (
                        k
                        for (k, v) in self.firewall.items()
                        if fw.name == self.firewall_name(k)
                    ),
                    None,
                )
                if fw_name:
                    rule = self.firewall[fw_name]

                    rule["sourceRanges"] = self.warn_if_firewall_changed(
                        fw_name,
                        rule["sourceRanges"],
                        normalize_list(fw.source_ranges),
                        "source ranges",
                    )
                    rule["sourceTags"] = self.warn_if_firewall_changed(
                        fw_name,
                        rule["sourceTags"],
                        normalize_list(fw.source_tags),
                        "source tags",
                    )
                    rule["targetTags"] = self.warn_if_firewall_changed(
                        fw_name,
                        rule["targetTags"],
                        normalize_list(fw.target_tags),
                        "target tags",
                    )

                    if fw.allowed != trans_allowed(rule["allowed"]):
                        self.warn(
                            "{0} allowed ports and protocols have changed unexpectedly".format(
                                self.full_firewall_name(fw_name)
                            )
                        )
                        rule["allowed"] = {}  # mark for update

                    self.update_firewall(fw_name, rule)
                else:
                    self.warn(
                        "deleting {0} which isn't supposed to exist...".format(
                            self.firewall_name(fw_name)
                        )
                    )
                    fw.destroy()

            # find missing firewall rules
            for k, v in self.firewall.items():
                if not any(fw.name == self.firewall_name(k) for fw in firewalls):
                    self.warn("firewall rule '{0}' has disappeared...".format(k))
                    self.update_firewall(k, None)

        # add new and update changed
        for k, v in defn.firewall.items():
            if k in self.firewall:
                if v == self.firewall[k]:
                    continue
                self.log("updating {0}...".format(self.firewall_name(k)))
                try:
                    firewall = self.connect().ex_get_firewall(self.firewall_name(k))
                    firewall.allowed = trans_allowed(v["allowed"])
                    firewall.source_ranges = v["sourceRanges"]
                    firewall.source_tags = v["sourceTags"]
                    firewall.target_tags = v["targetTags"]
                    firewall.update()
                except libcloud.common.google.ResourceNotFoundError:
                    raise Exception(
                        "tried updating a firewall rule that doesn't exist; "
                        "please run 'deploy --check' to fix this"
                    )

            else:
                self.log("creating {0}...".format(self.full_firewall_name(k)))
                try:
                    self.connect().ex_create_firewall(
                        self.firewall_name(k),
                        trans_allowed(v["allowed"]),
                        network=self.network_name,
                        source_ranges=v["sourceRanges"],
                        source_tags=v["sourceTags"],
                        target_tags=v["targetTags"],
                    )
                except libcloud.common.google.ResourceExistsError:
                    raise Exception(
                        "tried creating a firewall rule that already exists; "
                        "please run 'deploy --check' to fix this"
                    )

            self.update_firewall(k, v)

        # delete unneeded
        for k in set(self.firewall.keys()) - set(defn.firewall.keys()):
            self.destroy_firewall(k)

    def destroy(self, wipe=False):
        if self.state == self.UP:
            try:
                network = self.network()
                if not self.depl.logger.confirm(
                    "are you sure you want to destroy {0}?".format(self.full_name)
                ):
                    return False

                for k in self.firewall.keys():
                    self.destroy_firewall(k)

                self.log("destroying {0}...".format(self.full_name))
                network.destroy()
            except libcloud.common.google.ResourceNotFoundError:
                self.warn(
                    "tried to destroy {0} which didn't exist".format(self.full_name)
                )

        return True

{
  gcpProject                     # (required) GCP project to deploy to
, serviceAccount                 # (required) GCP service account email
, accessKey                      # (required) path to GCP access key
, region ? "us-east1-b"          # GCE region
, instanceType ? "n1-standard-2" # Default GCE VM (instance) type
, subnet ? ""
, volumeSize ? 50                # Default volume size
, labels ? {}
, description ? ""
, ...
}:
{
  network.description = description;

  defaults =
    { config, resources, lib, name, uuid, pkgs, ...}:
    let
      machineName = "${config.deployment.name}-" + "${name}-" + builtins.substring 2 6 "${uuid}";
    in
    rec {
      deployment.targetEnv = "gce";
      deployment.gce = {
        inherit region subnet serviceAccount machineName;
        project = gcpProject;
        labels = labels;
        instanceType = lib.mkDefault instanceType;
        accessKey = builtins.readFile accessKey;
        rootDiskSize = 10;
      };

      fileSystems."/data" = {
        fsType = "xfs";
        options = [ "noatime" "nodiratime" ];
        autoFormat = true;
        formatOptions = "-f";
        gce.disk = lib.mkDefault null;
        gce.disk_name = lib.mkDefault null;
        gce.size = lib.mkDefault volumeSize;
        gce.diskType = lib.mkDefault "ssd";
      };
   };

  # GCE Disk for Frontend
  resources.gceDisks.frontend-volume =
    { resources, lib, ...}:
    let
      namespace = resources.machines.frontend.deployment.gce;
    in
    {
      inherit (namespace) project serviceAccount region accessKey labels;
      inherit (resources.machines.frontend.fileSystems."/data".gce) size disk diskType;
      name = "${namespace.machineName}-volume";
    };

  # Machine
  frontend =
    { resources, lib, ... }:
    {
      fileSystems."/data".gce.disk       = resources.gceDisks.frontend-volume;
      fileSystems."/data".gce.disk_name  = "volume";
    };

}

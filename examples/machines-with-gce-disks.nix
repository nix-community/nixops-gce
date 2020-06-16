{
  gcpProject                     # (required) GCP project to deploy to
, serviceAccount                 # (required) GCP service account email
, accessKey                      # (required) path to GCP access key
, region ? "us-east1-b"          # GCE region
, instanceType ? "n1-standard-2" # Default GCE VM (instance) type
, network ? ""                   # GCP network to create resources into
, subnet ? ""

, volumeSize ? 50                # Default volume size
, instanceServiceAccount ? ""    # Email of the service account to be assigned to the instance
, instanceScopes ? []            # Access scopes to be assigned to the instance
, preemptible ? true             # Preemtpible volatile machine

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
      networkTags = [ "default" ];
    in
    rec {
      deployment.targetEnv = "gce";
      deployment.gce = {
        inherit region network subnet serviceAccount machineName;
        project = gcpProject;
        tags = networkTags;
        labels = labels;
        instanceType = lib.mkDefault instanceType;
        instanceServiceAccount = {
          email = instanceServiceAccount;
          scopes =
           [
             "https://www.googleapis.com/auth/devstorage.read_write"
             "https://www.googleapis.com/auth/logging.write"
             "https://www.googleapis.com/auth/monitoring.write"
             "https://www.googleapis.com/auth/trace.append"
           ] ++ instanceScopes;
        };
        accessKey = builtins.readFile accessKey;
        scheduling = if preemptible then {
          preemptible = true;
          automaticRestart = false;
          onHostMaintenance = "TERMINATE";
        } else {};
        rootDiskSize = 100;
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

      environment.systemPackages = [ pkgs.google-cloud-sdk ];
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

  # Frontend Machine
  frontend =
    { resources, lib, ... }:
    {
      fileSystems."/data".gce.disk       = resources.gceDisks.frontend-volume;
      fileSystems."/data".gce.disk_name  = "volume";
    };

  # GCE Disk for Backend
  resources.gceDisks.backend-volume =
    { resources, lib, ...}:
    let
      namespace = resources.machines.backend.deployment.gce;
    in
    {
      inherit (namespace) project serviceAccount region accessKey labels;
      inherit (resources.machines.backend.fileSystems."/data".gce) size disk diskType;
      name = "${namespace.machineName}-volume";
      #snapshot ="test";
      #image = {
      #  name = "n-4151a235c48c11e786970ae168952ac0-bootstrap";
      #  family = null;
      #  project = "new-account";
      #};
    };

  # Backend Machine
  backend =
    { resources, lib, ... }:
    {
      fileSystems."/data".gce.disk       = resources.gceDisks.backend-volume;
      fileSystems."/data".gce.disk_name  = "volume";
    };
}

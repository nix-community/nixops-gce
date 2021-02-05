{
  gcpProject                     # (required) GCP project to deploy to
, serviceAccount                 # (required) GCP service account email
, accessKey                      # (required) path to GCP access key
, region ? "us-east1-b"          # GCE region
, instanceType ? "n1-standard-2" # Default GCE VM (instance) type
, subnet ? ""
, volumeSize ? 50                # Default volume size
, description ? "Deploy from custom image"
, ...
}:
{
  network.description = description;

  resources.gceImages.custom-image = 
    { config, resources, lib, name, pkgs, ...}:
    {
      inherit serviceAccount;
      project = gcpProject;
      accessKey = builtins.readFile accessKey;
      sourceUri = "gs://nixos-cloud-images/nixos-image-18.09.1228.a4c4cbb613c-x86_64-linux.raw.tar.gz";
      description = "custom 18.09 image";
    };


  custom-machine =
    { config, resources, lib, name, uuid, pkgs, ...}:
    let
      machineName = "${config.deployment.name}-" + "${name}-" + builtins.substring 2 6 "${uuid}";
    in
    rec {
      deployment.targetEnv = "gce";
      deployment.gce = {
        inherit region subnet serviceAccount machineName;
        project = gcpProject;
        instanceType = lib.mkDefault instanceType;
        accessKey = builtins.readFile accessKey;
        rootDiskSize = 10;
        bootstrapImage = resources.gceImages.custom-image;
      };
   };

}

let
  region = "europe-west1-b";
in
{
  machine =
    { resources, ... }:
    {
      deployment.targetEnv = "gce";
      deployment.gce = {
        inherit region;
        instanceType = "g1-small";
        rootDiskSize = 5;
        tags = [ "test" "instance" ];
        metadata.random = "mess";
      };
    };

  ip =
    { resources, ... }:
    {
      resources.gceStaticIPs.endpointIP = credentials // {
        region = region;
        name = "endpoint-ip";
      };
    };
}

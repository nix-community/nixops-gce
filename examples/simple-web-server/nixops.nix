let
  credentials = {
    project = "nixops-testing";
    serviceAccount = "deployer-tester@nixops-testing.iam.gserviceaccount.com";
    accessKey = builtins.readFile ~/nixops-testing-0743723f3d6d.json;
  };
in
{
  network.description = "GCE network";

  # FIXME: use pin or flake for nixpkgs
  network.nixpkgs = import <nixpkgs> { overlays = [ (self: super: { python2 = super.python3; })]; };
  network.storage.legacy = {
    databasefile = "~/.nixops/deployments-gce-example.nixops";
  } ;

  resources.gceNetworks.web = credentials // {
    firewall = {
      allow-http = {
        allowed.tcp = [ 80 ];
        sourceRanges =  ["0.0.0.0/0"];
      };
      allow-ssh = {
        allowed.tcp = [ 22 ];
        sourceRanges =  ["0.0.0.0/0"];
      };
    };
  };

  machine = { pkgs, resources, ... }:
    { deployment.targetEnv = "gce";
      deployment.gce = credentials // {
        # instance properties
        region = "europe-west1-b";
        instanceType = "n1-standard-2";
        tags = ["crazy"];
        scheduling.automaticRestart = true;
        scheduling.onHostMaintenance = "MIGRATE";
        rootDiskSize = 20;
        network = resources.gceNetworks.web;
      };

      # fileSystems."/data"=
      #   { autoFormat = true;
      #     fsType = "ext4";
      #     gce.size = 10;
      #     gce.disk_name = "data";
      #   };

      services.nginx.enable = true;
      services.nginx.virtualHosts."localhost".root = pkgs.nix.doc + "/share/doc/nix/manual";
      networking.firewall.allowedTCPPorts = [ 80 ];
    };
}

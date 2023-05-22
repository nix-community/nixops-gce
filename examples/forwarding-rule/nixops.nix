let
  credentials = {
    project = "nixops-testing";
    serviceAccount = "deployer-tester@nixops-testing.iam.gserviceaccount.com";
    accessKey = builtins.readFile ~/nixops-testing-0743723f3d6d.json;
  };

  projectName = "nixops-testing";
  regionName = "europe-west4";
  region = "projects/${projectName}/regions/${regionName}";
  zoneName = "${regionName}-c";
  zone = "projects/${projectName}/zones/${zoneName}";

in
{
  network.description = "GCE network";

  # FIXME: use pin or flake for nixpkgs
  network.nixpkgs = import <nixpkgs> { overlays = [ (self: super: { python2 = super.python3; })]; };
  network.storage.legacy = {
    databasefile = "~/.nixops/deployments-gce-example.nixops";
  };

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

  # resources.gceHTTPHealthChecks."httpHealthCheck" = credentials // {
  #   name = "examples-fw-http-health-check";
  #   port = 80;
  # };

  resources.gceTargetPools."httpTargetPool" = {nodes, resources, ...}: credentials // {
      name = "examples-fw-http-target-pool";
      # healthCheck = resources.gceHTTPHealthChecks."httpHealthCheck";
      machines = [ nodes.machine.config.deployment.gce.machineName ];
      region = regionName;
  };

  resources.gceForwardingRules."httpGceForwardingRules" = {resources, ...}: credentials // {
    # make name more specific?
    name = "examples-fw-http-gce-forwarding-rules";
    protocol = "TCP";
    targetPool = "examples-fw-http-target-pool";
    description = "Web server forwarding rule";
    portRange = "80";
    region = regionName;
  };

  machine = { pkgs, resources, ... }:
    { 
      deployment.targetEnv = "gce";
      deployment.gce = credentials // {
        # instance properties
        region = zoneName;
        instanceType = "n1-standard-2";
        tags = ["crazy"];
        scheduling.automaticRestart = true;
        scheduling.onHostMaintenance = "MIGRATE";
        rootDiskSize = 20;
        network = resources.gceNetworks.web;
      };

      documentation.enable = false;

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

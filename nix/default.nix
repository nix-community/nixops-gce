{
  config_exporters = { resources, optionalAttrs, pkgs, ... }: with pkgs.lib ;[
    (config: {
      gce = optionalAttrs (config.deployment.targetEnv == "gce") config.deployment.gce;
    })
  ];
  options = [
    ./gce.nix
  ];
  resources = { evalResources, zipAttrs, resourcesByType, ...}: {
    gceDisks = evalResources ./gce-disk.nix (zipAttrs resourcesByType.gceDisks or []);
    gceStaticIPs = evalResources ./gce-static-ip.nix (zipAttrs resourcesByType.gceStaticIPs or []);
    gceNetworks = evalResources ./gce-network.nix (zipAttrs resourcesByType.gceNetworks or []);
    gceHTTPHealthChecks = evalResources ./gce-http-health-check.nix (zipAttrs resourcesByType.gceHTTPHealthChecks or []);
    gceTargetPools = evalResources ./gce-target-pool.nix (zipAttrs resourcesByType.gceTargetPools or []);
    gceForwardingRules = evalResources ./gce-forwarding-rule.nix (zipAttrs resourcesByType.gceForwardingRules or []);
    gseBuckets = evalResources ./gse-bucket.nix (zipAttrs resourcesByType.gseBuckets or []);
    gceImages = evalResources ./gce-image.nix (zipAttrs resourcesByType.gceImages  or []);
    gceRoutes = evalResources ./gce-routes.nix (zipAttrs resourcesByType.gceRoutes or []);
  };
}

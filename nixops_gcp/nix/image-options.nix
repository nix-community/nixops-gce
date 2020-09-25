{ config, lib, ... }:

with lib;
{

  options = {
    name = mkOption {
      default = null;
      example = "image-2cfda297";
      type = types.nullOr (types.either types.str (resource "gce-image"));
      description = ''
        Name of an existent image or image-resource to be used.
        Must specify the project if the image is defined as public.
      '';
    };

    family = mkOption {
      default = null;
      example = "nixos-20-03";
      type = types.nullOr types.str;
      description = ''
        Image family to grab the latest non-deprecated image from.
        Must specify the project if the image family is defined as public.
      '';
    };

    project = mkOption {
      default = null;
      example = "gcp-project";
      type = types.nullOr types.str;
      description = ''
        The parent project containing a GCE image that was made public
        for all authenticated users.
      '';
    };

  };
  config =
    (mkAssert ( (config.name == null) || (config.family == null) )
        "Must specify either image name or image family"
    (mkAssert ( (config.project != null) && ((config.name == null)
             || (config.family == null)))
        "Specify either image name or image family alongside the project"
       {}
    ));
}

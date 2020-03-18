{ config, lib, pkgs, uuid, name, ... }:

with lib;
with import <nixops/lib.nix> lib;

{

  options = (import ./gce-credentials.nix lib "image") // {

    name = mkOption {
      example = "my-bootstrap-image";
      default = "n-${shorten_uuid uuid}-${name}";
      type = types.str;
      description = "Description of the GCE image. This is the <literal>Name</literal> tag of the image.";
    };

    sourceUri = mkOption {
      example = "gs://nixos-cloud-images/nixos-image-18.09.1228.a4c4cbb613c-x86_64-linux.raw.tar.gz";
      type = types.str;
      description = "The full Google Cloud Storage URL where the disk image is stored.";
    };

    publicImage = mkOption {
      example = "nixos-18091228a4c4cbb613c-x86-64-linux";
      type = types.str;
      description = "The name of a GCE image that was made public for all authenticated users."
    };

    publicImageProject = mkOption {
      default = "predictix-operations";
      example = "nixos-gcp-project";
      type = types.str;
      description = "The parent project containing the public image."
    };

    description = mkOption {
      default = null;
      example = "bootstrap image for the DB node";
      type = types.nullOr types.str;
      description = "An optional textual description of the image.";
    };

  };

  config._type = "gce-image";

}

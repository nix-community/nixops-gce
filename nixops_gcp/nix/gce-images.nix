let self = {
  "18.03" = "nixos-1803";
  "18.09" = "nixos-1809";

  latest = self."18.09";
  project = "predictix-operations";
}; in self

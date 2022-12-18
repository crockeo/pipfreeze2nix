{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {self, flake-utils, nixpkgs}:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python310;
      in
      rec {
        defaultPackage = python.pkgs.buildPythonApplication {
          pname = "pipfreeze2nix";
          version = "0.1.0";

          src = ./src;

          # TODO: enable when i've got it working
          # propagatedBuildInputs = pkgs.callPackage ./requirements.nix {
          #   inherit python;
          #   nixpkgs = pkgs;
          # };
          propagatedBuildInputs = [
            python.pkgs.certifi
            python.pkgs.charset-normalizer
            python.pkgs.idna
            python.pkgs.packaging
            python.pkgs.requests
            python.pkgs.urllib3
          ];
        };
      }
    );
}

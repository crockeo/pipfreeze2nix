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

          src = ./.;

          propagatedBuildInputs = pkgs.callPackage ./requirements.nix {
            inherit python;
            nixpkgs = pkgs;
          };
        };
      }
    );
}

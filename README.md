# pipfreeze2nix

A tool to generate `requirements.nix` files from
[pip-compile'd](https://github.com/jazzband/pip-tools)
requirements files.

## Installation

```shell
nix profile install git+https://github.com/crockeo/pipfreeze2nix
```

## Usage

```shell
pipfreeze2nix <path/to/requirements.txt>
```

Then pipfreeze2nix will generate a `requirements.nix` file in that same directory.
You can use `requirements.nix` as a `propagatedBulidInputs` inside of
a `buildPythonApplication` or `buildPythonPackage` call.
For example, this project's [requirements.nix](./requirements.nix)
at time of writing:

```nix
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

          propagatedBuildInputs = pkgs.callPackage ./requirements.nix {
            inherit python;
            nixpkgs = pkgs;
          };
        };
      }
    );
}
```

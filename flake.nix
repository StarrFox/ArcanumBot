{
  description = "arcanumbot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts/";
    nix-systems.url = "github:nix-systems/default";
  };

  outputs = inputs @ {
    self,
    flake-parts,
    nix-systems,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      debug = true;
      systems = import nix-systems;
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: let
        overrides = self: super: {
          discord-ext-menus = super.discord-ext-menus.overridePythonAttrs (
            old: {
              buildInputs = (old.buildInputs or []) ++ [super.setuptools];
            }
          );
          jishaku = super.jishaku.overridePythonAttrs (
            old: {
              buildInputs = (old.buildInputs or []) ++ [super.setuptools];
              propagatedBuildInputs = (old.propagatedBuildInputs or []) ++ [super.setuptools];
            }
          );
        };
      in {
        packages.default = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
          overrides = [
            pkgs.poetry2nix.defaultPoetryOverrides
            overrides
          ];
        };

        devShells.default = pkgs.mkShell {
          name = "arcanumbot";
          packages = with pkgs; [(poetry.withPlugins (ps: with ps; [poetry-plugin-up])) just alejandra black isort];
        };
      };
      flake = {
        nixosModules.default = import ./modules/arcanumbot.nix {
          # packages.system is taken from pkgs.system
          selfpkgs = self.packages;
        };
      };
    };
}

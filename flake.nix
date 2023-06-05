{
  description = "arcanumbot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    forAllSystems = function:
      nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
      ] (system: function nixpkgs.legacyPackages.${system});

    overrides = self: super: {
      discord-ext-menus = super.discord-ext-menus.overridePythonAttrs (
        old: {
          buildInputs = (old.buildInputs or []) ++ [super.setuptools];
        }
      );
    };
  in {
    packages = forAllSystems (pkgs: {
      default = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        preferWheels = true;
        overrides = [
          pkgs.poetry2nix.defaultPoetryOverrides
          overrides
        ];
      };
    });

    devShells = forAllSystems (pkgs: {
      default = pkgs.mkShell {
        name = "arcanumbot";
        packages = with pkgs; [poetry just alejandra black isort];
      };
    });
  };
}

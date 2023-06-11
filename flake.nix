{
  description = "arcanumbot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    forAllSystems = nixpkgs.lib.genAttrs [
      "x86_64-linux"
      "aarch64-linux"
    ];
    forAllPkgs = function: forAllSystems (system: function nixpkgs.legacyPackages.${system});

    overrides = self: super: {
      discord-ext-menus = super.discord-ext-menus.overridePythonAttrs (
        old: {
          buildInputs = (old.buildInputs or []) ++ [super.setuptools];
        }
      );
    };
  in {
    packages = forAllPkgs (pkgs: {
      default = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        preferWheels = true;
        overrides = [
          pkgs.poetry2nix.defaultPoetryOverrides
          overrides
        ];
      };
    });

    nixosModules.default = import ./modules/arcanumbot.nix {
      # packages.system is taken from pkgs.system
      selfpkgs = self.packages;
    };

    devShells = forAllPkgs (pkgs: {
      default = pkgs.mkShell {
        name = "arcanumbot";
        packages = with pkgs; [poetry just alejandra black isort];
      };
    });
  };
}

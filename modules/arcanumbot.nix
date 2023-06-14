{selfpkgs, ...}: {
  config,
  lib,
  pkgs,
  ...
}:
with lib; let
  cfg = config.services.arcanumbot;
  defaultUser = "arcanumbot";
  spkgs = selfpkgs.${pkgs.system};
in {
  # used for debugging (show filename)
  _file = "arcanumbot.nix";

  options.services.arcanumbot = {
    enable = mkEnableOption "arcanumbot service";
    user = mkOption {
      default = defaultUser;
      type = types.str;
      example = "alice";
      description = ''
        Name of an existing user that owns the bot process
        creates a new user named arcanumbot by default
      '';
    };
    group = mkOption {
      default = defaultUser;
      type = types.str;
      example = "users";
      description = ''
        Name of an existing group that owns the bot process
        creates a new group named arcanumbot by default
      '';
    };
    tokenFile = mkOption {
      type = types.path;
      example = literalExpression "~/discord_token";
      description = lib.mdDoc ''
        file with discord token to be used by the bot
      '';
    };
  };

  config = mkIf cfg.enable {
    systemd.services.arcanumbot = {
      description = "Arcanumbot";
      wantedBy = ["multi-user.target"];
      after = ["network-online.target"];
      serviceConfig = {
        User = cfg.user;
        Group = cfg.group;
        Restart = "always";
        ExecStart = "${spkgs.default}/bin/arcanumbot --secret ${cfg.tokenFile}";
      };
    };

    users.users = optionalAttrs (cfg.user == defaultUser) {
      ${defaultUser} = {
        description = "arcanumbot process owner";
        group = cfg.group;
        isSystemUser = true;
      };
    };

    users.groups = optionalAttrs (cfg.group == defaultUser) {
      ${defaultUser} = {
        members = [defaultUser];
      };
    };
  };
}

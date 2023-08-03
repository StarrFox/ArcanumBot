# show this list
default:
    just --list

# update deps
update:
    nix flake update
    # the poetry devs dont allow this with normal update for some unknown reason
    poetry up --latest

# format
format:
    # TODO: treefmt?
    isort .
    black .
    alejandra .

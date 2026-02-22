# dotsync

Fleet-style dotfiles manager with push cascading and status dashboard.

## What makes it different

- **Fleet dashboard** — see the sync status of all your machines at once
- **Push cascading** — push from one machine, auto-pull on all others via SSH
- **New-machine bootstrap** — SSH key setup, GitHub key, clone, link, brew
- **Simple config** — one TOML file, no templating engine

## Install

```bash
pipx install dotsync
```

## Quick start

```bash
# Bootstrap a new machine (generates SSH key, clones dotfiles, links, brews)
dotsync setup

# See fleet status
dotsync status

# Push changes to all machines
dotsync push

# Pull latest on this machine
dotsync pull

# Manage fleet
dotsync add work-laptop --ssh-alias work
dotsync remove old-desktop

# Retry failed brew packages
dotsync pending
```

## Config

dotsync reads `~/.dotfiles/.dotsync.toml`:

```toml
[dotsync]
repo = "git@github.com:you/dotfiles.git"
dotfiles_path = "~/.dotfiles"

[links]
".zshrc" = ".zshrc"
".zprofile" = ".zprofile"
".gitconfig" = ".gitconfig"
"ssh/config" = ".ssh/config"

[brew]
brewfile = "Brewfile"
pending_file = ".brew-pending"

[[machines]]
name = "work-mini"
ssh_alias = "work-mini"

[[machines]]
name = "home-mini"
ssh_alias = "home-mini"
```

## Status

Alpha — core scaffolding complete, implementation in progress.

## License

MIT

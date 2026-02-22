"""Load and save ~/.dotfiles/.dotsync.toml config."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


DEFAULT_CONFIG_PATH = Path.home() / ".dotfiles" / ".dotsync.toml"


@dataclass
class Machine:
    name: str
    ssh_alias: str


@dataclass
class Config:
    repo: str = ""
    dotfiles_path: str = "~/.dotfiles"
    links: dict[str, str] = field(default_factory=dict)
    brewfile: str = "Brewfile"
    pending_file: str = ".brew-pending"
    machines: list[Machine] = field(default_factory=list)

    @property
    def dotfiles_dir(self) -> Path:
        return Path(self.dotfiles_path).expanduser()

    @property
    def config_path(self) -> Path:
        return self.dotfiles_dir / ".dotsync.toml"


def load_config(path: Path | None = None) -> Config:
    """Load config from TOML file. Returns defaults if file doesn't exist."""
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return Config()

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    ds = data.get("dotsync", {})
    brew = data.get("brew", {})
    machines_raw = data.get("machines", [])

    machines = [
        Machine(name=m["name"], ssh_alias=m.get("ssh_alias", m["name"]))
        for m in machines_raw
    ]

    return Config(
        repo=ds.get("repo", ""),
        dotfiles_path=ds.get("dotfiles_path", "~/.dotfiles"),
        links=data.get("links", {}),
        brewfile=brew.get("brewfile", "Brewfile"),
        pending_file=brew.get("pending_file", ".brew-pending"),
        machines=machines,
    )


def save_config(config: Config, path: Path | None = None) -> None:
    """Save config to TOML file."""
    config_path = path or config.config_path

    data: dict = {
        "dotsync": {
            "repo": config.repo,
            "dotfiles_path": config.dotfiles_path,
        },
        "links": config.links,
        "brew": {
            "brewfile": config.brewfile,
            "pending_file": config.pending_file,
        },
        "machines": [
            {"name": m.name, "ssh_alias": m.ssh_alias}
            for m in config.machines
        ],
    }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "wb") as f:
        tomli_w.dump(data, f)


def add_machine(name: str, ssh_alias: str | None = None) -> None:
    """Add a machine to the config."""
    from rich.console import Console

    console = Console()
    config = load_config()

    if any(m.name == name for m in config.machines):
        console.print(f"[yellow]Machine '{name}' already exists in config.[/yellow]")
        return

    config.machines.append(Machine(name=name, ssh_alias=ssh_alias or name))
    save_config(config)
    console.print(f"[green]Added machine '{name}' (ssh: {ssh_alias or name})[/green]")


def remove_machine(name: str) -> None:
    """Remove a machine from the config."""
    from rich.console import Console

    console = Console()
    config = load_config()

    original_count = len(config.machines)
    config.machines = [m for m in config.machines if m.name != name]

    if len(config.machines) == original_count:
        console.print(f"[yellow]Machine '{name}' not found in config.[/yellow]")
        return

    save_config(config)
    console.print(f"[green]Removed machine '{name}'[/green]")

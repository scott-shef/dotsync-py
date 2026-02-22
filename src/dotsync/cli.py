"""Click CLI for dotsync."""

import click

from dotsync import __version__


@click.group()
@click.version_option(version=__version__, prog_name="dotsync")
def cli():
    """Fleet-style dotfiles manager.

    Sync dotfiles across machines with push cascading,
    fleet status dashboard, and new-machine bootstrap.
    """


@cli.command()
def status():
    """Show fleet dashboard — status of all machines."""
    from dotsync.sync import fleet_status

    fleet_status()


@cli.command()
def push():
    """Auto-commit, push, and cascade to fleet."""
    from dotsync.sync import push_dotfiles

    push_dotfiles()


@cli.command()
def pull():
    """Pull latest changes and run setup locally."""
    from dotsync.sync import pull_dotfiles

    pull_dotfiles()


@cli.command()
def setup():
    """Bootstrap this machine (SSH key, GitHub, clone, link, brew)."""
    from dotsync.setup_machine import bootstrap

    bootstrap()


@cli.command()
@click.argument("name")
@click.option("--ssh-alias", default=None, help="SSH alias for the machine (defaults to name).")
def add(name: str, ssh_alias: str | None):
    """Add a machine to the fleet config."""
    from dotsync.config import add_machine

    add_machine(name, ssh_alias=ssh_alias or name)


@cli.command()
@click.argument("name")
def remove(name: str):
    """Remove a machine from the fleet config."""
    from dotsync.config import remove_machine

    remove_machine(name)


@cli.command()
def pending():
    """Show or install failed brew packages."""
    from dotsync.brewfile import show_pending

    show_pending()

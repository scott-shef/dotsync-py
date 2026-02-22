"""New-machine bootstrap: SSH key, GitHub, clone, link, brew."""

from __future__ import annotations

import platform
import subprocess
import webbrowser
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from dotsync.config import load_config
from dotsync.linker import link_dotfiles


def _run(cmd: list[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)


def _generate_ssh_key(console: Console) -> Path:
    """Generate an ED25519 SSH key if one doesn't exist."""
    key_path = Path.home() / ".ssh" / "id_ed25519"
    if key_path.exists():
        console.print(f"[dim]SSH key already exists at {key_path}[/dim]")
        return key_path

    console.print("Generating SSH key...")
    key_path.parent.mkdir(mode=0o700, exist_ok=True)
    hostname = platform.node()
    _run([
        "ssh-keygen", "-t", "ed25519",
        "-f", str(key_path),
        "-N", "",  # no passphrase
        "-C", f"dotsync@{hostname}",
    ])
    console.print(f"[green]Created {key_path}[/green]")
    return key_path


def _add_key_to_github(console: Console, key_path: Path) -> None:
    """Show the public key and open GitHub settings to add it."""
    pub_path = key_path.with_suffix(".pub")
    pub_key = pub_path.read_text().strip()

    console.print("\n[bold]Add this SSH key to GitHub:[/bold]")
    console.print(f"\n  {pub_key}\n")

    if Confirm.ask("Open GitHub SSH settings in browser?", default=True):
        webbrowser.open("https://github.com/settings/ssh/new")
        console.print("[dim]Waiting for you to add the key... Press Enter when done.[/dim]")
        input()


def _clone_dotfiles(console: Console, repo: str, dotfiles_path: Path) -> None:
    """Clone the dotfiles repo if the directory doesn't exist."""
    if dotfiles_path.exists():
        console.print(f"[dim]Dotfiles directory already exists at {dotfiles_path}[/dim]")
        return

    console.print(f"Cloning {repo}...")
    result = _run(
        ["git", "clone", repo, str(dotfiles_path)],
        check=False,
    )
    if result.returncode != 0:
        console.print(f"[red]Clone failed:[/red] {result.stderr.strip()}")
        console.print("[yellow]Make sure you've added your SSH key to GitHub.[/yellow]")
        raise SystemExit(1)
    console.print(f"[green]Cloned to {dotfiles_path}[/green]")


def _run_brew_bundle(console: Console, dotfiles_path: Path, brewfile: str) -> None:
    """Run brew bundle if on macOS and Brewfile exists."""
    if platform.system() != "Darwin":
        console.print("[dim]Skipping brew (not macOS).[/dim]")
        return

    brewfile_path = dotfiles_path / brewfile
    if not brewfile_path.exists():
        console.print(f"[dim]No {brewfile} found, skipping brew.[/dim]")
        return

    console.print("Running brew bundle...")
    result = _run(
        ["brew", "bundle", "--file", str(brewfile_path)],
        check=False,
    )
    if result.returncode != 0:
        console.print("[yellow]Some brew packages failed. Run 'dotsync pending' to retry.[/yellow]")
        # Capture failed packages
        from dotsync.brewfile import capture_failures
        capture_failures(result.stderr + result.stdout, dotfiles_path)
    else:
        console.print("[green]Brew bundle complete.[/green]")


def bootstrap() -> None:
    """Full new-machine bootstrap flow."""
    console = Console()
    config = load_config()

    console.print("[bold]dotsync setup — bootstrapping this machine[/bold]\n")

    # Step 1: SSH key
    key_path = _generate_ssh_key(console)

    # Step 2: GitHub key
    _add_key_to_github(console, key_path)

    # Step 3: Clone dotfiles
    if config.repo:
        dotfiles_path = config.dotfiles_dir
        _clone_dotfiles(console, config.repo, dotfiles_path)
    else:
        console.print("[yellow]No repo configured in .dotsync.toml. Skipping clone.[/yellow]")
        console.print("[dim]Set dotsync.repo in your config after cloning manually.[/dim]")
        return

    # Step 4: Symlink dotfiles
    console.print("\nLinking dotfiles...")
    link_dotfiles()

    # Step 5: Brew bundle
    _run_brew_bundle(console, config.dotfiles_dir, config.brewfile)

    # Step 6: Add this machine to config
    hostname = platform.node().split(".")[0].lower()
    if not any(m.name == hostname for m in config.machines):
        if Confirm.ask(f"\nAdd this machine ('{hostname}') to fleet config?", default=True):
            from dotsync.config import add_machine
            add_machine(hostname)

    console.print("\n[bold green]Setup complete![/bold green]")

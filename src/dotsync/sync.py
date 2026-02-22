"""Push, pull, cascade, and fleet status dashboard."""

from __future__ import annotations

import subprocess

from rich.console import Console
from rich.table import Table

from dotsync.config import load_config


def _run(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def _git(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a git command in the dotfiles directory."""
    config = load_config()
    return _run(["git", *args], cwd=cwd or str(config.dotfiles_dir))


def _get_changed_files(cwd: str) -> list[str]:
    """Get list of changed files (staged + unstaged + untracked)."""
    result = _run(["git", "status", "--porcelain"], cwd=cwd, check=False)
    if result.returncode != 0:
        return []
    return [
        line[3:].strip()
        for line in result.stdout.strip().splitlines()
        if line.strip()
    ]


def _auto_commit(cwd: str) -> bool:
    """Auto-commit changes with a generated message. Returns True if a commit was made."""
    changed = _get_changed_files(cwd)
    if not changed:
        return False

    # Stage everything
    _run(["git", "add", "-A"], cwd=cwd)

    # Generate commit message from changed filenames
    if len(changed) <= 5:
        files_desc = ", ".join(changed)
    else:
        files_desc = ", ".join(changed[:4]) + f" +{len(changed) - 4} more"

    message = f"update {files_desc}"
    _run(["git", "commit", "-m", message], cwd=cwd)
    return True


def fleet_status() -> None:
    """Show fleet dashboard with status of all machines."""
    console = Console()
    config = load_config()

    if not config.machines:
        console.print("[yellow]No machines configured. Run 'dotsync add <name>' to add one.[/yellow]")
        return

    table = Table(title="dotsync fleet status")
    table.add_column("Machine", style="cyan")
    table.add_column("SSH Alias", style="dim")
    table.add_column("Reachable", justify="center")
    table.add_column("Git Status", style="yellow")

    for machine in config.machines:
        # Check if machine is reachable via SSH
        result = _run(
            ["ssh", "-o", "ConnectTimeout=3", "-o", "BatchMode=yes",
             machine.ssh_alias, "echo ok"],
            check=False,
        )
        reachable = "[green]yes[/green]" if result.returncode == 0 else "[red]no[/red]"

        # Try to get git status on remote
        git_status = "—"
        if result.returncode == 0:
            gs = _run(
                ["ssh", "-o", "ConnectTimeout=3", machine.ssh_alias,
                 f"cd {config.dotfiles_path} && git status --porcelain 2>/dev/null | wc -l"],
                check=False,
            )
            if gs.returncode == 0:
                count = gs.stdout.strip()
                git_status = "clean" if count == "0" else f"{count} changed"

        table.add_row(machine.name, machine.ssh_alias, reachable, git_status)

    console.print(table)


def push_dotfiles() -> None:
    """Auto-commit local changes, push to remote, then cascade pull to fleet."""
    console = Console()
    config = load_config()
    cwd = str(config.dotfiles_dir)

    # Auto-commit
    if _auto_commit(cwd):
        console.print("[green]Committed local changes.[/green]")
    else:
        console.print("[dim]No local changes to commit.[/dim]")

    # Push to remote
    console.print("Pushing to remote...")
    result = _run(["git", "push"], cwd=cwd, check=False)
    if result.returncode != 0:
        console.print(f"[red]Push failed:[/red] {result.stderr.strip()}")
        return
    console.print("[green]Pushed.[/green]")

    # Cascade to fleet
    if not config.machines:
        return

    console.print("\nCascading to fleet...")
    for machine in config.machines:
        console.print(f"  {machine.name}...", end=" ")
        r = _run(
            ["ssh", "-o", "ConnectTimeout=5", machine.ssh_alias,
             f"cd {config.dotfiles_path} && git pull --ff-only 2>&1"],
            check=False,
        )
        if r.returncode == 0:
            console.print("[green]ok[/green]")
        else:
            console.print(f"[red]failed[/red] — {r.stderr.strip() or r.stdout.strip()}")


def pull_dotfiles() -> None:
    """Pull latest changes and report."""
    console = Console()
    config = load_config()
    cwd = str(config.dotfiles_dir)

    console.print("Pulling latest changes...")
    result = _run(["git", "pull", "--ff-only"], cwd=cwd, check=False)
    if result.returncode != 0:
        console.print(f"[red]Pull failed:[/red] {result.stderr.strip()}")
        return

    console.print(f"[green]{result.stdout.strip()}[/green]")

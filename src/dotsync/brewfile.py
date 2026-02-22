"""Brew bundle with failure capture and pending package management."""

from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console

from dotsync.config import load_config


def capture_failures(output: str, dotfiles_path: Path) -> None:
    """Parse brew bundle output and save failed packages to .brew-pending."""
    config = load_config()
    pending_path = dotfiles_path / config.pending_file

    # Extract failed package names from brew bundle output
    # Typical failure line: "Installing <name> has failed!"
    # or "Homebrew Bundle failed! N Brewfile dependencies failed to install."
    failed = []
    for line in output.splitlines():
        line = line.strip()
        if "has failed" in line.lower():
            # Try to extract the package name
            parts = line.split()
            if len(parts) >= 2:
                failed.append(parts[1])

    if failed:
        pending_path.write_text("\n".join(failed) + "\n")


def show_pending() -> None:
    """Show pending (failed) brew packages and offer to install."""
    console = Console()
    config = load_config()
    pending_path = config.dotfiles_dir / config.pending_file

    if not pending_path.exists():
        console.print("[green]No pending brew packages.[/green]")
        return

    packages = [p.strip() for p in pending_path.read_text().splitlines() if p.strip()]
    if not packages:
        console.print("[green]No pending brew packages.[/green]")
        pending_path.unlink()
        return

    console.print(f"[yellow]Pending brew packages ({len(packages)}):[/yellow]")
    for pkg in packages:
        console.print(f"  - {pkg}")

    from rich.prompt import Confirm
    if Confirm.ask("\nAttempt to install now?", default=True):
        still_failed = []
        for pkg in packages:
            console.print(f"  Installing {pkg}...", end=" ")
            result = subprocess.run(
                ["brew", "install", pkg],
                capture_output=True, text=True, check=False,
            )
            if result.returncode == 0:
                console.print("[green]ok[/green]")
            else:
                console.print("[red]failed[/red]")
                still_failed.append(pkg)

        if still_failed:
            pending_path.write_text("\n".join(still_failed) + "\n")
            console.print(f"\n[yellow]{len(still_failed)} packages still failing.[/yellow]")
        else:
            pending_path.unlink()
            console.print("\n[green]All pending packages installed![/green]")

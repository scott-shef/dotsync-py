"""Symlink dotfiles from the repo to ~."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from dotsync.config import load_config


def link_dotfiles() -> None:
    """Create symlinks for all configured links."""
    console = Console()
    config = load_config()

    if not config.links:
        console.print("[yellow]No links configured in .dotsync.toml.[/yellow]")
        return

    dotfiles_dir = config.dotfiles_dir
    home = Path.home()

    for source_rel, target_rel in config.links.items():
        source = dotfiles_dir / source_rel
        target = home / target_rel

        if not source.exists():
            console.print(f"  [red]skip[/red] {source_rel} — source not found")
            continue

        # Create parent directory if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.is_symlink():
            if target.resolve() == source.resolve():
                console.print(f"  [dim]ok[/dim]   {target_rel} → {source_rel}")
                continue
            # Symlink exists but points elsewhere — replace it
            target.unlink()

        if target.exists():
            # Real file exists — back it up
            backup = target.with_suffix(target.suffix + ".dotsync-backup")
            console.print(f"  [yellow]backup[/yellow] {target_rel} → {backup.name}")
            target.rename(backup)

        target.symlink_to(source)
        console.print(f"  [green]link[/green]  {target_rel} → {source_rel}")

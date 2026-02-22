"""Test symlink creation."""

from pathlib import Path
from unittest.mock import patch

from dotsync.config import Config
from dotsync.linker import link_dotfiles


def test_link_creates_symlinks(tmp_path):
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    home = tmp_path / "home"
    home.mkdir()

    # Create source files
    (dotfiles / ".zshrc").write_text("# zshrc")
    (dotfiles / ".gitconfig").write_text("# gitconfig")

    config = Config(
        dotfiles_path=str(dotfiles),
        links={".zshrc": ".zshrc", ".gitconfig": ".gitconfig"},
    )

    with patch("dotsync.linker.load_config", return_value=config), \
         patch("dotsync.linker.Path.home", return_value=home):
        link_dotfiles()

    assert (home / ".zshrc").is_symlink()
    assert (home / ".zshrc").resolve() == (dotfiles / ".zshrc").resolve()
    assert (home / ".gitconfig").is_symlink()


def test_link_backs_up_existing_files(tmp_path):
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    home = tmp_path / "home"
    home.mkdir()

    (dotfiles / ".zshrc").write_text("# new zshrc")
    (home / ".zshrc").write_text("# old zshrc")

    config = Config(
        dotfiles_path=str(dotfiles),
        links={".zshrc": ".zshrc"},
    )

    with patch("dotsync.linker.load_config", return_value=config), \
         patch("dotsync.linker.Path.home", return_value=home):
        link_dotfiles()

    assert (home / ".zshrc").is_symlink()
    assert (home / ".zshrc.dotsync-backup").exists()
    assert (home / ".zshrc.dotsync-backup").read_text() == "# old zshrc"


def test_link_skips_missing_source(tmp_path):
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    home = tmp_path / "home"
    home.mkdir()

    config = Config(
        dotfiles_path=str(dotfiles),
        links={".missing": ".missing"},
    )

    with patch("dotsync.linker.load_config", return_value=config), \
         patch("dotsync.linker.Path.home", return_value=home):
        link_dotfiles()

    assert not (home / ".missing").exists()

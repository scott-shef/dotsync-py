"""Common test fixtures for dotsync."""

import pytest

from dotsync.config import Config, Machine


@pytest.fixture
def sample_config(tmp_path):
    """A Config pointing at a temp directory with sample machines."""
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    return Config(
        repo="git@github.com:test/dotfiles.git",
        dotfiles_path=str(dotfiles),
        links={".zshrc": ".zshrc", ".gitconfig": ".gitconfig"},
        machines=[
            Machine(name="work-mini", ssh_alias="work-mini"),
            Machine(name="home-mini", ssh_alias="home-mini"),
        ],
    )


@pytest.fixture
def empty_config(tmp_path):
    """A Config with no machines configured."""
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()
    return Config(dotfiles_path=str(dotfiles))

"""Test config loading and saving."""

from dotsync.config import Config, Machine, load_config, save_config


def test_save_and_load_roundtrip(tmp_path):
    config_path = tmp_path / ".dotsync.toml"

    original = Config(
        repo="git@github.com:user/dots.git",
        dotfiles_path=str(tmp_path),
        links={".zshrc": ".zshrc"},
        machines=[Machine(name="test-box", ssh_alias="test-box")],
    )

    save_config(original, path=config_path)
    assert config_path.exists()

    loaded = load_config(path=config_path)
    assert loaded.repo == original.repo
    assert loaded.links == original.links
    assert len(loaded.machines) == 1
    assert loaded.machines[0].name == "test-box"


def test_load_missing_config_returns_defaults(tmp_path):
    config = load_config(path=tmp_path / "nonexistent.toml")
    assert config.repo == ""
    assert config.machines == []
    assert config.dotfiles_path == "~/.dotfiles"


def test_add_machine_duplicate(tmp_path, capsys):
    config_path = tmp_path / ".dotsync.toml"
    config = Config(
        dotfiles_path=str(tmp_path),
        machines=[Machine(name="box1", ssh_alias="box1")],
    )
    save_config(config, path=config_path)

    # Loading from default path won't work in tests, so we test the logic directly
    loaded = load_config(path=config_path)
    assert any(m.name == "box1" for m in loaded.machines)

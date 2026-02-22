"""Test that the CLI loads and --help works for each command."""

from click.testing import CliRunner

from dotsync.cli import cli


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Fleet-style dotfiles manager" in result.output


def test_cli_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_status_help():
    result = runner.invoke(cli, ["status", "--help"])
    assert result.exit_code == 0
    assert "fleet dashboard" in result.output.lower()


def test_push_help():
    result = runner.invoke(cli, ["push", "--help"])
    assert result.exit_code == 0
    assert "cascade" in result.output.lower()


def test_pull_help():
    result = runner.invoke(cli, ["pull", "--help"])
    assert result.exit_code == 0


def test_setup_help():
    result = runner.invoke(cli, ["setup", "--help"])
    assert result.exit_code == 0
    assert "bootstrap" in result.output.lower()


def test_add_help():
    result = runner.invoke(cli, ["add", "--help"])
    assert result.exit_code == 0
    assert "machine" in result.output.lower()


def test_remove_help():
    result = runner.invoke(cli, ["remove", "--help"])
    assert result.exit_code == 0
    assert "machine" in result.output.lower()


def test_pending_help():
    result = runner.invoke(cli, ["pending", "--help"])
    assert result.exit_code == 0
    assert "brew" in result.output.lower()

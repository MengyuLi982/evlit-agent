from typer.testing import CliRunner

from evagent.app import app


def test_profiles_command_lists_default_profile() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "sps_space_event_" in result.stdout


def test_help_lists_space_observation_push_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "space-observation-push" in result.stdout

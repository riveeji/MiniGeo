from pathlib import Path

from scripts.audit_project import _pytest_command, _workspace_temp_env


def test_pytest_command_uses_workspace_basetemp() -> None:
    command = _pytest_command("python")
    command_text = " ".join(command)

    assert "--basetemp" in command
    assert ".pytest_tmp" in command_text
    assert "-p" in command
    assert "no:cacheprovider" in command


def test_audit_project_runs_release_checklist_step() -> None:
    text = Path("scripts/audit_project.py").read_text(encoding="utf-8")

    assert "发布验收清单" in text
    assert "scripts/write_release_checklist.py" in text


def test_workspace_temp_env_uses_project_temp_dir() -> None:
    env = _workspace_temp_env(Path(".pytest_tmp"))

    assert env["TMP"].endswith(".pytest_tmp")
    assert env["TEMP"].endswith(".pytest_tmp")

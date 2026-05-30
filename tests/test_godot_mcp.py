import os
import sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcps.godot.server import scaffold_project, export_html5
from unittest.mock import patch


def test_scaffold_creates_project_godot(tmp_path):
    result = scaffold_project(name="test-game", path=str(tmp_path))
    project_dir = tmp_path / "test-game"
    assert project_dir.exists()
    assert (project_dir / "project.godot").exists()


def test_scaffold_creates_export_presets(tmp_path):
    scaffold_project(name="test-game", path=str(tmp_path))
    project_dir = tmp_path / "test-game"
    presets = (project_dir / "export_presets.cfg").read_text()
    assert 'platform="Web"' in presets
    assert 'name="Web"' in presets


def test_scaffold_creates_subdirs(tmp_path):
    scaffold_project(name="test-game", path=str(tmp_path))
    project_dir = tmp_path / "test-game"
    for subdir in ["scenes", "scripts", "rooms", "sprites", "audio"]:
        assert (project_dir / subdir).exists(), f"Missing subdir: {subdir}"


def test_scaffold_returns_project_path(tmp_path):
    result = scaffold_project(name="test-game", path=str(tmp_path))
    assert result == str(tmp_path / "test-game")


def test_export_html5_calls_godot_headless(tmp_path):
    scaffold_project(name="test-game", path=str(tmp_path))
    project_path = str(tmp_path / "test-game")
    output_path = str(tmp_path / "test-game" / "build" / "index.html")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        export_html5(project_path=project_path, output_path=output_path)
    call_args = mock_run.call_args[0][0]
    assert "--headless" in call_args
    assert "--export-release" in call_args
    assert "Web" in call_args


def test_export_html5_rejects_path_traversal(tmp_path):
    scaffold_project(name="test-game", path=str(tmp_path))
    project_path = str(tmp_path / "test-game")
    with pytest.raises(ValueError, match="outside project"):
        export_html5(project_path=project_path, output_path="/tmp/evil/index.html")

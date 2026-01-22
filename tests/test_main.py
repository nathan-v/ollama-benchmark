import pytest
import subprocess
import yaml
from unittest.mock import patch, MagicMock, call, mock_open
from typer.testing import CliRunner
import llm_benchmark.main as main
from llm_benchmark import run_benchmark
from llm_benchmark.systeminfo import sysmain


@patch("llm_benchmark.main.sysmain.get_extra")
@patch("llm_benchmark.main.check_ollama_version")
@patch("llm_benchmark.main.pull_models")
@patch("llm_benchmark.main.run_benchmark.run_benchmark")
def test_run_command(
    mock_run_benchmark, mock_pull_models, mock_check_ollama_version, mock_get_extra
):
    # Test run command with default parameters
    mock_get_extra.return_value = {
        "memory": 32.0,
        "cpu": "test_cpu",
        "gpu": "test_gpu",
        "os_version": "test_os",
    }
    mock_check_ollama_version.return_value = "0.1.0"
    mock_run_benchmark.return_value = None

    runner = CliRunner()
    result = runner.invoke(main.app, ["run"])

    assert result.exit_code == 0
    assert "Total memory size : 32.00 GB" in result.output
    assert "ollama_version: 0.1.0" in result.output


@patch("llm_benchmark.main.sysmain.get_extra")
@patch("llm_benchmark.main.check_ollama_version")
@patch("llm_benchmark.main.pull_models")
@patch("llm_benchmark.main.run_benchmark.run_benchmark")
def test_run_command_custom_benchmark(
    mock_run_benchmark, mock_pull_models, mock_check_ollama_version, mock_get_extra
):
    # Test run command with custom benchmark file
    mock_get_extra.return_value = {
        "memory": 32.0,
        "cpu": "test_cpu",
        "gpu": "test_gpu",
        "os_version": "test_os",
    }
    mock_check_ollama_version.return_value = "0.1.0"

    # Mock the run_benchmark function (actual implementation doesn't return anything)
    mock_run_benchmark.return_value = None

    runner = CliRunner()
    result = runner.invoke(main.app, ["run", "--custombenchmark", "custom_benchmark.yml"])

    assert result.exit_code == 0
    # The actual implementation prints the full path, not just the filename
    # We'll check for the presence of the key phrase without the exact path
    assert "running custom benchmark from models_file_path:" in result.output


def test_sysinfo_command():
    # Test sysinfo command
    with patch("llm_benchmark.main.sysmain.get_extra") as mock_get_extra:
        mock_get_extra.return_value = {
            "memory": 32.0,
            "cpu": "test_cpu",
            "gpu": "test_gpu",
            "os_version": "test_os",
            "system_name": "Linux",
        }
        runner = CliRunner()
        result = runner.invoke(main.app, ["sysinfo"])
        assert result.exit_code == 0
        assert "memory : 32.00 GB" in result.output


def test_run_command_success():
    # Test successful command execution
    with patch("llm_benchmark.main.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="ollama version 0.1.0", stderr="", returncode=0
        )
        result = main.run_command(["ollama", "--version"])
        assert result == "ollama version 0.1.0"


def test_run_command_failure():
    # Test failed command execution
    with patch("llm_benchmark.main.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(0, "Darn")
        result = main.run_command(["ollama", "--version"])
        assert result is None


def test_check_ollama_version_success():
    # Test successful version check
    with patch("llm_benchmark.main.run_command") as mock_run_command:
        mock_run_command.return_value = "ollama version is 0.14.3\nwarning: this is a test"
        result = main.check_ollama_version("ollama")
        assert result == "0.14.3"


def test_check_ollama_version_no_warning():
    # Test version check without warning
    with patch("llm_benchmark.main.run_command") as mock_run_command:
        mock_run_command.return_value = "ollama version is 0.14.3"
        result = main.check_ollama_version("ollama")
        assert result == "0.14.3"


def test_parse_yaml_success():
    # Test successful YAML parsing
    yaml_content = """
models:
  - model: "test-model-1"
  - model: "test-model-2"
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)) as mock_file:
        result = main.parse_yaml("dummy_path.yml")
        expected = {"models": [{"model": "test-model-1"}, {"model": "test-model-2"}]}
        assert result == expected
        mock_file.assert_called_once_with("dummy_path.yml", "r")


def test_parse_yaml_error():
    # Test YAML parsing error
    with patch("builtins.open", side_effect=yaml.YAMLError("error")):
        with pytest.raises(yaml.YAMLError):
            main.parse_yaml("dummy_path.yml")


def test_pull_models_success():
    # Test successful model pulling
    model_list = ["test-model-1", "test-model-2"]
    with patch("llm_benchmark.main.models_file_to_list", return_value=model_list):
        with patch("llm_benchmark.main.ollama") as mock_ollama:
            mock_ollama.pull.return_value = True
            main.pull_models(None, "dummy_path.yml")
            mock_ollama.pull.assert_has_calls(
                [call("test-model-1"), call("test-model-2")]
            )

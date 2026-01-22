import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from llm_benchmark.main import app
from llm_benchmark import check_models, check_ollama, run_benchmark
from llm_benchmark.systeminfo import sysmain


def test_hello_command():
    # Test hello command
    runner = CliRunner()
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output


def test_goodbye_command():
    # Test goodbye command
    runner = CliRunner()
    result = runner.invoke(app, ["goodbye", "World"])
    assert result.exit_code == 0
    assert "Bye World!" in result.output


def test_goodbye_command_formal():
    # Test goodbye command with formal flag
    runner = CliRunner()
    result = runner.invoke(app, ["goodbye", "World", "--formal"])
    assert result.exit_code == 0
    assert "Goodbye Mr.(Ms.) World. Have a good day." in result.output


@patch("llm_benchmark.main.sysmain.get_extra")
@patch("llm_benchmark.main.check_ollama.check_ollama_version")
@patch("llm_benchmark.main.check_models.pull_models")
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

    # Mock the run_benchmark function to return a test result
    mock_run_benchmark.return_value = {"test-model": "10.50"}

    runner = CliRunner()
    result = runner.invoke(app, ["run"])

    assert result.exit_code == 0
    assert "Total memory size : 32.00 GB" in result.output
    assert "ollama_version: 0.1.0" in result.output


@patch("llm_benchmark.main.sysmain.get_extra")
@patch("llm_benchmark.main.check_ollama.check_ollama_version")
@patch("llm_benchmark.main.check_models.pull_models")
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

    # Mock the run_benchmark function to return a test result
    mock_run_benchmark.return_value = {"test-model": "10.50"}

    runner = CliRunner()
    result = runner.invoke(app, ["run", "--custombenchmark", "custom_benchmark.yml"])

    assert result.exit_code == 0
    assert (
        "running custom benchmark from models_file_path: custom_benchmark.yml"
        in result.output
    )


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
        result = runner.invoke(app, ["sysinfo"])
        assert result.exit_code == 0
        assert "memory : 32.00 GB" in result.output

import subprocess

import pytest
from unittest.mock import patch, MagicMock
from llm_benchmark.check_ollama import run_command, check_ollama_version


def test_run_command_success():
    # Test successful command execution
    with patch("llm_benchmark.check_ollama.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="ollama version 0.1.0", stderr="", returncode=0
        )
        result = run_command(["ollama", "--version"])
        assert result == "ollama version 0.1.0"


def test_run_command_failure():
    # Test failed command execution
    with patch("llm_benchmark.check_ollama.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(0, "Darn")
        result = run_command(["ollama", "--version"])
        assert result is None


def test_check_ollama_version_success():
    # Test successful version check
    with patch("llm_benchmark.check_ollama.run_command") as mock_run_command:
        mock_run_command.return_value = "ollama version 0.1.0\nwarning: this is a test"
        result = check_ollama_version("ollama")
        assert result == "0.1.0"


def test_check_ollama_version_no_warning():
    # Test version check without warning
    with patch("llm_benchmark.check_ollama.run_command") as mock_run_command:
        mock_run_command.return_value = "ollama version 0.1.0"
        result = check_ollama_version("ollama")
        assert result == "0.1.0"

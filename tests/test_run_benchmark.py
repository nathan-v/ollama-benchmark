import pytest
from unittest.mock import patch, MagicMock, mock_open
import yaml
from llm_benchmark.run_benchmark import parse_yaml, run_benchmark


def test_parse_yaml_success():
    # Test successful YAML parsing
    yaml_content = """
models:
  - model: "test-model-1"
  - model: "test-model-2"
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)) as mock_file:
        result = parse_yaml("dummy_path.yml")
        expected = {"models": [{"model": "test-model-1"}, {"model": "test-model-2"}]}
        assert result == expected
        mock_file.assert_called_once_with("dummy_path.yml", "r")


def test_parse_yaml_error():
    # Test YAML parsing error
    with patch("builtins.open", side_effect=yaml.YAMLError("error")):
        with pytest.raises(yaml.YAMLError):
            parse_yaml("dummy_path.yml")


def test_run_benchmark_instruct():
    # Test running benchmark with instruct type
    with patch("llm_benchmark.run_benchmark.subprocess") as mock_subprocess, patch(
        "llm_benchmark.run_benchmark.datetime"
    ) as mock_datetime, patch("llm_benchmark.run_benchmark.files") as mock_files, patch(
        "llm_benchmark.run_benchmark.parse_yaml"
    ) as mock_parse, patch(
        "llm_benchmark.run_benchmark._run_text_model_benchmark"
    ) as mock_text_benchmark, patch(
        "llm_benchmark.run_benchmark.open"
    ) as mock_open_file:

        # Mock data
        mock_models_dict = {"models": [{"model": "test-model-1"}]}

        mock_benchmark_dict = {
            "modeltypes": [
                {
                    "type": "instruct",
                    "models": [{"model": "test-model-1"}],
                    "prompts": [{"prompt": "test prompt"}],
                }
            ]
        }

        # Create a mock datetime object with proper strftime behavior
        mock_date = MagicMock()
        mock_date.strftime.return_value = "2023-01-01-120000"
        mock_datetime.datetime.today.return_value = mock_date
        mock_files.return_value.joinpath.return_value = "dummy_path"

        # Mock text benchmark to return successful result
        mock_text_benchmark.return_value = [10.5]

        # Mock open to prevent actual file creation
        mock_open_file.return_value.__enter__.return_value = MagicMock()

        mock_parse.side_effect = [mock_models_dict, mock_benchmark_dict]
        result = run_benchmark("models_path.yml", "benchmark_path.yml", "instruct")

        assert "test-model-1" in result
        assert result["test-model-1"] == "10.50"


def test_run_benchmark_vision_image():
    # Test running benchmark with vision-image type
    with patch("llm_benchmark.run_benchmark.subprocess") as mock_subprocess, patch(
        "llm_benchmark.run_benchmark.datetime"
    ) as mock_datetime, patch("llm_benchmark.run_benchmark.files") as mock_files, patch(
        "llm_benchmark.run_benchmark.parse_yaml"
    ) as mock_parse, patch(
        "llm_benchmark.run_benchmark._run_vision_model_benchmark"
    ) as mock_vision_benchmark, patch(
        "llm_benchmark.run_benchmark.open"
    ) as mock_open_file:

        # Mock data
        mock_models_dict = {"models": [{"model": "llava-test"}]}

        mock_benchmark_dict = {
            "modeltypes": [
                {
                    "type": "vision-image",
                    "models": [{"model": "llava-test"}],
                    "prompts": [
                        {"keywords": "sample1.jpg", "prompt": "describe image"}
                    ],
                }
            ]
        }

        # Create a mock datetime object with proper strftime behavior
        mock_date = MagicMock()
        mock_date.strftime.return_value = "2023-01-01-120000"
        mock_datetime.datetime.today.return_value = mock_date
        mock_files.return_value.joinpath.return_value = "dummy_path"

        # Mock vision benchmark to return successful result
        mock_vision_benchmark.return_value = [15.2]

        # Mock open to prevent actual file creation
        mock_open_file.return_value.__enter__.return_value = MagicMock()

        mock_parse.side_effect = [mock_models_dict, mock_benchmark_dict]
        result = run_benchmark("models_path.yml", "benchmark_path.yml", "vision-image")

        assert "llava-test" in result
        assert result["llava-test"] == "15.20"

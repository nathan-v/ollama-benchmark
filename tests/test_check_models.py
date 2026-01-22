import pytest
import yaml
from unittest.mock import patch, MagicMock, call, mock_open
from llm_benchmark.check_models import parse_yaml, pull_models


def test_nothing():
    pass


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


def test_pull_models_success():
    # Test successful model pulling
    yaml_parsed = {"models": [{"model": "test-model-1"}, {"model": "test-model-2"}]}
    with patch("llm_benchmark.check_models.parse_yaml", return_value=yaml_parsed):
        with patch("llm_benchmark.check_models.ollama") as mock_ollama:
            mock_ollama.pull.return_value = True
            pull_models("dummy_path.yml")
            mock_ollama.pull.assert_has_calls(
                [call("test-model-1"), call("test-model-2")]
            )

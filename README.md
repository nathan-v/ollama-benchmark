# llm-benchmark (ollama-benchmark)

LLM Benchmark for Throughput via Ollama (Local LLMs)

Measure how fast your local LLMs _really_ are—with a simple, cross-platform CLI tool that tells you the tokens-per-second truth.

## About this fork
- Added the ability to specify the tested models on the command-line; no need to write YAML
- Removed the default setting of phoning home with the results
- Removed commented-out debug code
- Removed unused/unnecessary code
- Refactored complicated methods
- Added unit tests
- Updated documentation


## Installation prerequisites

Working [Ollama](https://ollama.com) installation.

## To create a virtual environment via python3 -m venv

```bash
python3 -m venv .venv
## On Linux and macOS
source .venv/bin/activate
## On Windows Powershell or Cmd
.\.venv\Scripts\activate
```

## To create a virtual environment via uv (For uv virtual environments (recommended for Python 3.13))

```bash
uv venv .venv --python 3.13
## On Linux and macOS
source .venv/bin/activate
## On Windows Powershell or Cmd
.\.venv\Scripts\activate
```

## Installation Steps

Check out this fork and install from source

```bash
git clone https://github.com/nathan-v/ollama-benchmark.git
cd ollama-benchmark
pip install .
```


## Usage for general users directly

```bash
llm_benchmark run
```

## ollama installation with the following models installed

7B model can be run on machines with 8GB of RAM

13B model can be run on machines with 16GB of RAM

## Usage explaination

On Windows, Linux, and macOS, it will detect memory RAM size to first download required LLM models.

When memory RAM size is greater than or equal to 4GB, but less than 7GB, it will check if gemma:2b exist. The program implicitly pull the model.

```bash
ollama pull deepseek-r1:1.5b
ollama pull gemma:2b
ollama pull phi:2.7b
ollama pull phi3:3.8b
```

When memory RAM size is greater than 7GB, but less than 15GB, it will check if these models exist. The program implicitly pull these models

```bash
ollama pull phi3:3.8b
ollama pull gemma2:9b
ollama pull mistral:7b
ollama pull llama3.1:8b
ollama pull deepseek-r1:8b
ollama pull llava:7b
```

When memory RAM size is greater than 15GB, but less than 31GB, it will check if these models exist. The program implicitly pull these models

```bash
ollama pull gemma2:9b
ollama pull mistral:7b
ollama pull phi4:14b
ollama pull deepseek-r1:8b
ollama pull deepseek-r1:14b
ollama pull llava:7b
ollama pull llava:13b
```

When memory RAM size is greater than 31GB, it will check if these models exist. The program implicitly pull these models

```bash
ollama pull phi4:14b
ollama pull deepseek-r1:14b
ollama pull gpt-oss:20b
```

## Python Poetry manually(advanced) installation

<https://python-poetry.org/docs/#installing-manually>

## For developers to develop new features on Windows Powershell or on Ubuntu Linux or macOS

```bash
python3 -m venv .venv
. ./.venv/bin/activate
pip install -U pip setuptools
pip install poetry
```

## Usage in Python virtual environment

```bash
poetry install
llm_benchmark run
```

### Example #1 run the benchmark

```bash
llm_benchmark run
```

### Example #2 Benchmark run on explicitly given the path to the ollama executable (When you built your own developer version of ollama)

```bash
llm_benchmark run --ollamabin=~/code/ollama/ollama
```

### Example #3 run custom benchmark models

Run with --custombenchmark and space-separated a list of models

```bash
llm_benchmark run --custombenchmark="deepseek-r1:1.5b qwen:0.5b"
```

### Example #4 run custom benchmark models from a YAML file

1. Create a custom benchmark file like following yaml format, replace with your own benchmark models, remember to use double quote for your model name

```yaml
file_name: "custombenchmarkmodels.yml"
version: 2.0.custom
models:
  - model: "deepseek-r1:1.5b"
  - model: "qwen:0.5b"
```

2. run with the flag and point to the path of custombenchmarkmodels.yml

```bash
llm_benchmark run --custombenchmark=path/to/custombenchmarkmodels.yml
```

## Reference

[Ollama](https://ollama.com)

import os, subprocess, yaml
from importlib.resources import files

import typer
import ollama

from llm_benchmark import run_benchmark
from .systeminfo import sysmain

app = typer.Typer()


def parse_yaml(yaml_file_path):
    with open(yaml_file_path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
    return data


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e}")


def models_file_to_list(models_file: str) -> list[str]:
    print(f"LLM models file path：{models_file}")
    models_dict = parse_yaml(models_file)
    models_list = []
    for x in models_dict["models"]:
        models_list.append(x["model"])
    return models_list


def pull_models(
    model_list: list[str] | None = None, models_file: str | None = None
) -> None:
    if models_file:
        model_list = models_file_to_list(models_file)
    print(f"Checking and pulling the following LLM models:")
    for model_name in model_list:
        print(model_name)
        ollama.pull(model_name)
    return None


def check_ollama_version(ollamabin: str = "ollama") -> str:
    res = run_command([ollamabin, "--version"])
    if "warning" in res:
        version_string = [item for item in res.split("\n") if "version" in item][0]
    else:
        version_string = res
    return version_string.split(" ")[3]


@app.command()
def run(
    ollamabin: str = typer.Option("ollama", "--ollamabin"),
    custombenchmark: str = typer.Option(None, "--custombenchmark"),
):
    print("-" * 20)
    sys_info = sysmain.get_extra()
    print(f"Total memory size : {sys_info['memory']:.2f} GB")
    print(f"cpu_info: {sys_info['cpu']}")
    print(f"gpu_info: {sys_info['gpu']}")
    print(f"os_version: {sys_info['os_version']}")
    print("-" * 20)
    ollama_version = check_ollama_version(ollamabin)
    print(f"ollama_version: {ollama_version}")
    print("-" * 20)

    ft_mem_size = float(f"{sys_info['memory']:.2f}")

    models_list = None
    models_file_path = None
    if custombenchmark:
        if os.path.isfile(custombenchmark):
            models_file_path = custombenchmark
        else:
            models_list = custombenchmark.split(" ")
        print(f"running custom benchmark from models_file_path: {models_file_path}")
    else:
        models_file_path = str(
            files("llm_benchmark").joinpath("data/benchmark_models_32gb_ram.yml")
        )
        if ft_mem_size >= 1 and ft_mem_size < 2:
            models_file_path = str(
                files("llm_benchmark").joinpath("data/benchmark_models_2gb_ram.yml")
            )
        elif ft_mem_size >= 2 and ft_mem_size < 4:
            models_file_path = str(
                files("llm_benchmark").joinpath("data/benchmark_models_3gb_ram.yml")
            )
        elif ft_mem_size >= 4 and ft_mem_size < 7:
            models_file_path = str(
                files("llm_benchmark").joinpath("data/benchmark_models_4gb_ram.yml")
            )
        elif ft_mem_size >= 7 and ft_mem_size < 15:
            models_file_path = str(
                files("llm_benchmark").joinpath("data/benchmark_models_8gb_ram.yml")
            )
        elif ft_mem_size >= 15 and ft_mem_size < 31:
            models_file_path = str(
                files("llm_benchmark").joinpath("data/benchmark_models_16gb_ram.yml")
            )

    pull_models(models_list, models_file_path)
    print("-" * 20)

    benchmark_file_path = str(files("llm_benchmark").joinpath("data/benchmark2.yml"))

    if custombenchmark:
        run_benchmark.run_benchmark(
            models_file_path,
            benchmark_file_path,
            "custom-model",
            ollamabin,
            models_list,
        )
    else:
        result1 = run_benchmark.run_benchmark(
            models_file_path, benchmark_file_path, "instruct", ollamabin
        )
        result2 = run_benchmark.run_benchmark(
            models_file_path, benchmark_file_path, "question-answer", ollamabin
        )
        result3 = run_benchmark.run_benchmark(
            models_file_path, benchmark_file_path, "vision-image", ollamabin
        )
        result4 = run_benchmark.run_benchmark(
            models_file_path,
            benchmark_file_path,
            "instruction-question-answer-code-generation",
            ollamabin,
        )


@app.command()
def sysinfo(formal: bool = typer.Option(True, "--formal")):
    if formal:
        sys_info = sysmain.get_extra()
        print(f"memory : {sys_info['memory']:.2f} GB")
        print(f"cpu_info: {sys_info['cpu']}")
        print(f"gpu_info: {sys_info['gpu']}")
        print(f"os_version: {sys_info['os_version']}")
    else:
        print(f"No print!")


if __name__ == "__main__":
    app()

import argparse
import yaml
import subprocess
import datetime
from importlib.resources import files


def parse_yaml(yaml_file_path):
    """Parse YAML file and return its contents."""
    with open(yaml_file_path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
    return data


def _run_vision_model_benchmark(model_name, prompt, ollamabin, log_file):
    """Run benchmark for vision models with image prompts."""
    stored_nums = []
    img_file_names = prompt["keywords"].split(",")
    for img in img_file_names:
        img_file_path = str(files("llm_benchmark").joinpath(f"data/img/{img}"))
        prompt_text = f"{prompt['prompt']} {img_file_path}"
        print(f"prompt = {prompt_text}")
        result = subprocess.run(
            [
                ollamabin,
                "run",
                model_name,
                prompt["prompt"],
                "--verbose",
            ],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        std_err = result.stderr
        log_file.write(std_err)

        for line in std_err.split("\n"):
            if ("eval rate" in line) and ("prompt" not in line):
                print(line)
                number = float(line[-20:-8])
                stored_nums.append(number)
    return stored_nums


def _run_text_model_benchmark(model_name, prompt, ollamabin, log_file):
    """Run benchmark for text models."""
    stored_nums = []
    print(f"prompt = {prompt['prompt']}")
    result = subprocess.run(
        [
            ollamabin,
            "run",
            model_name,
            prompt["prompt"],
            "--verbose",
        ],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    std_err = result.stderr
    log_file.write(std_err)

    for line in std_err.split("\n"):
        if ("eval rate" in line) and ("prompt" not in line):
            print(line)
            number = float(line[-20:-8])
            stored_nums.append(number)
    return stored_nums


def _process_model_type(models_dict, benchmark_dict, model_type, ollamabin, log_file):
    """Process all models of a specific type."""
    allowed_models = {e["model"] for e in models_dict["models"]}
    results = {}

    for model_type_config in benchmark_dict["modeltypes"]:
        if model_type_config["type"] == model_type:
            for model_config in model_type_config["models"]:
                model_name = model_config["model"]
                if model_name in allowed_models:
                    print(f"model_name =    {model_name}")
                    log_file.write(f"\nmodel_name =    {model_name}\n")
                    stored_nums = []

                    # Process all prompts for this model
                    for prompt in model_type_config["prompts"]:
                        if model_name.startswith("llava"):
                            stored_nums.extend(
                                _run_vision_model_benchmark(
                                    model_name, prompt, ollamabin, log_file
                                )
                            )
                        else:
                            stored_nums.extend(
                                _run_text_model_benchmark(
                                    model_name, prompt, ollamabin, log_file
                                )
                            )

                    # Calculate average if we have results
                    if stored_nums:
                        average = sum(stored_nums) / len(stored_nums)
                        print("Average of eval rate: ", round(average, 3), " tokens/s")
                        results[model_name] = f"{round(average,3):.2f}"
                    else:
                        print("No eval rate data found for this model")
                    print("-" * 40)
                    log_file.write("\n" + "-" * 40)

    return results


def run_benchmark(
    models_file_path: str | None,
    benchmark_file_path: str,
    model_type: str,
    ollamabin: str = "ollama",
    models_list: list[str] | None = None,
):
    """Run benchmark for specified model type and return results."""
    if models_file_path:
        models_dict = parse_yaml(models_file_path)
    else:
        models_dict = {"models": []}
        for model in models_list:
            models_dict["models"].append({"model": model})
    benchmark_dict = parse_yaml(benchmark_file_path)
    results = {}

    # Handle custom model type
    if model_type == "custom-model":
        print("Running custom-model")
        # dynamically add models to benchmark_dict for custom-model
        for model in models_dict["models"]:
            for one_model_type in benchmark_dict["modeltypes"]:
                if one_model_type["type"] == "custom-model":
                    if one_model_type["models"] is None:
                        one_model_type["models"] = []
                    one_model_type["models"].append(model)

    # Create log file name with timestamp
    timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H%M%S")
    log_filename = f"log_{timestamp}.log"

    # Process all models of the specified type
    with open(log_filename, "w", encoding="utf-8") as log_file:
        results = _process_model_type(
            models_dict, benchmark_dict, model_type, ollamabin, log_file
        )

    return results

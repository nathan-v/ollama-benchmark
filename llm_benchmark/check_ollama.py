import subprocess


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()  # Return the output of the command
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e}")
        return None


def check_ollama_version(ollamabin="ollama"):
    res = run_command([ollamabin, "--version"])
    if res is None:
        return None
    # Extract version from "ollama version X.X.X" format
    lines = res.split("\n")
    # Get the first line which contains version info
    version_line = lines[0] if lines else ""
    if version_line.startswith("ollama version "):
        return version_line.split()[2]
    return None

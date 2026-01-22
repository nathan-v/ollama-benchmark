import platform
import psutil
import GPUtil
import subprocess
import os


def get_total_memory_size():
    memory_info = psutil.virtual_memory()
    return memory_info.total / (2 ** (10 * 3))


def get_system_info():
    system_info = platform.uname()
    ans = {}
    ans["system"] = f"{system_info.system}"
    ans["node_name"] = f"{system_info.node}"
    ans["release"] = f"{system_info.release}"
    ans["version"] = f"{system_info.version}"
    ans["machine"] = f"{system_info.machine}"
    ans["processor"] = f"{system_info.processor}"
    return ans


def get_cpu_info():
    cpu_info = platform.processor()
    cpu_count = psutil.cpu_count(logical=False)
    logical_cpu_count = psutil.cpu_count(logical=True)

    ans = {}
    ans["processor"] = f"{cpu_info}"
    ans["physical_cores"] = f"{cpu_count}"
    ans["logical_cores"] = f"{logical_cpu_count}"
    return ans


def get_memory_info():
    memory_info = psutil.virtual_memory()

    ans = {}
    ans["total_memory"] = f"{memory_info.total}"
    ans["available_memory"] = f"{memory_info.available}"
    ans["used_memory"] = f"{memory_info.used}"
    ans["memory_utilization"] = f"{memory_info.percent:.2f}%"
    return ans


def get_disk_info():
    disk_info = psutil.disk_usage("/")

    ans = {}
    ans["total_disk_space"] = f"{disk_info.total}"
    ans["used_disk_space"] = f"{disk_info.used}"
    ans["free_disk_space"] = f"{disk_info.free}"
    ans["disk_space_utilization"] = f" {disk_info.percent:.2f}%"
    return ans


# AMD GPU on Linux Only
def get_gpu_names_rocminfo():
    try:
        result = subprocess.run(
            ["rocminfo"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None

        gpu_names = []
        lines = result.stdout.split("\n")

        for line in lines:
            # Marketing Name is the most user-friendly identifier
            if "Marketing Name:" in line:
                name = line.split("Marketing Name:")[1].strip()

                if name and name != "N/A" and "Intel" not in name:
                    gpu_names.append(name)

        return gpu_names
    except Exception as e:
        print(f"rocminfo failed: {e}")
        return None


# Only Nvidia GPU on Windows and Linux
def get_gpu_info():

    ans = {}
    if get_system_info()["system"] == "Darwin":
        ans["0"] = "no_gpu"
        return ans
    else:
        gpus = GPUtil.getGPUs()

    if not gpus:
        print("\nNo NVIDIA GPU detected.")
        ans["0"] = "no_gpu"
    else:
        ans["0"] = "there_is_gpu"

        for i, gpu in enumerate(gpus):
            ans[f"{i+1}"] = {}
            ans[f"{i+1}"]["id"] = f"{gpu.id}"
            ans[f"{i+1}"]["name"] = f"{' '.join(gpu.name.splitlines())}"
            ans[f"{i+1}"]["driver"] = f"{gpu.driver}"
            ans[f"{i+1}"]["gpu_memory_total"] = f"{gpu.memoryTotal} MB"
            ans[f"{i+1}"]["gpu_memory_free"] = f"{gpu.memoryFree} MB"
            ans[f"{i+1}"]["gpu_memory_used"] = f"{gpu.memoryUsed} MB"
            ans[f"{i+1}"]["gpu_load"] = f"{gpu.load*100}%"
            ans[f"{i+1}"]["gpu_temperature"] = f"{gpu.temperature}°C"

    return ans


def check_windows_shell():
    parent_pid = os.getppid()
    shell_name = psutil.Process(parent_pid).name().lower()
    if "cmd" in shell_name:
        return "CMD"
    elif "powershell" in shell_name:
        return "PowerShell"
    else:
        return "Unknown"


def get_linux_gpu_names(gpu_dict):
    return "\n".join(
        gpu["name"] for key, gpu in gpu_dict.items() if key.isdigit() and key != "0"
    )


def _get_macos_info():
    """Get system information for macOS."""
    ans = {}
    print("----------Apple Mac---------")

    # Get model identifier
    r1 = subprocess.run(
        ["system_profiler", "SPHardwareDataType"],
        capture_output=True,
        text=True,
    )
    for line in r1.stdout.split("\n"):
        if "Model Identifier" in line:
            ans["model"] = f"{line[24:]}"

    # Get CPU info
    for line in r1.stdout.split("\n"):
        if "Chip" in line:
            ans["cpu"] = f"{line[12:]}"

    # Set GPU info
    if ans["cpu"].startswith("Apple"):
        ans["gpu"] = ans["cpu"]
    else:
        ans["gpu"] = "no_gpu"

    # Get OS version
    r3 = subprocess.run(
        ["system_profiler", "SPSoftwareDataType"],
        capture_output=True,
        text=True,
    )

    for line in r3.stdout.split("\n"):
        if "System Version" in line:
            ans["os_version"] = f"{line[22:]}"

    return ans


def _get_linux_info():
    """Get system information for Linux."""
    ans = {}
    print("-------Linux----------")

    # Get OS version
    try:
        r2 = subprocess.run(["lsb_release", "-a"], capture_output=True, text=True)
        software = f"{r2.stdout}"
        for line in software.split("\n"):
            if "Description" in line:
                ans["os_version"] = f"{line[12:]}".strip()
    except:
        r2 = subprocess.run(["cat", "/etc/os-release"], capture_output=True, text=True)
        software = f"{r2.stdout}"
        for line in software.split("\n"):
            if "PRETTY_NAME" in line:
                ans["os_version"] = f"{line[12:]}".strip()

    # Get CPU info
    try:
        r1 = subprocess.run(["lshw", "-C", "cpu"], capture_output=True, text=True)
        for line in r1.stdout.split("\n"):
            if "product" in line:
                ans["cpu"] = f"{line[16:]}"
    except:
        cmd = ["lscpu"]
        ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        cmd = ["grep", "Model name"]
        grep = subprocess.Popen(
            cmd, stdin=ps.stdout, stdout=subprocess.PIPE, encoding="utf-8"
        )
        ps.stdout.close()
        output, _ = grep.communicate()
        python_processes = output.split("\n")
        ans["cpu"] = python_processes[0][16:].strip()

    # Get GPU info
    if get_gpu_info()["0"] == "no_gpu":
        try:
            r2 = subprocess.run(
                ["lshw", "-C", "display"], capture_output=True, text=True
            )
            for line in r2.stdout.split("\n"):
                if "product" in line:
                    ans["gpu"] = f"{line[16:]}"
        except:
            try:
                amd_gpus = get_gpu_names_rocminfo()
                if amd_gpus is None:
                    raise Exception("No AMD GPUs")

                amd_ans = {}
                amd_ans["0"] = "there_is_amd_gpu"

                for i, gpu in enumerate(amd_gpus):
                    amd_ans[f"{i+1}"] = {}
                    amd_ans[f"{i+1}"]["id"] = f"{i}"
                    amd_ans[f"{i+1}"]["name"] = f"{gpu}"
                ans["gpu"] = get_linux_gpu_names(amd_ans)
            except:
                ans["gpu"] = "no_gpu"
    else:
        print(f"{get_gpu_info()['1']}")
        try:
            print(get_gpu_info()["2"])
            print("At least two GPU cards")
            ans["gpu"] = get_linux_gpu_names(get_gpu_info())
        except:
            print("Only one GPU card")
            # List only the first gpu name
            ans["gpu"] = get_gpu_info()["1"]["name"]

    return ans


def _get_windows_info():
    """Get system information for Windows."""
    ans = {}
    prefix_exe = "powershell.exe"

    # Get CPU info
    r_cpu = subprocess.run(
        [prefix_exe, "(Get-WmiObject Win32_Processor).Name"],
        capture_output=True,
        text=True,
    )
    ans["cpu"] = r_cpu.stdout.strip()

    # Get GPU info
    r_gpu = subprocess.run(
        [prefix_exe, "(Get-WmiObject Win32_VideoController).Caption"],
        capture_output=True,
        text=True,
    )
    str_gpu = r_gpu.stdout.strip()
    str_gpu = " ".join(str_gpu.splitlines())
    ans["gpu"] = str_gpu

    # Get OS version
    r4 = subprocess.run(
        [prefix_exe, "(Get-WmiObject Win32_OperatingSystem).Caption"],
        capture_output=True,
        text=True,
    )
    ans["os_version"] = f"{r4.stdout}"

    return ans


def get_extra():
    """Get comprehensive system information."""
    system_info = platform.uname()
    ans = {}
    ans["system"] = f"{system_info.system}"
    ans["memory"] = get_total_memory_size()
    ans["cpu"] = f"unknown"
    ans["gpu"] = f"unknown"
    ans["os_version"] = f"unknown"

    try:
        if system_info.system == "Darwin":
            ans["system_name"] = "macOS"
            ans.update(_get_macos_info())
        elif system_info.system == "Linux":
            ans["system_name"] = "Linux"
            ans.update(_get_linux_info())
        elif system_info.system == "Windows":
            ans["system_name"] = "Windows"
            ans["run_in"] = f"{check_windows_shell()}"
            ans.update(_get_windows_info())
        else:
            print(f"Unsupported system: {system_info.system}")

        return ans

    except Exception as e:
        print(f"error! when retrieving os_version, cpu, or gpu ! Error: {e}")

    return ans

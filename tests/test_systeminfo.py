import pytest
from unittest.mock import patch, MagicMock
import platform
import psutil
import GPUtil
import subprocess
from llm_benchmark.systeminfo.sysmain import (
    get_total_memory_size,
    get_system_info,
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_gpu_names_rocminfo,
    get_gpu_info,
    check_windows_shell,
    get_linux_gpu_names,
    get_extra,
)


def test_get_total_memory_size():
    # Test memory size calculation
    with patch("psutil.virtual_memory") as mock_memory:
        mock_memory.return_value.total = 34359738368  # 32 GB in bytes
        result = get_total_memory_size()
        assert result == 32.0


def test_get_system_info():
    # Test system info retrieval
    with patch("platform.uname") as mock_uname:
        mock_uname.return_value = MagicMock(
            system="Linux",
            node="test-node",
            release="5.4.0",
            version="5.4.0-123-generic",
            machine="x86_64",
            processor="x86_64",
        )
        result = get_system_info()
        expected = {
            "system": "Linux",
            "node_name": "test-node",
            "release": "5.4.0",
            "version": "5.4.0-123-generic",
            "machine": "x86_64",
            "processor": "x86_64",
        }
        assert result == expected


def test_get_cpu_info():
    # Test CPU info retrieval
    with patch("platform.processor") as mock_processor:
        with patch("psutil.cpu_count") as mock_cpu_count:
            mock_processor.return_value = "Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz"
            mock_cpu_count.side_effect = [6, 12]  # physical, logical
            result = get_cpu_info()
            expected = {
                "processor": "Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz",
                "physical_cores": "6",
                "logical_cores": "12",
            }
            assert result == expected


def test_get_memory_info():
    # Test memory info retrieval
    with patch("psutil.virtual_memory") as mock_memory:
        mock_memory.return_value = MagicMock(
            total=34359738368,  # 32 GB
            available=17179869184,  # 16 GB
            used=17179869184,  # 16 GB
            percent=50.0,
        )
        result = get_memory_info()
        expected = {
            "total_memory": "34359738368",
            "available_memory": "17179869184",
            "used_memory": "17179869184",
            "memory_utilization": "50.00%",
        }
        assert result == expected


def test_get_disk_info():
    # Test disk info retrieval
    with patch("psutil.disk_usage") as mock_disk:
        mock_disk.return_value = MagicMock(
            total=107374182400,  # 100 GB
            used=53687091200,  # 50 GB
            free=53687091200,  # 50 GB
            percent=50.0,
        )
        result = get_disk_info()
        expected = {
            "total_disk_space": "107374182400",
            "used_disk_space": "53687091200",
            "free_disk_space": "53687091200",
            "disk_space_utilization": " 50.00%",
        }
        assert result == expected


@patch("subprocess.run")
def test_get_gpu_names_rocminfo_success(mock_subprocess_run):
    # Test successful ROCm info retrieval
    mock_subprocess_run.return_value = MagicMock(
        stdout="Marketing Name: Radeon RX 7900 XTX\nMarketing Name: Radeon RX 7900 XT",
        stderr="",
        returncode=0,
    )
    result = get_gpu_names_rocminfo()
    expected = ["Radeon RX 7900 XTX", "Radeon RX 7900 XT"]
    assert result == expected


@patch("subprocess.run")
def test_get_gpu_names_rocminfo_failure(mock_subprocess_run):
    # Test ROCm info retrieval failure
    mock_subprocess_run.side_effect = Exception("rocminfo not found")
    result = get_gpu_names_rocminfo()
    assert result is None


def test_get_gpu_info_no_gpu():
    # Test GPU info when no GPU is present
    with patch("llm_benchmark.systeminfo.sysmain.get_system_info") as mock_system_info:
        mock_system_info.return_value = {"system": "Linux"}
        with patch("GPUtil.getGPUs") as mock_gpus:
            mock_gpus.return_value = []
            result = get_gpu_info()
            assert result["0"] == "no_gpu"


@patch("GPUtil.getGPUs")
def test_get_gpu_info_with_gpu(mock_gpus):
    # Test GPU info when GPU is present
    mock_gpu = MagicMock()
    mock_gpu.id = 0
    mock_gpu.name = "GeForce RTX 3080"
    mock_gpu.driver = "470.82.01"
    mock_gpu.memoryTotal = 10240
    mock_gpu.memoryFree = 5120
    mock_gpu.memoryUsed = 5120
    mock_gpu.load = 0.5
    mock_gpu.temperature = 65
    mock_gpus.return_value = [mock_gpu]

    with patch("llm_benchmark.systeminfo.sysmain.get_system_info") as mock_system_info:
        mock_system_info.return_value = {"system": "Linux"}
        result = get_gpu_info()
        assert result["0"] == "there_is_gpu"
        assert result["1"]["name"] == "GeForce RTX 3080"


def test_check_windows_shell():
    # Test Windows shell detection
    with patch("os.getppid") as mock_ppid:
        with patch("psutil.Process") as mock_process:
            mock_ppid.return_value = 1234
            mock_process.return_value.name.return_value = "cmd.exe"
            result = check_windows_shell()
            assert result == "CMD"


def test_get_linux_gpu_names():
    # Test Linux GPU names extraction
    gpu_dict = {
        "0": "there_is_gpu",
        "1": {"name": "GeForce RTX 3080"},
        "2": {"name": "GeForce RTX 3090"},
    }
    result = get_linux_gpu_names(gpu_dict)
    assert result == "GeForce RTX 3080\nGeForce RTX 3090"


@patch("platform.uname")
@patch("subprocess.run")
@patch("psutil.cpu_count")
@patch("psutil.virtual_memory")
@patch("GPUtil.getGPUs")
def test_get_extra_macos(
    mock_gpus, mock_memory, mock_cpu_count, mock_subprocess_run, mock_uname
):
    # Test system info retrieval for macOS
    mock_uname.return_value = MagicMock(system="Darwin")
    mock_memory.return_value = MagicMock(
        total=34359738368, available=17179869184, used=17179869184, percent=50.0
    )
    mock_cpu_count.return_value = 6
    mock_gpus.return_value = []

    # Mock subprocess calls for macOS
    mock_subprocess_run.side_effect = [
        MagicMock(stdout="Model Identifier: MacBookPro16,1\nChip: Apple M1\n"),
        MagicMock(stdout="System Version: macOS 12.0"),
    ]

    result = get_extra()
    assert result["system_name"] == "macOS"
    assert result["memory"] == 32.0


@patch("platform.uname")
@patch("subprocess.run")
@patch("psutil.cpu_count")
@patch("psutil.virtual_memory")
@patch("GPUtil.getGPUs")
def test_get_extra_linux(
    mock_gpus, mock_memory, mock_cpu_count, mock_subprocess_run, mock_uname
):
    # Test system info retrieval for Linux
    mock_uname.return_value = MagicMock(system="Linux")
    mock_memory.return_value = MagicMock(
        total=34359738368, available=17179869184, used=17179869184, percent=50.0
    )
    mock_cpu_count.return_value = 6
    mock_gpus.return_value = []

    # Mock subprocess calls for Linux
    mock_subprocess_run.side_effect = [
        MagicMock(stdout="Description: Ubuntu 20.04.3 LTS\n"),
        MagicMock(stdout="product: Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz\n"),
        MagicMock(stdout="product: GeForce RTX 3080\n"),
    ]

    result = get_extra()
    assert result["system_name"] == "Linux"
    assert result["memory"] == 32.0

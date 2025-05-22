import os
import sys
import tempfile
import shutil
import builtins
import run_service
from unittest import mock

# Utility to create a fake service directory with an entrypoint
def make_service_dir(tmpdir, name, entrypoint="main.py", port=5000):
    svc_path = os.path.join(tmpdir, name)
    os.makedirs(svc_path)
    entrypoint_path = os.path.join(svc_path, entrypoint)
    with open(entrypoint_path, "w") as f:
        f.write(f"app.run(port={port})\n")
    return svc_path

def test_find_services(tmp_path):
    make_service_dir(tmp_path, "foo_service")
    make_service_dir(tmp_path, "bar_service")
    os.chdir(tmp_path)
    services = run_service.find_services()
    assert set(services) == {"foo_service", "bar_service"}

def test_find_entrypoint(tmp_path):
    svc = make_service_dir(tmp_path, "foo_service", entrypoint="main.py")
    os.chdir(tmp_path)
    assert run_service.find_entrypoint("foo_service") == "main.py"

def test_parse_port(tmp_path):
    svc = make_service_dir(tmp_path, "foo_service", entrypoint="main.py", port=5555)
    entrypoint_path = os.path.join(svc, "main.py")
    assert run_service.parse_port(entrypoint_path) == 5555

@mock.patch("run_service.subprocess.Popen")
def test_start_service_opens_powershell(mock_popen, tmp_path):
    svc = make_service_dir(tmp_path, "foo_service", entrypoint="main.py", port=5000)
    os.chdir(tmp_path)
    run_service.start_service("foo_service", "main.py", 5000)
    assert mock_popen.called
    args, kwargs = mock_popen.call_args
    assert "powershell" in args[0]

@mock.patch("builtins.input", return_value="all")
@mock.patch("run_service.start_service")
def test_main_select_all_services(mock_start, mock_input, tmp_path):
    make_service_dir(tmp_path, "foo_service", port=5001)
    make_service_dir(tmp_path, "bar_service", port=5002)
    os.chdir(tmp_path)
    with mock.patch("run_service.find_services", return_value=["foo_service", "bar_service"]):
        run_service.main()
        assert mock_start.call_count == 2

@mock.patch("builtins.input", return_value="1")
@mock.patch("run_service.start_service")
def test_main_select_one_service(mock_start, mock_input, tmp_path):
    make_service_dir(tmp_path, "foo_service", port=5001)
    make_service_dir(tmp_path, "bar_service", port=5002)
    os.chdir(tmp_path)
    with mock.patch("run_service.find_services", return_value=["foo_service", "bar_service"]):
        run_service.main()
        assert mock_start.call_count == 1 
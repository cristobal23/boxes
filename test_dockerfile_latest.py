import os
import pytest
import subprocess
import testinfra
import shutil


DOCKER_TAG = "latest"
EXPECTED_VERSION = "3.22.2"


if shutil.which("docker") is None:
    pytest.skip("Docker is not installed or not in PATH", allow_module_level=True)

@pytest.fixture(scope='session')
def host(request):
    """Build and run a Docker container for alpine:latest."""
    username = os.environ.get("DOCKER_USERNAME", "cristobal23")
    image_name = f"{username}/alpine:{DOCKER_TAG}"

    # Build Docker image using the latest alpine tag
    subprocess.check_call(
        [
            "docker",
            "build",
            "-f",
            "Dockerfile",
            "-t",
            image_name,
            ".",
        ]
    )

    # Run the container
    docker_id = (
        subprocess.check_output(
            ["docker", "run", "-d", image_name, "tail", "-f", "/dev/null"]
        )
        .decode()
        .strip()
    )

    # Return a testinfra connection to the container
    host = testinfra.get_host(f"docker://{docker_id}")
    yield host

    # Cleanup
    subprocess.check_call(["docker", "rm", "-f", docker_id])


def test_latest_version(host):
    """Verify alpine:latest matches the expected release version."""
    release = host.check_output("cat /etc/alpine-release").strip()
    assert (
        release == EXPECTED_VERSION
    ), f"Expected Alpine {EXPECTED_VERSION}, but got {release}"

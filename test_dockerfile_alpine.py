import os
import pytest
import subprocess
import testinfra
import shutil


# List of Alpine versions to test
ALPINE_VERSIONS = [
    "3.19",
    "3.20",
    "3.21",
    "3.22",
]


if shutil.which("docker") is None:
    pytest.skip("Docker is not installed or not in PATH", allow_module_level=True)

@pytest.fixture(scope='session', params=ALPINE_VERSIONS)
def docker_host(request):
    """Build and run Docker containers for multiple Alpine versions."""
    docker_tag = request.param
    username = os.environ.get("DOCKER_USERNAME", "cristobal23")
    image_name = f"{username}/alpine:{docker_tag}"

    # Build Docker image with the given tag
    subprocess.check_call(
        [
            "docker",
            "build",
            "--pull"
            "-f",
            "Dockerfile",
            "-t",
            image_name,
            "--build-arg",
            f"TAG={docker_tag}",
            ".",
        ],
        timeout=900,
    )

    # Run the container
    docker_id = (
        subprocess.check_output(
            ["docker", "run", "-d", image_name, "tail", "-f", "/dev/null"],
            timeout=60,
        )
        .decode()
        .strip()
    )

    # Provide testinfra connection
    host = testinfra.get_host(f"docker://{docker_id}")
    yield host, docker_tag

    # Cleanup after tests
    subprocess.check_call(["docker", "rm", "-f", docker_id])


def test_alpine_version(docker_host):
    """Ensure the container reports the expected Alpine version."""
    h, docker_tag = docker_host
    release = h.check_output("cat /etc/alpine-release").strip()

    # Basic version consistency check
    assert release.startswith(docker_tag), f"Expected {docker_tag}, got {release}"

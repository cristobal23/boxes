import os
import pytest
import subprocess
import testinfra


# List of Alpine versions to test
ALPINE_VERSIONS = [
    "3.19",
    "3.20",
    "3.21",
    "3.22",
]


@pytest.fixture(scope='session', params=ALPINE_VERSIONS)
def host(request):
    """Build and run Docker containers for multiple Alpine versions."""
    docker_tag = request.param
    username = os.environ.get("DOCKER_USERNAME", "cristobal23")
    image_name = f"{username}/alpine:{docker_tag}"

    # Build Docker image with the given tag
    subprocess.check_call(
        [
            "docker",
            "build",
            "-f",
            "Dockerfile",
            "-t",
            image_name,
            "--build-arg",
            f"TAG={docker_tag}",
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

    # Provide testinfra connection
    host = testinfra.get_host(f"docker://{docker_id}")
    yield host, docker_tag

    # Cleanup after tests
    subprocess.check_call(["docker", "rm", "-f", docker_id])


def test_alpine_version(host):
    """Ensure the container reports the expected Alpine version."""
    h, docker_tag = host
    release = h.check_output("cat /etc/alpine-release").strip()

    # Basic version consistency check
    assert release.startswith(docker_tag), f"Expected {docker_tag}, got {release}"

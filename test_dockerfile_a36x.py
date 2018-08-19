import pytest
import subprocess
import testinfra


@pytest.fixture(scope='session')
def host(request):
    """Build Docker containers with Testinfra by overloading the host fixture."""
    # build local ./Dockerfile
    subprocess.check_call(
        [
            'docker',
            'build',
            '-f',
            'Dockerfile',
            '-t',
            'cristobal23/alpine:3.6',
            '--build-arg',
            'TAG=3.6',
            '.',
        ]
    )

    # run a container
    docker_id = (
        subprocess.check_output(
            ['docker', 'run', '-d', 'cristobal23/alpine:3.6', 'tail', '-f', '/dev/null']
        )
        .decode()
        .strip()
    )

    # return a testinfra connection to the container
    yield testinfra.get_host("docker://" + docker_id)

    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


def test_myimage(host):
    """Test the built Docker container."""
    # 'host' now binds to the container
    assert host.check_output('cat /etc/alpine-release') == '3.6.2'

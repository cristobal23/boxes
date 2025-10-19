import os
import pytest
import subprocess
import testinfra


DOCKER_TAG = '3.8'


@pytest.fixture(scope='session')
def host(request):
    """Build Docker containers with Testinfra by overloading the host fixture."""
    username = os.environ['DOCKER_USERNAME']
    image_name = username + '/alpine:' + DOCKER_TAG

    # build local ./Dockerfile
    subprocess.check_call(
        [
            'docker',
            'build',
            '-f',
            'Dockerfile',
            '-t',
            image_name,
            '--build-arg',
            'TAG=' + DOCKER_TAG,
            '.',
        ]
    )

    # run a container
    docker_id = (
        subprocess.check_output(
            ['docker', 'run', '-d', image_name, 'tail', '-f', '/dev/null']
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
    assert host.check_output('cat /etc/alpine-release') == '3.8.5'

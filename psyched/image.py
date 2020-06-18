import os

import docker


class Image(object):
    """Class representing a Docker Image."""

    def __init__(self, name: str, tag: str):
        """Class constructor.

        :param name: image name
        :type name: str
        :param tag: image tag
        :type tag: str
        """
        self.client = docker.from_env()
        self.name = name
        self.tag = tag
        self.volumes = {}
        return

    def add_volume(self, host_path: str, containter_path: str,
                   mode: str = 'rw'):
        """Add volume to containers created from this image.

        :param host_path: path of the directory in the host
        :type host_path: str
        :param containter_path: path of the directory in the container
        :type containter_path: str
        :param mode: either 'ro' (read-only) or 'rw' (read-write), defaults to 'rw'
        :type mode: str, optional
        """
        host_path = os.path.abspath(host_path)
        self.volumes[host_path] = {'bind': containter_path, 'mode': mode}
        return

    def run_command(self, command: str) -> docker.models.containers.Container:
        """Run command in a detached container.

        :param command: command to run
        :type command: str
        :return: running container
        :rtype: docker.models.containers.Container
        """
        container = self.client.containers.run(
            f'{self.name}:{self.tag}',
            command,
            detach=True,
            volumes=self.volumes,
            stderr=True
        )
        return container

    def __str__(self) -> str:
        return f'Image<{self.name}:{self.tag}>'

    def __del__(self):
        self.client.close()

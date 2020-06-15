import os

import docker


class Image(object):
    def __init__(self, name: str, tag: str):
        self.client = docker.from_env()
        self.name = name
        self.tag = tag
        self.volumes = {}
        return

    def add_volume(self, host_path: str, containter_path: str,
                   mode: str = 'rw'):
        host_path = os.path.abspath(host_path)
        self.volumes[host_path] = {'bind': containter_path, 'mode': mode}
        return

    def run_command(self, command: str) -> docker.models.containers.Container:
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

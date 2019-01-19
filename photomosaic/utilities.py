import os
import time
import subprocess


def get_timestamp():
    return str(time.time()).replace('.', '')


def get_absolute_fp_list(directory):
    return [os.path.join(directory, fp) for fp in os.listdir(directory)]


def get_unique_fp(extension='jpg'):
    return f'mosaic_{get_timestamp()}.{extension}'


class SimpleQueue:
    def __init__(self, max_length=0):
        self.queue = []
        self.max_length = max_length

    def __bool__(self):
        return bool(self.queue)

    def __contains__(self, item):
        return item in self.queue

    def put(self, item):
        self.queue.insert(0, item)
        self.queue = self.queue[0: self.max_length]

    def pop(self):
        if not self:
            return None
        return self.queue.pop()


def create_gif_from_directory(directory, output_file=None, delay=5):
    output_file = output_file if output_file else get_unique_fp('gif')
    cmd = f'gifsicle -d {int(delay)} --loop=0 --optimize -O3 {directory}/* > {output_file}'
    subprocess.run(cmd, shell=True)


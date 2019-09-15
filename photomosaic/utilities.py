import os
import time
from PIL import Image


def generate_filename(basename=None, file_type=None):
    basename = basename or os.getcwd()
    file_type = file_type or 'png'
    return os.path.join(basename, f'{str(time.time()).replace(".", "")}.{file_type}')


def resize_image(image, target_size):
    if target_size == image.size:
        return image
    return image.resize(target_size, Image.ANTIALIAS)


def scale_image(image, scale):
    if scale <= 0:
        raise ValueError('Scaling factor must be non-zero')
    return resize_image(image, tuple(dimension * scale for dimension in image.size))


def crop_largest_square(image):
    width, height = image.size
    minimum_dim = min(image.size)
    width_crop = (width - minimum_dim)
    height_crop = (height - minimum_dim)
    # - width_crop // 2 + width_crop != width_crop // 2 when with_crop is odd
    return image.crop((
        width_crop // 2,
        height_crop // 2,
        (width - width_crop) + (width_crop // 2),
        (height - height_crop) + (height_crop // 2)
    ))


def crop_image(image, tile_size):
    width, height = image.size
    width_crop, height_crop = (dim % tile_size for dim in image.size)
    if not any((width_crop, height_crop)):
        return image
    return image.crop((
        width_crop // 2,
        height_crop // 2,
        (width - width_crop) + (width_crop // 2),
        (height - height_crop) + (height_crop // 2)
    ))


def find_path(path, path_type=None, top=None):
    """
    Finds a file somewhere in directory tree
    :param path: The file path to look for
    :param top: top directory to search from if none is provided it default to the working directory
    :param path_type: file or directory (str)
    :return: absolute path to file
    :exception: Raises FileNotFoundError if unable to locate file
    """
    path_type = path_type or 'file'
    check_method = {
        'file': os.path.isfile,
        'dir': os.path.isdir,
    }.get(path_type.lower(), os.path.isfile)
    if check_method(path):
        # first check if this is an absolute path
        return os.path.abspath(path)

    top = top if top is not None else os.getcwd()
    for root, dirs, files in os.walk(top, topdown=True):
        search_list = dirs if path_type == 'dir' else files
        for file in search_list:
            candidate = os.path.abspath(os.path.join(root, file))
            if candidate.endswith(path) and check_method(candidate):
                return os.path.abspath(candidate)
    raise FileNotFoundError(f'No {path_type} {path} found below {top}')


def find_file(path, top=None):
    return find_path(path, path_type='file', top=top)


def find_dir(path, top=None):
    return find_path(path, path_type='dir', top=top)


def absolute_listdir(path):
    path = find_dir(path)
    return [os.path.join(path, fp) for fp in os.listdir(path)]


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

import time
import os
import numpy as np
from PIL import Image

from photo_mosaic.image_splitter import ImageSplitter
from photo_mosaic.tile_processor import TileProcessor
from photo_mosaic import matrix_math



def get_unique_fp():
    return 'mosaic_{}.jpg'.format(int(time.time() * 1000))


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


class PhotoMosaic(object):
    MAX_SIZE = 4000
    MAX_GIF_SIZE = 1080
    DEFAULT_TILE_DIRECTORY = '../tile_directories/characters'
    """
    Class that builds the photo-mosaic
    """
    def __init__(self, img, tile_directory=None, enlargement=1, tile_size=8,
                 output_file=None, img_type='L', intermediate_frames=50,
                 save_intermediates=False, max_repeats=0, method='euclid'):
        img = self.set_img(img, enlargement).convert(img_type)
        tile_directory = tile_directory if tile_directory is not None else self.DEFAULT_TILE_DIRECTORY
        self.save_intermediates = save_intermediates
        self.intermediate_frames = intermediate_frames
        self.image_data = ImageSplitter(img, tile_size)
        self.tile_data = TileProcessor(tile_directory, tile_size, img_type)
        self.output_file = output_file
        self.max_repeats = max_repeats
        self.method = method

    def set_img(self, img, enlargement):
        h, w = (enlargement * dim for dim in img.size)
        if any(dim > self.MAX_SIZE for dim in (h, w)):
            enlargement = int(self.MAX_SIZE / (max(h, w)) * enlargement)
            h, w = (enlargement * dim for dim in img.size)
        return img.resize((h, w), Image.ANTIALIAS)

    def get_tile_order(self):
        images = self.image_data.get_data()
        tiles = np.asarray(self.tile_data.tile_list, dtype=np.int32)
        tile_shape = len(images.shape)
        diff_method = matrix_math.diff2dlist if tile_shape == 3 else matrix_math.diff3dlist
        output = np.zeros((images.shape[0], tiles.shape[0]), dtype=np.int32)
        out_idxs = np.zeros((images.shape[0]), dtype=np.int32)
        res = diff_method(images, tiles, output)
        out = matrix_math.get_order(res, out_idxs)
        return list(out)

    def replace_tiles(self):
        if self.save_intermediates:
            self.image_data.hilbertize()
        tile_order = self.get_tile_order()
        for img_idx, tile_idx in enumerate(tile_order):
            self.image_data.tile_list[img_idx] = self.tile_data.tile_list[tile_idx]
        self.image_data.stitch_image()

    def save(self, output_file=None):
        output_file = output_file if output_file is not None else self.output_file
        self.image_data.img.save(output_file)

    def get_image(self):
        return self.image_data.img
"""
python
from photomosaic import *
img = Image.open('chuck.jpg')
foo = PhotoMosaic(img)
foo.replace_tiles()
"""
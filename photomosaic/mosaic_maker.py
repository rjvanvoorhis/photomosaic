import os
import shutil
import numpy as np
from PIL import Image

from photomosaic.image_splitter import ImageSplitter
from photomosaic.tile_processor import TileProcessor
from photomosaic import matrix_math, MAX_IMAGE_DIMENSION, MAX_GIF_DIMENSION, DEFAULT_TILE_DIRECTORY
from photomosaic.utilities import get_unique_fp, get_timestamp, create_gif_from_directory


class MosaicMaker(object):
    MAX_SIZE = MAX_IMAGE_DIMENSION
    MAX_GIF_SIZE = MAX_GIF_DIMENSION
    DEFAULT_TILE_DIRECTORY = DEFAULT_TILE_DIRECTORY
    """
    Class that builds the photo-mosaic
    """
    def __init__(self, img, tile_directory=None, enlargement=1, tile_size=8,
                 output_file=None, img_type='L', intermediate_frames=50,
                 save_intermediates=False, max_repeats=0, method='euclid', optimize=True):
        img = self.set_img(img, enlargement).convert(img_type)
        tile_directory = tile_directory if tile_directory is not None else self.DEFAULT_TILE_DIRECTORY
        output_file = output_file if output_file is not None else get_unique_fp()
        self.save_intermediates = save_intermediates
        self.intermediate_frames = intermediate_frames
        self.image_data = ImageSplitter(img, tile_size)
        self.tile_data = TileProcessor(tile_directory, tile_size, img_type)
        self.output_file = output_file
        self.max_repeats = max_repeats
        self.method = method
        self.replace_tiles(optimize=optimize)

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

    def setup_intermediates(self):
        frame_directory = get_timestamp()
        os.mkdir(frame_directory)
        self.image_data.hilbertize()
        return frame_directory

    def create_gif_from_progress(self, optimize=True):
        frame_directory = self.setup_intermediates()
        tile_order = self.get_tile_order()
        total = len(tile_order)
        save_on = max(total // max(self.intermediate_frames, 1), 1)
        for img_idx, tile_idx in enumerate(tile_order):
            self.image_data.tile_list[img_idx] = self.tile_data.tile_list[tile_idx]
            if img_idx % save_on == 0 or img_idx == (total - 1):
                temp_order = self.image_data.tile_list
                thumbnail = self.image_data.get_thumbnail(self.MAX_GIF_SIZE)
                thumbnail.save(os.path.join(frame_directory, f'Mosaic_frame_{img_idx:012d}.gif'))
                self.image_data.tile_list = temp_order
        self.image_data.stitch_image()
        create_gif_from_directory(frame_directory, delay=10, optimize=optimize)
        shutil.rmtree(frame_directory)

    def replace_tiles_no_gif(self):
        tile_order = self.get_tile_order()
        for img_idx, tile_idx in enumerate(tile_order):
            self.image_data.tile_list[img_idx] = self.tile_data.tile_list[tile_idx]
        self.image_data.stitch_image()

    def replace_tiles(self, save_intermediates=None, optimize=True):
        save_intermediates = save_intermediates if save_intermediates is not None else self.save_intermediates
        if save_intermediates:
            self.create_gif_from_progress(optimize=optimize)
        else:
            self.replace_tiles_no_gif()

    def save(self, output_file=None, max_size=None):
        img = self.image_data.img
        if max_size is not None and max_size < max(img.size):
            img = img.copy()
            img.thumbnail((max_size, max_size), Image.ANTIALIAS)
        output_file = output_file if output_file is not None else self.output_file
        img.save(output_file)

    def get_image(self):
        return self.image_data.img

"""
python
from PIL import Image
from photomosaic.mosaic_maker import MosaicMaker
img = Image.open('chuck.jpg')
foo = MosaicMaker(img, save_intermediates=True)
"""
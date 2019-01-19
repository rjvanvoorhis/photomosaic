import os
import shutil
import numpy as np
from PIL import Image

from photomosaic.image_splitter import ImageSplitter
from photomosaic.tile_processor import TileProcessor
from photomosaic import matrix_math
from photomosaic.utilities import get_unique_fp, get_timestamp, create_gif_from_directory


class MosaicMaker(object):
    MAX_SIZE = 4000
    MAX_GIF_SIZE = 1080
    DEFAULT_TILE_DIRECTORY = f'{os.path.dirname(__file__)}/../tile_directories/characters'
    """
    Class that builds the photo-mosaic
    """
    def __init__(self, img, tile_directory=None, enlargement=1, tile_size=8,
                 output_file=None, img_type='L', intermediate_frames=50,
                 save_intermediates=False, max_repeats=0, method='euclid'):
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
        self.replace_tiles()

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

    def create_gif_from_progress(self, tile_order):
        total = len(tile_order)
        frame_directory = self.setup_intermediates()
        save_on = max(total // max(self.intermediate_frames, 1), 1)
        for img_idx, tile_idx in enumerate(tile_order):
            self.image_data.tile_list[img_idx] = self.tile_data.tile_list[tile_idx]
            if img_idx % save_on == 0 or img_idx == (total - 1):
                self.image_data.stitch_image()
                self.save(os.path.join(frame_directory, f'Mosaic_frame_{img_idx:04d}.jpg'))
        self.image_data.stitch_image()
        create_gif_from_directory(frame_directory)
        shutil.rmtree(frame_directory)

    def replace_tiles_no_gif(self, tile_order):
        for img_idx, tile_idx in enumerate(tile_order):
            self.image_data.tile_list[img_idx] = self.tile_data.tile_list[tile_idx]
        self.image_data.stitch_image()

    def replace_tiles(self, save_intermediates=None):
        save_intermediates = save_intermediates if save_intermediates is not None else self.save_intermediates
        tile_order = self.get_tile_order()
        if save_intermediates:
            self.create_gif_from_progress(tile_order)
        else:
            self.replace_tiles_no_gif(tile_order)

    def save(self, output_file=None):
        output_file = output_file if output_file is not None else self.output_file
        self.image_data.img.save(output_file)

    def get_image(self):
        return self.image_data.img

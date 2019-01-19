import numpy as np

from PIL import Image
from photomosaic.utilities import get_absolute_fp_list


class TileProcessor(object):
    DEFAULT_DIRECTORY = f'{__file__}/../tile_directories/characters'

    def __init__(self, tile_directory=None, tile_size=8, img_type='L'):
        self.tile_directory = tile_directory if tile_directory is not None else self.DEFAULT_DIRECTORY
        self.tile_size = tile_size
        self.img_type = img_type
        self.tile_list = self.get_tiles(tile_directory)

    @staticmethod
    def crop_image(img):
        w, h = img.size
        min_dim = min(w, h)
        w_crop = w - min_dim
        h_crop = h - min_dim
        crop_rect = (w_crop//2, h_crop//2, w - w_crop + w_crop//2, h - h_crop + h_crop//2)
        return img.crop(crop_rect)

    @staticmethod
    def resize_image(img, tile_size):
        return img.resize((tile_size, tile_size), Image.ANTIALIAS)

    def process_image(self, fp):
        img = Image.open(fp)
        img = self.crop_image(img)
        img = self.resize_image(img, self.tile_size)
        return np.asarray(img.convert(self.img_type))

    def get_tiles(self, tile_directory=None):
        tile_directory = tile_directory if tile_directory is not None else self.tile_directory
        fp_list = get_absolute_fp_list(tile_directory)
        return [self.process_image(fp) for fp in fp_list]



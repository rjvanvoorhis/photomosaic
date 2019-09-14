import os
import numpy as np
from PIL import Image
from photomosaic import utilities


class TileProcessor:
    DEFAULT_DIRECTORY = os.path.abspath(os.path.join(__file__, '../character_directory'))

    def __init__(self, tile_directory=None, tile_size=8, image_type='L'):
        tile_directory = tile_directory or self.DEFAULT_DIRECTORY
        self.tile_directory = utilities.find_dir(tile_directory)
        self.image_type = image_type
        self.tile_size = tile_size
        self.tile_list = self.process_tiles()

    def _process_tile(self, path):
        with Image.open(path) as image:
            image = utilities.crop_largest_square(image)
            image = utilities.resize_image(image, (self.tile_size, self.tile_size))
            data = np.asarray(image.convert(self.image_type))
        return data

    def process_tiles(self):
        return [self._process_tile(path) for path in utilities.absolute_listdir(self.tile_directory)]

    @property
    def tile_data(self):
        return np.asarray(self.tile_list, dtype=np.int32)

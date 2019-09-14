import numpy as np
from PIL import Image
from photomosaic import utilities


class ImageSplitter:
    MAX_SIZE = 4000

    @staticmethod
    def image_to_blocks(image, tile_size):
        data = np.asarray(image)
        rows = data.shape[0] // tile_size
        cols = data.shape[1] // tile_size
        matrix = [np.split(row, cols, axis=1) for row in np.split(data, rows)]
        return np.asarray([col for row in matrix for col in row])

    @staticmethod
    def blocks_to_image(data, rows):
        data = np.asarray(data) if isinstance(data, list) else data
        pix_map = np.concatenate([np.concatenate(row, axis=1) for row in np.split(data, rows)])
        return Image.fromarray(pix_map)

    def __init__(self, image, tile_size=8, image_type='L'):
        self._format = image.format
        image = image.convert(image_type)
        if not int(tile_size) > 0:
            raise ValueError('tile_size must be a non zero integer')
        self.tile_size = int(tile_size)
        image = utilities.crop_image(image, self.tile_size)
        self.cols = image.size[0] // tile_size
        self.rows = image.size[1] // tile_size
        self.tile_list = self.image_to_blocks(image, self.tile_size)

    @property
    def format(self):
        image_format = self._format if self._format else 'png'
        return 'jpg' if image_format == 'JPEG' else image_format

    @property
    def image(self):
        return self.blocks_to_image(self.tile_list, self.rows)

    @property
    def tile_matrix(self):
        return np.asarray([
            [self.tile_list[(self.cols * row) + index] for index in range(self.cols)]
            for row in range(self.rows)
        ])

    @property
    def tile_data(self):
        return np.asarray([tile for tile in self.tile_list], dtype=np.int32)

    def save(self, output_file=None):
        image = self.image
        output_file = utilities.generate_filename(file_type=self.format) if output_file is None else output_file
        if any(dim > self.MAX_SIZE for dim in image.size):
            image = image.copy()
            image.thumbnail((self.MAX_SIZE, self.MAX_SIZE), Image.ANTIALIAS)
        image.save(output_file)

    @classmethod
    def load(cls, filename, tile_size=8, image_type='L', scale=1):
        with Image.open(filename) as image:
            image.format = filename.split('.')[-1] if not image.format else image.format
            splitter = cls(utilities.scale_image(image, scale=scale), tile_size, image_type)
        return splitter

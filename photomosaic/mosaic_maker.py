import numpy as np
from photomosaic import matrix_math
from photomosaic import utilities


def euclid(image_splitter, tile_processor):
    """
    The default tile order function
    Takes a image_splitter and a tile_processor as input and returns the sorted order
    :return: list of indexes of tile indexes to replace in image splitter
    """
    image_data = image_splitter.tile_data
    tile_data = tile_processor.tile_data
    comparison_method = matrix_math.diff2dlist if len(image_data.shape) == 3 else matrix_math.diff3dlist
    return list(
        matrix_math.get_order(
            comparison_method(
                image_data,
                tile_data,
                np.zeros((image_data.shape[0], tile_data.shape[0]), dtype=np.int32)  # comparison buffer
            ),
            np.zeros((image_data.shape[0]), dtype=np.int32)  # buffer of list of tile indexes
        )
    )


class MosaicMaker:

    def __init__(self, image_splitter, tile_processor, method=None, output_file=None, context=None):
        self.context = context or {'frame_number': 1, 'total_frames': 1}
        self.image_splitter = image_splitter
        self.tile_processor = tile_processor
        self.method = method or euclid
        self.output_file = output_file or utilities.generate_filename(file_type=image_splitter.format)

    def save(self, output_file=None):
        output_file = output_file or self.output_file
        self.image_splitter.save(output_file)
        return self

    def process(self):
        for image_index, tile_index in enumerate(self.method(self.image_splitter, self.tile_processor)):
            self.image_splitter.tile_list[image_index] = self.tile_processor.tile_list[tile_index]
        return self

    @property
    def image(self):
        return self.image_splitter.image

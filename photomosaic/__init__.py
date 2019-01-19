__all__ = ['__version__', 'gif_splitter', 'image_splitter', 'mosaic_maker', 'utilities',
           'progress_bar', 'tile_processor', 'matrix_math', 'DEFAULT_TILE_DIRECTORY',
           'MAX_GIF_DIMENSION', 'MAX_IMAGE_DIMENSION']
import os
DEFAULT_TILE_DIRECTORY = f'{os.path.dirname(__file__)}/../tile_directories/characters'
MAX_GIF_DIMENSION = 2160
MAX_IMAGE_DIMENSION = 3128
import photomosaic.gif_splitter
import photomosaic.image_splitter
import photomosaic.mosaic_maker
import photomosaic.progress_bar
import photomosaic.tile_processor
import photomosaic.utilities
import photomosaic.matrix_math
from version_info import __version__

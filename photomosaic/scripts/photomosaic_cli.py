__all__ = ['create_photomosaic', 'create_frame', 'create_gif', 'main']

from PIL import Image
from photomosaic.gif_splitter import GifSplitter
from photomosaic.mosaic_maker import MosaicMaker
from photomosaic import DEFAULT_TILE_DIRECTORY
import click


def create_photomosaic(input_file, enlargement=1, tile_size=8, tile_directory=DEFAULT_TILE_DIRECTORY,
                       optimize=True, output_file=None, progress_callback=None, save_intermediates=False,
                       img_type='L'):
    if input_file.lower().endswith('gif'):
        create_gif(input_file, enlargement, tile_size, tile_directory,
                   optimize, output_file, progress_callback, img_type)
    else:
        create_frame(input_file, enlargement, tile_size, tile_directory,
                     optimize, output_file, save_intermediates, img_type)


def create_gif(input_file, enlargement=1, tile_size=8, tile_directory=DEFAULT_TILE_DIRECTORY,
               optimize=True, output_file=None, progress_callback=None, img_type='L'):
    mosaic = GifSplitter(fp=input_file)
    mosaic.to_photomosaic(tile_directory=tile_directory, tile_size=tile_size, enlargement=enlargement,
                          optimize=optimize, output_file=output_file, progress_callback=progress_callback,
                          img_type=img_type)
    pass


def create_frame(input_file, enlargement=1, tile_size=8, tile_directory=DEFAULT_TILE_DIRECTORY,
               optimize=True, output_file=None, save_intermediates=False, img_type='L'):
    img = Image.open(input_file)
    mosaic = MosaicMaker(img, tile_directory=tile_directory, enlargement=enlargement, tile_size=tile_size,
                         output_file=output_file, img_type=img_type, save_intermediates=save_intermediates,
                         optimize=optimize)
    mosaic.save()


@click.command()
@click.option('--input_file', help='File to be converted')
@click.option('--output_file', default=None, help='New name for file')
@click.option('--enlargement', type=int, default=1, help='How large to make the mosaic, memory limits will limit this')
@click.option('--tile_size', type=int, default=8, help='Dimension in pixels to make each tile of the mosaic')
@click.option('--tile_directory', default=DEFAULT_TILE_DIRECTORY, help='path to the tile directory to use')
@click.option('--optimize/--no-optimize', default=True, help='Setting this to false will produce uncompressed gifs')
@click.option('--save_intermediates/--no-save-intermediates', default=True, help='Will make a progress gif')
@click.option('--img_type', default='L', help='Type of image to convert (L for greyscale RGB for color)')
def main(input_file, output_file, enlargement, tile_size, tile_directory, optimize,
         save_intermediates, img_type):
    create_photomosaic(input_file, enlargement, tile_size, tile_directory, optimize,
                       output_file, None, save_intermediates, img_type)


if __name__ == '__main__':
    main()

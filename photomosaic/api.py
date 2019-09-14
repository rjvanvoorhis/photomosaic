__all__ = ['mosaicfy', 'is_animated']
import sys
import os
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from enlighten import get_manager as _get_manager
from photomosaic import gif_splitter, image_splitter, tile_processor, mosaic_maker, utilities


LOGGER = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def get_manager():
    enable_counter = os.environ.get('DISABLE_COUNTER', 'FALSE').upper() not in('1', 'TRUE')
    return _get_manager(stream=sys.stdout, enabled=enable_counter)


def is_animated(fp):
    splitter = gif_splitter.GifSplitter(fp)
    return splitter.info.get('frames', 1) > 1


def _image_to_mosaic(filename, tile_size=8, **kwargs):
    callback = kwargs.get('callback', lambda x: x)
    splitter = image_splitter.ImageSplitter.load(
        filename,
        tile_size,
        scale=kwargs.get('scale', 1),
        image_type=kwargs.get('image_type', 'L')
    )
    tile_proc = kwargs.get('tile_processor') or tile_processor.TileProcessor(
        tile_directory=kwargs.get('tile_directory'),
        image_type=kwargs.get('image_type', 'L'),
        tile_size=tile_size
    )
    maker = mosaic_maker.MosaicMaker(
        image_splitter=splitter,
        tile_processor=tile_proc,
        context=kwargs.get('context')
    ).process().save(output_file=kwargs.get('output_file'))
    return callback(maker)


def _convert_frames(tile_proc, frame_directory, **kwargs):
    frames = utilities.absolute_listdir(frame_directory)
    with get_manager().counter(
        total=len(frames),
        desc='Converting frames synchronously',
        unit='frames'
    ) as progress_bar:
        for frame in progress_bar(frames):
            _image_to_mosaic(
                frame,
                tile_size=kwargs.get('tile_size', 8),
                tile_processor=tile_proc,
                scale=kwargs.get('scale', 1),
                image_type=kwargs.get('image_type', 'L'),
                output_file=frame,
                callback=kwargs.get('callback', lambda x: x)
            )


def _convert_frames_async(tile_proc, frame_directory, **kwargs):
    frames = utilities.absolute_listdir(frame_directory)
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(
            _image_to_mosaic,
            frame,
            tile_size=kwargs.get('tile_size', 8),
            tile_processor=tile_proc,
            scale=kwargs.get('scale', 1),
            image_type=kwargs.get('image_type', 'L'),
            output_file=frame,
            context={'frame_number': frame_index, 'total_frames': len(frames)}
            # callback=kwargs.get('callback', lambda x: x)
        ) for frame_index, frame in enumerate(frames)]
        with get_manager().counter(
                total=len(futures),
                desc='Converting frames asynchronously',
                unit='frames'
        ) as progress_bar:
            for future in progress_bar(futures):
                kwargs.get('callback', lambda x: x)(future.result())


def _make_mosaic_name(filename):
    base_name = f'mosaic_of_{os.path.basename(filename)}'
    return os.path.join(os.path.dirname(filename), base_name)


def _gif_to_mosaic(filename, tile_size=8, asynchronous=True, **kwargs):
    frame_directory = kwargs.get('frame_directory', f'{time.time()}'.replace('.', ''))
    splitter = gif_splitter.GifSplitter(
        filename,
        frame_directory=frame_directory
    ).split_gif()
    tile_proc = tile_processor.TileProcessor(
        tile_directory=kwargs.get('tile_directory'),
        image_type=kwargs.get('image_type', 'L'),
        tile_size=tile_size
    )
    frame_converter = _convert_frames_async if asynchronous else _convert_frames
    frame_converter(
        tile_proc,
        frame_directory,
        **kwargs
    )
    return gif_splitter.GifStitcher(
        frame_directory,
        splitter.info,
        gif_path=kwargs.get('gif_path', _make_mosaic_name(filename))
    ).stitch_gif()


def mosaicfy(filename, tile_size=8, **kwargs):
    method = _gif_to_mosaic if is_animated(filename) else _image_to_mosaic
    LOGGER.info(f'Using method {method}')
    return method(filename, tile_size=tile_size, **kwargs)




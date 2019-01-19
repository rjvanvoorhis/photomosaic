import subprocess
import os
import shutil
from PIL import Image
from photomosaic.mosaic_maker import MosaicMaker
from photomosaic.progress_bar import parallel_process
from photomosaic.utilities import get_timestamp
import functools
from photomosaic.utilities import create_gif_from_directory
from photomosaic import DEFAULT_TILE_DIRECTORY, MAX_GIF_DIMENSION


class GifSplitter(object):
    DELAY_RANGE = range(3, 15)

    def __init__(self, fp):
        img = Image.open(fp)
        self.duration = img.info.get('duration')
        self.delay = 5
        self.original_file = fp
        self.frame_directory = f'{get_timestamp()}_frames_dir'

    def split_gif(self):
        if not os.path.exists(self.frame_directory):
            os.mkdir(self.frame_directory)
        cmd1 = f'gifsicle --explode --unoptimize -O2 {self.original_file} ' \
               f'-o {self.frame_directory}/{self.original_file}_frames'
        subprocess.run(cmd1.split())
        frames = len(os.listdir(self.frame_directory))
        self.set_delay(frames)

    def set_delay(self, total_frames, duration=None):
        duration = duration if duration else self.duration
        if not duration:
            self.delay = 5
            return
        try:
            if duration / 10 in self.DELAY_RANGE:
                self.delay = duration/ 10
            elif duration / total_frames in self.DELAY_RANGE:
                self.delay = duration / total_frames
            elif duration in self.DELAY_RANGE:
                self.delay = duration
            else:
                self.delay = 5
        except Exception:
            self.delay = 5

    def to_photomosaic(self, tile_directory=DEFAULT_TILE_DIRECTORY, output_file=None, tile_size=8,
                       enlargement=1, progress_callback=None, optimize=True, img_type='L'):
        frame_directory = get_timestamp()
        output_file = output_file if output_file else f'Mosaic_of_{self.original_file}'
        if not os.path.exists(frame_directory):
            os.mkdir(frame_directory)
        if not os.path.exists(self.frame_directory):
            self.split_gif()

        progress = parallel_process(functools.partial(self.make_mosaic_frame, tile_directory=tile_directory,
                                                      frame_directory=frame_directory, tile_size=tile_size,
                                                      enlargement=enlargement, optimize=optimize, img_type=img_type),
                                    sorted(os.listdir(self.frame_directory)), desc='Processing Frames')
        for idx, item in progress:
            if progress_callback is not None:
                progress_callback(idx, item)
        self.stitch_gif(frame_directory, output_file, optimize=optimize)
        return frame_directory, output_file

    def asciify(self, output_file=None, tile_size=8, enlargement=1, progress_callback=None, optimize=True):
        return self.to_photomosaic(output_file=output_file, tile_size=tile_size, enlargement=enlargement,
                                   progress_callback=progress_callback, optimize=optimize)

    def stitch_gif(self, frame_directory=None, output_file=None, optimize=True):
        frame_directory = frame_directory if frame_directory else self.frame_directory
        output_file = output_file if output_file else f'{get_timestamp()}.gif'
        # cmd = f'gifsicle -d {int(self.delay)} --loop=0 --optimize -O3 {frame_directory}/* > {output_file}'
        # subprocess.run(cmd, shell=True)
        create_gif_from_directory(frame_directory, output_file=output_file,
                                  delay=int(self.delay), optimize=optimize)
        for directory in [frame_directory, self.frame_directory]:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def make_mosaic_frame(self, fp, tile_directory, frame_directory, tile_size, enlargement, optimize, img_type):
        cleaned_fp = f'{fp.replace(".", "_")}.gif'
        img = Image.open(os.path.join(self.frame_directory, fp))
        mosaic = MosaicMaker(img, tile_directory=tile_directory, img_type=img_type,
                             save_intermediates=False, tile_size=tile_size, enlargement=enlargement,
                             output_file=os.path.join(frame_directory, cleaned_fp))
        if optimize:
            mosaic.save()
        else:
            mosaic.save(max_size=MAX_GIF_DIMENSION)
        return mosaic


"""
python
from photomosaic.gif_splitter import *
foo = GifSplitter('ships.gif')
foo.asciify(enlargement=6)
"""

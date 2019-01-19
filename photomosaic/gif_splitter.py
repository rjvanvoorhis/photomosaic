import time
import subprocess
import os
import shutil
from PIL import Image
from photomosaic.mosaic_maker import MosaicMaker
from photomosaic.progress_bar import parallel_process
import functools
TILE_DIRECTORY = f'{os.path.dirname(__file__)}/../tile_directories/characters'


def get_timestamp():
    return str(time.time()).replace('.', '')


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
        cmd1 = f'gifsicle --explode --unoptimize -O3 {self.original_file} -o {self.frame_directory}/{self.original_file}_frames'
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

    def asciify(self, output_file=None, tile_size=8, enlargement=1, progress_callback=None):
        frame_directory = get_timestamp()
        output_file = output_file if output_file else f'Mosaic_of_{self.original_file}'
        if not os.path.exists(frame_directory):
            os.mkdir(frame_directory)
        if not os.path.exists(self.frame_directory):
            self.split_gif()

        progress = parallel_process(functools.partial(self.make_mosaic_frame, frame_directory=frame_directory,
                                                      tile_size=tile_size, enlargement=enlargement),
                                    sorted(os.listdir(self.frame_directory)), desc='Processing Frames')
        for idx, item in progress:
            if progress_callback is not None:
                progress_callback(idx, item)
        self.stitch_gif(frame_directory, output_file)
        return frame_directory, output_file

    def stitch_gif(self, frame_directory=None, output_file=None):
        frame_directory = frame_directory if frame_directory else self.frame_directory
        output_file = output_file if output_file else f'{get_timestamp()}.gif'
        cmd = f'gifsicle -d {int(self.delay)} --loop=0 --optimize -O3 {frame_directory}/* > {output_file}'
        subprocess.run(cmd, shell=True)
        for directory in [frame_directory, self.frame_directory]:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def make_mosaic_frame(self, fp, frame_directory, tile_size, enlargement):
        cleaned_fp = f'{fp.replace(".", "_")}.gif'
        img = Image.open(os.path.join(self.frame_directory, fp))
        mosaic = MosaicMaker(img, tile_directory=TILE_DIRECTORY, img_type='L',
                             save_intermediates=False, tile_size=tile_size, enlargement=enlargement,
                             output_file=os.path.join(frame_directory, cleaned_fp))
        mosaic.save()
        return mosaic


"""
python
from gif_splitter import *
foo = GifSplitter('ships.gif')
foo.asciify()
"""

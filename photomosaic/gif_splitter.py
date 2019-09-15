import os
import subprocess
import shutil
import time
import itertools
from PIL import Image
from photomosaic import utilities, mosaic_maker, tile_processor, image_splitter
GIFSICLE_HELPER = os.path.abspath(f'{__file__}/../gifsicle_helper.sh')


class GifSplitter:
    DEFAULT_DELAY = 5

    def __init__(self, gif_path, frame_directory=None):
        with Image.open(gif_path) as image:
            self.info = image
        self.gif_path = gif_path
        self.frame_directory = frame_directory or f'{int(time.time() * 1000)}_gif_frames'

    @property
    def info(self):
        return self._info or {}

    @info.setter
    def info(self, image):
        image.seek(0)
        self._info = image.info or {}
        duration = 0
        for frames in itertools.count(start=1):
            try:
                info = image.info or {}
                duration += info.get('duration', 0)
                image.seek(frames)
            except EOFError:
                delay = duration / (max(1, frames) * 10)
                self._info.update({'duration': duration, 'frames': frames, 'delay': delay})
                break

    def split_gif(self):
        if not os.path.exists(self.frame_directory):
            os.mkdir(self.frame_directory)
        cmd = f'gifsicle --explode --unoptimize -O2 {self.gif_path} -o {self.frame_directory}/frames'
        subprocess.run(cmd.split())
        self._clean_files(self.frame_directory)
        return self

    def _clean_files(self, path=None):
        path = path or self.frame_directory
        for filename in utilities.absolute_listdir(path):
            dst = f'{filename.replace(".", "_")}.gif'
            os.rename(filename, dst)


class GifStitcher:
    DEFAULT_DELAY = 5

    def __init__(self, frame_directory, image_info=None, gif_path=None):
        self.frame_directory = frame_directory
        self.gif_path = gif_path or utilities.generate_filename(file_type='.gif')
        self.info = image_info

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, image_info):
        if image_info:
            self._info = image_info
        else:
            frames = len(os.listdir(self.frame_directory))
            self._info = {
                'frames': frames,
                'duration': self.DEFAULT_DELAY * frames,
                'delay': self.DEFAULT_DELAY
            }

    @property
    def duration(self):
        return self._info.get('duration')

    @property
    def delay(self):
        return int(self._info.get('delay', self.DEFAULT_DELAY))

    def stitch_gif(self, gif_path=None):
        gif_path = gif_path or self.gif_path
        cmd = f'bash {GIFSICLE_HELPER} {self.delay} {self.frame_directory} {gif_path}'
        subprocess.run(cmd.split())
        shutil.rmtree(self.frame_directory)
        return self


def gif_to_mosaic(fp, scale=1):
    splitter = GifSplitter(fp, 'mosaic_test')
    splitter.split_gif()
    tile_proc = tile_processor.TileProcessor()
    _convert_frames(tile_proc, scale, 'mosaic_test')
    GifStitcher(
        splitter.frame_directory,
        splitter.info,
        gif_path=f'mosaic_of_{fp}'
    ).stitch_gif()


def _convert_frames(tile_proc, scale, frame_dir):
    frame_len = len(utilities.absolute_listdir(frame_dir))
    for idx, frame in enumerate(utilities.absolute_listdir(frame_dir)):
        print(f'frame {idx} of {frame_len}')
        mosaic_maker.MosaicMaker(
            image_splitter.ImageSplitter.load(frame, scale=scale),
            tile_proc,
            output_file=frame
        ).process().save()


if __name__ == '__main__':
    gif_to_mosaic('loading_gif.gif')

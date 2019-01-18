import math

from concurrent.futures import ProcessPoolExecutor


class ProgressBarError(Exception):
    """
    Raise when something goes wrong in ProgressBar
    """
    pass


class ProgressBar(object):
    def __init__(self, iterable, desc=None, start=0, step=1, cols=50, block=u"\u2588", last_index=None):
        self.iterator = iter(iterable)
        self.count = start - 1
        self.description = '' if desc is None else '{} : '.format(desc)
        self.step = step
        self.cols = cols
        self.block = block
        if last_index is None:
            try:
                last_index = len(iterable) + start
                self.last_index = max(last_index, 1)
            except ValueError:
                raise ProgressBarError('Iterable is of type: {type}, last_index argument must be passed to '
                                       'constructor for iterables that do not support len()')
        else:
            self.last_index = last_index
        self.update_coefficient = self.cols / float(self.last_index)
        self.template = '{msg} | {per:>7} | {blocks: <{cols}} |'

    def log_progress(self):
        idx = self.count
        if idx % self.step == 0 or idx == self.last_index:
            blocks = self.block * math.ceil(self.update_coefficient * idx)
            percentage = '{:.2%}'.format(idx / float(self.last_index))
            bar = self.template.format(msg=self.description, per=percentage, blocks=blocks, cols=self.cols)
            print(bar, end='\r')

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = next(self.iterator)
            self.count += 1
            self.log_progress()
        except StopIteration:
            print()
            raise StopIteration
        return self.count, result


def parallel_process(func, *args, max_workers=5, chunksize=1, desc=None):
    with ProcessPoolExecutor(max_workers=max_workers) as exec:
        progress = ProgressBar(
            exec.map(func, *args, chunksize=chunksize), desc=desc,
            last_index=len(args[0]) - 1
        )
        for idx, data in progress:
            yield idx, data
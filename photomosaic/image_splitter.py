import time
import numpy as np
from PIL import Image
import photomosaic.matrix_math


class HilbertList(object):
    def __init__(self, mat):
        start = time.time()
        self.rows = len(mat)
        self.cols = len(mat[0])
        self.n = matrix_math.get_n(self.rows, self.cols)
        self.mat = mat
        self.hilbert_dict = {}
        self.hilbert_indices = {}
        for row_idx, row in enumerate(mat):
            for col_idx, col in enumerate(row):
                d = matrix_math.xy2d(self.n, col_idx, row_idx)
                self.hilbert_dict[(col_idx, row_idx)] = d
        self.set_hilbert_order()
        print(f'Took {time.time() - start} to build HilbertList')

    def __getitem__(self, item):
        if not isinstance(item, int):
            foo = str(type(item))
            raise TypeError('list indicies must be int not %s' % foo)
        try:
            col, row = self.hilbert_indices[item]
        except KeyError:
            raise IndexError
        return self.mat[row][col]

    def __setitem__(self, name, value):
        if isinstance(name, int):
            col, row = self.hilbert_indices[name]
            self.mat[row][col] = value
        else:
            raise TypeError(f'list indicies must be int not {str(type(name))}')

    def __len__(self):
        return len(self.hilbert_dict)

    def set_hilbert_order(self):
        indices = [item[0] for item in sorted(
            self.hilbert_dict.items(), key=lambda x: x[1])]
        self.hilbert_indices = {idx: pair for idx, pair in enumerate(indices)}

    def get_hilbert_order(self):
        indices = [item[0] for item in sorted(
            self.hilbert_dict.items(), key=lambda x: x[1])]
        return [self.mat[row][col] for col, row in indices]

    def get_flat_order(self):
        return np.asarray([col for row in self.mat for col in row])


class ImageSplitter(object):
    def __init__(self, img, tile_size):
        self.img = self.crop_image(img, tile_size)
        self.tile_size = tile_size
        self.cols = img.size[0] // tile_size
        self.rows = img.size[1] // tile_size
        self.tile_list = self.blockshaped(np.asarray(self.img), tile_size)

    def hilbertize(self):
        self.tile_list = HilbertList(self.get_mat(self.tile_list, self.rows))

    def stitch_image(self):
        if isinstance(self.tile_list, HilbertList):
            self.tile_list = self.tile_list.get_flat_order()
        self.img = Image.fromarray(self.unblockshaped(self.tile_list, self.rows))

    @staticmethod
    def crop_image(img, tile_size):
        w, h = img.size
        w_crop = w % tile_size
        h_crop = h % tile_size
        crop_rect = (w_crop//2, h_crop//2, w - w_crop + w_crop//2, h - h_crop + h_crop//2)
        return img.crop(crop_rect)

    @staticmethod
    def blockshaped(arr, tile_size):
        rows = arr.shape[0] // tile_size
        cols = arr.shape[1] // tile_size
        mat = [np.split(row, cols, axis=1) for row in
               np.split(arr, rows)]
        return np.asarray([col for row in mat for col in row])

    @staticmethod
    def unblockshaped(arr, rows):
        if isinstance(arr, list):
            arr = np.asarray(arr)
        row_list = np.split(arr, rows)
        pix_map = np.concatenate([
            np.concatenate(row, axis=1) for row in row_list
        ])
        return pix_map

    @staticmethod
    def get_mat(tile_list, rows):
        cols = len(tile_list)//rows
        return np.asarray([[tile_list[cols * j + i] for i in range(cols)] for j in range(rows)])

    def get_data(self):
        return np.asarray([tile for tile in self.tile_list], dtype=np.int32)

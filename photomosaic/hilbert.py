import sys,math
import numpy as np
from PIL import Image
from pdb import set_trace as bp

def d2xy(n,d):
    t=d
    x,y = (0,0)
    s = 1
    while s< n:
        rx = 1 & (t//2)
        ry = 1 & (t ^ rx)
        x,y = rot(s,x,y,rx,ry)
        x += s * rx
        y += s * ry
        t = t//4
        s *=2
    return (x,y)

def xy2d(n,x,y):
    d = 0
    s = n//2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * (( 3 * rx ) ^ ry)
        x,y = rot(s,x,y,rx,ry)
        s = s//2
    return d

def rot(n,x,y,rx,ry):
    if ry  == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        z = x
        m = y
        x = m
        y = z
    return (x,y)

def get_n(x,y):
    d = max(x,y)
    return 2**(math.ceil(math.log2(d)))

def build_mat(arr,x,y):
    mat = []
    for i in arr:
        if i % x == 0:
            mat.append([])
        mat[-1].append(i)
    return mat

class Image_Stitcher:
    def __init__(self,img_path,tile_size,enlargement=1.0,tile_rescale=1.0,img_type='RGB'):
        self.tile_size = tile_size
        self.enlargement = enlargement
        self.tile_rescale = tile_rescale
        img = Image.open(img_path).convert(img_type)
        w_original,h_original = img.size
        w_large = math.ceil(w_original * self.enlargement)
        h_large = math.ceil(h_original * self.enlargement)
        if w_large %2 == 1:
            w_large-=1
        if h_large %2 == 1:
            h_large-=1
        final_img = img.resize((w_large,h_large),Image.ANTIALIAS)
        w_crop = (w_large % self.tile_size) // 2
        h_crop = (h_large % self.tile_size) // 2
        if (w_crop + h_crop) > 0:
            final_img = final_img.crop((
                w_crop,h_crop,w_large-w_crop,h_large-h_crop))
        w_final,h_final = final_img.size
        self.cols = w_final//self.tile_size
        self.rows = h_final//self.tile_size
        w_small = self.cols * math.ceil(self.tile_size*tile_rescale)
        h_small = self.rows * math.ceil(self.tile_size*tile_rescale)
        small_img = np.array(final_img.resize((w_small,h_small),Image.ANTIALIAS))
        final_img = np.array(final_img)
        self.large_img = Hilbert_List(self.pix_map_to_tile_mat(final_img))
        self.small_img = Hilbert_List(self.pix_map_to_tile_mat(small_img))
        
    def pix_map_to_tile_mat(self,pix_map):
        tiles =  [np.split(row,self.cols,axis=1)
                           for row in np.split(pix_map,self.rows)]
        return tiles
    
    def get_data(self):
        return self.large_img,self.small_img

    def stitch_img(self):
        pix_map = self.large_img.stitch_img()
        return pix_map
    
class Hilbert_List:
    def __init__(self,mat):
        self.rows = len(mat)
        self.cols = len(mat[0])
        self.n = get_n(self.rows,self.cols)
        self.mat = mat
        self.hilbert_dict = {}
        self.hilbert_indicies = {}
        for row_idx,row in enumerate(mat):
            for col_idx,col in enumerate(row):
                d = xy2d(self.n,col_idx,row_idx)
                self.hilbert_dict[(col_idx,row_idx)] = d
        self.set_hilbert_order()
        
    def __getitem__(self,item):
        if not isinstance(item,int):
            foo = str(type(item))
            raise  TypeError ('list indicies must be int not %s'%foo)
        try:
            col,row = self.hilbert_indicies[item]
        except KeyError:
            raise IndexError
        return self.mat[row][col]
    
    def __setitem__(self,name,value):
        if isinstance(name,int):
            col,row = self.hilbert_indicies[name]
            self.mat[row][col] = value
        else:
            foo = str(type(name))
            raise TypeError ('list indicies must be int not %s'%foo)

    def __len__(self):
        return len(self.hilbert_dict)

    def set_hilbert_order(self):
        indicies = [item[0] for item in sorted(
            self.hilbert_dict.items(), key=lambda x:x[1])]
        self.hilbert_indicies = {idx:pair for idx,pair in
                                  enumerate(indicies)}

    def stitch_img(self):
        tile_list = np.array(self.row_col_order())
        row_list = np.split(tile_list,self.rows)
        pix_map = np.concatenate([np.concatenate(row,axis=1)
                                  for row in row_list])
        return pix_map

    def hilbert_order(self):
        indicies = [item[0] for item in sorted(
            self.hilbert_dict.items(),key=lambda x:x[1])]
        return [self.mat[row][col] for col,row in indicies]

    def row_col_order(self):
        return [col for row in self.mat for col in row]

    def print_mat(self):
        print('\n\n'.join('\t'.join('% 6s'%col for col
                                  in row) for row in self.mat))

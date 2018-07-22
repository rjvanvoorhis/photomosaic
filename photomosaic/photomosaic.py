import sys
import os
from PIL import Image
import numpy as np
from pdb import set_trace as bp
import math
import pickle

def chunks(l,n):
    for i in range(0,len(l),n):
        yield l[i:i+n]

def get_default_tile_directory():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname,'tile_directory')

def get_default_character_dictionary():
    dirname = os.path.dirname(__file__)
    fp = os.path.join(dirname,'character_dictionary.pickle')
    with open(fp,'rb') as fn: data = pickle.load(fn)
    return data

def prepend_to_path(path,modifier):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    return os.path.join(dirname,'%s_%s'%(modifier,basename)) 

class Gif_Reader:
    def __init__(self,path,tile_directory=None,enlargement=1,
                 tile_size=16,delay='10',as_text=False,img_type='RGB'):
        self.tile_directory = get_default_tile_directory() if tile_directory is None else tile_directory
        self.image = Image.open(path)
        self.tile_size = tile_size
        self.enlargement = enlargement
        self.ascii_gif = prepend_to_path(path,'ascii')
        self.gif_dir = os.path.basename(path).split('.')[0]
        self.delay = delay
        self.as_text=as_text
        self.img_type = img_type
        if as_text:
            self.img_type = 'L'
        if not os.path.isdir(self.gif_dir):
            os.makedirs(self.gif_dir)
        self.ascii_gif_dir = prepend_to_path(self.gif_dir,'ascii')
        if not os.path.isdir(self.ascii_gif_dir):
            os.makedirs(self.ascii_gif_dir)
        self.save_frames()
        
    def is_partial(self):
        partial_tile = False
        while True:
            try:
                if self.image.tile:
                    tile = self.image.tile[0]
                    region = tile[0]
                    region_dimensions = tile[2:]
                    if region_dimensions != self.image.size:
                        partial_tile = True
                        break
                self.image.seek(self.image.tell() + 1)
            except EOFError:
                break
        self.image.seek(0)
        return partial_tile

    def get_image_frames(self):
        is_partial_gif = self.is_partial()
        palette = self.image.getpalette()
        previous_frame = None
        while True:
            try:
                if not self.image.getpalette():
                    self.image.putpalette(p)
                new_frame = Image.new('RGBA',self.image.size)
                if is_partial_gif and previous_frame is not None:
                    new_frame.paste(previous_frame)
                new_frame.paste(self.image,(0,0),self.image.convert('RGBA'))
                yield new_frame
                previous_frame = new_frame
                self.image.seek(self.image.tell()+1)
            except EOFError:
                break

    def save_frames(self):
        fp_list = []
        data = None
        for idx,img in enumerate(self.get_image_frames()):
            img_fp = '%s-%s.jpg'%(self.gif_dir,idx)
            fp = os.path.join(self.gif_dir,img_fp)
            img.save(fp)
            ascii_fp = prepend_to_path(img_fp,'ascii')
            out_fp = os.path.join(self.ascii_gif_dir,ascii_fp)
            mosaic = Photo_Mosaic(fp,self.tile_directory,enlargement=self.enlargement,
                                  tile_size=self.tile_size,out_fp=out_fp,data=data,
                                  as_text=self.as_text)
            mosaic.save()
            if data is None:
                data = mosaic.get_data()
            fp_list.append(out_fp)
        fp_string = ' '.join(fp_list)
        cmd = 'convert -loop 0 -delay {0} {1} {2}'.format(self.delay,fp_string,self.ascii_gif)
        os.system(cmd)
        
class Photo_Mosaic:
    def __init__(self,original_image,tile_directory=None,enlargement=1,
                 tile_size=50,tile_rescale = 0.5,out_fp=None,
                 data=None,euclid=False,as_text=False,img_type='RGB'):
        self.character_dictionary = None
        if tile_directory is None:
            tile_directory = get_default_tile_directory()
        if as_text:
            img_type = 'L'
            self.character_dictionary = get_default_character_dictionary()
            tile_directory = get_default_tile_directory()
        self.img_type = img_type
        if data is None:
            self.large_tile_data,self.small_tile_data  = Tile_Processor(tile_directory,tile_size,tile_rescale,img_type=img_type).get_data()
        else:
            self.large_tile_data,self.small_tile_data = data
        self.char_matrix=[]
        self.use_euclid = euclid
        self.enlargement = enlargement
        self.tile_rescale = tile_rescale
        self.tile_size = tile_size
        self.rows = None
        self.cols = None
        self.large_image_data,self.small_image_data = self.get_image_data(original_image)
        self.replace_tiles()
        self.pix_map = self.stitch_image()
        self.out_path = 'Mosaic_of_'+original_image if not out_fp else out_fp


    def get_data(self):
        return (self.large_tile_data,self.small_tile_data)

    def get_image_data(self,image_path):
        print('Processing main image...')
        img = Image.open(image_path).convert(self.img_type)
        w_original,h_original = img.size
        w_large = math.ceil(w_original * self.enlargement)
        h_large = math.ceil(h_original * self.enlargement)
        if w_large %2 == 1:
            w_large-=1
        if h_large %2 ==1:
            h_large-=1
        final_img = img.resize((w_large,h_large),Image.ANTIALIAS)
        w_crop = (w_large % self.tile_size) // 2
        h_crop = (h_large % self.tile_size) // 2
        if (w_crop + h_crop) > 0:
            final_img = final_img.crop((w_crop,h_crop,w_large-w_crop,h_large-h_crop))
        w_final,h_final = final_img.size
        self.cols = w_final // self.tile_size
        self.rows = h_final // self.tile_size
        w_small = self.cols * math.ceil(self.tile_size * self.tile_rescale)
        h_small = self.rows * math.ceil(self.tile_size * self.tile_rescale)
        small_img = final_img.resize((w_small,h_small),Image.ANTIALIAS)
        large_pix_map,small_pix_map = (np.array(final_img),np.array(small_img))
        try:
            image_data = (self.split_image(large_pix_map),self.split_image(small_pix_map))
        except Exception as e:
            print(e)
            bp()
            print('foo')
        return image_data

    def split_image(self,pix_map):
        rows,cols = (self.rows,self.cols)
        split_data = (np.concatenate([np.split(row,cols,axis=1)
            for row in np.split(pix_map,rows)]))
        return split_data
        
    @staticmethod
    def get_tile_difference(t1,t2,use_euclid=False):
        t1 = t1.astype(np.int32)
        t2 = t2.astype(np.int32)
        if not use_euclid:
            diff = np.sum(np.fabs(t1-t2))
        else:
            diff = np.sum((t1-t2)**2)
        return diff

    def get_best_fit_tile(self,tile):
        best_fit_tile = None
        min_diff = float('inf')
        for tile_index,tile_data in enumerate(self.small_tile_data):
            diff = self.get_tile_difference(tile_data,tile,self.use_euclid)
            if diff < min_diff:
                min_diff = diff
                best_fit_tile_index = tile_index 
        return best_fit_tile_index


    def replace_tiles(self):
        total = len(self.large_image_data)-1
        for index,item in enumerate(self.large_image_data):
            if index %10 == 0 or index == total:
                print('------{:.1%} of mosaic processed ------'.format(index/float(total)),end='\r')
            best_tile_index = self.get_best_fit_tile(self.small_image_data[index])
            self.large_image_data[index] = self.large_tile_data[best_tile_index]
            if self.character_dictionary:
                self.char_matrix.append(self.character_dictionary[best_tile_index])
                
    def stitch_image(self):
        tile_list = self.large_image_data
        rows = self.rows
        row_list = np.split(tile_list,rows)
        pix_map = np.concatenate([np.concatenate(row,axis = 1) for row in row_list])
        return pix_map

    def save(self,display=False):
        img = Image.fromarray(self.pix_map)
        img.save(self.out_path)
        if self.character_dictionary:
            txt_fp = self.out_path.split('.')[0] + '.txt'
            cols = len(self.char_matrix)//self.rows
            chunked = chunks(self.char_matrix,cols)
            chunk_string = '\r\n'.join([''.join(chunk) for chunk in chunked])
            print(chunk_string)
            with open(txt_fp,'w+') as fn: fn.write(chunk_string)
        if display:
            os.system(self.out_path)

class Tile_Processor:
    def __init__(self,tile_directory,tile_size = 50,tile_match_scale=0.5,img_type='RGB'):
        self.tile_path_list = [os.path.join(tile_directory,fp) 
                for fp in os.listdir(tile_directory)]
        self.img_type = img_type
        self.tile_size = tile_size
        self.tile_match_size = math.ceil(tile_size * tile_match_scale)
        self.large_tile_list = []
        self.small_tile_list = []
        self.process_tile_directory()

    def process_tile_data(self,tile_path):
        img = Image.open(tile_path).convert(self.img_type)
        w,h = img.size
        min_dimension = min(w,h)
        w_crop = (w-min_dimension)//2
        h_crop = (h-min_dimension)//2
        img = img.crop((w_crop,h_crop,w-w_crop,h-h_crop))
        large_tile_img = img.resize((self.tile_size,self.tile_size),Image.ANTIALIAS)
        small_tile_img = img.resize((self.tile_match_size,self.tile_match_size),Image.ANTIALIAS)
        tile_data = (np.array(large_tile_img),np.array(small_tile_img))
        return tile_data

    def process_tile_directory(self):
        total = len(self.tile_path_list)
        for index,fp in enumerate(self.tile_path_list,start=1):
            if index % 10 == 0 or index == total:
                print('-----{:.1%} of tiles processed ------'.format(index/total),end='\r')
            large,small = self.process_tile_data(fp)
            self.large_tile_list.append(large)
            self.small_tile_list.append(small)
    
    def get_data(self):
        return (self.large_tile_list,self.small_tile_list)
       


import photomosaic

def main():
    for i in range(1,11):
        out_path = 'Mosaic_of_dameron_%s.jpg'%i
        mosaic = photomosaic.Photo_Mosaic('dameron.jpg','tile_directory',enlargement=i,tile_size = 50,tile_rescale=1,out_fp=out_path)
        mosaic.save(True)
if __name__ == '__main__':
    main()


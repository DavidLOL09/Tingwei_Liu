import numpy as np
import astropy
import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/lacosmic/')
sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/lacosmic/lacosmic')
import core
import os
from icecream import ic
from astropy.io import fits
import matplotlib.pyplot as plt

data='/Users/david/PycharmProjects/Demo1/Part3'
files=[]
for file in os.listdir(data):
  if file.endswith('.fits.gz'):
    files.append(os.path.join(data,file))
data_list=[]
files=sorted(files)
for file in files:
  ic(file)
  with fits.open(file) as hdul:
    ic(hdul.info())
    ic('here')
    for i in range(1,len(hdul)):
      data_list.append(hdul[i].data)

chip_a = np.array(data_list[0])
chip_b = np.array(data_list[1])
def show_img(image):
    fig,ax=plt.subplots(1,1,figsize=(8,8))
    vmin, vmax = np.percentile(image, (1, 99))
    im=ax.imshow(image, cmap='rainbow', vmin=vmin, vmax=vmax)
    fig.colorbar(im,ax=ax)
    plt.show()
chip_a=chip_a[90:2500,50:1600]
# show_img(chip_a)
la_image=core.lacosmic(chip_a,contrast=1.5,cr_threshold=1.5,neighbor_threshold=1,mask=False,effective_gain=1,readnoise=1)

# (chip_a,contrast=1.5,cr_threshold=1.5,neighbor_threshold=1,mask=True)
show_img(la_image)
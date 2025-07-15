from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import numpy as np
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import channelParameters as chp
from icecream import ic
import os
import send2trash
from NuRadioReco.framework.parameters import stationParameters as stnp
import ToolsPac
import matplotlib.pyplot as plt

def get_direction(reader:NuRadioReco.modules.io,Temp_id):
    direction_r=[]
    dir_g=[]
    for evt in reader.get_events():
        stn = evt.get_station(51)
        run=evt.get_run_number()
        id=evt.get_id()
        if evt[evtp.Pass_cut_line][Temp_id]:
            zen = stn.get_parameter(stnp.zenith)/units.deg
            azi = stn.get_parameter(stnp.azimuth)/units.deg
            direction_r.append([zen,azi])
        else:
            zen = stn.get_parameter(stnp.zenith)/units.deg
            azi = stn.get_parameter(stnp.azimuth)/units.deg
            dir_g.append([zen,azi])
    return direction_r,dir_g
def direction_plot_detect(ax:plt.axes,name:str,direct:list,zorder=1,color='r',alfa=1):
    # direct=[]
    # ax.set_title('Direct')
    ax.set_rlim(0,90)
    direct=np.array(direct)
    zen=direct[:,0]
    azi=direct[:,1]
    # if len(zen)<10000:
    #     al=0.5
    # else:
    #     al=0.1
    # annotate_scatter(ax,azi,zen,Iden)
    ax.scatter(azi,zen,s=20,alpha=alfa,zorder=zorder,color=color,label=len(zen))
    ax.legend()
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Candi_with_direct/R243E512_cut'
readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
fig,ax = plt.subplots(1,2,figsize=(10,5),layout='constrained',subplot_kw={'projection': 'polar'})
dir_r,dir_g   = get_direction(readARIANNAData,'R243E512')
ax1=ax[0]
ax2=ax[1]
direction_plot_detect(ax1,'Pass',dir_r)
direction_plot_detect(ax2,'No-Pass',dir_g,color='grey')
plt.show()



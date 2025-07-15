Vrms=(9.71+9.66+8.94)/3
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from icecream import ic
from NuRadioReco.framework.parameters import stationParameters as stnp
input_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/'
from NuRadioReco.utilities import units
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
from NuRadioReco.modules.ARIANNA import hardwareResponseIncorporator as ChardwareResponseIncorporator
hardwareResponseIncorporator = ChardwareResponseIncorporator.hardwareResponseIncorporator()
hardwareResponseIncorporator.begin(debug=False)
from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.detector import detector
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
import NuRadioReco.modules.channelResampler
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
ic(NuRadioReco.modules.channelResampler.__file__)
# channelResampler.begin(debug=False)
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.channelSignalReconstructor
channelSignalReconstructor=NuRadioReco.modules.channelSignalReconstructor.channelSignalReconstructor()
import NuRadioReco.modules.channelTemplateCorrelation
channelTemplateCorrelation = NuRadioReco.modules.channelTemplateCorrelation.channelTemplateCorrelation(template_directory='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/')
channelTemplateCorrelation.begin(debug=False)
import NuRadioReco.modules.io.eventWriter
eventWriter = NuRadioReco.modules.io.eventWriter.eventWriter()
import datetime
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
from NuRadioReco.framework.parameters import channelParameters as chp
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
# readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input_path))
files = os.listdir(input_path)
director = []
for i in files:
    if i.startswith('.'):
        continue
    director.append(i)
print(director)

def making_Xcorr(path,output):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(path))
    eventWriter.begin(os.path.join(output,'Vrms_Xcorr&Incop.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time = stn.get_station_time().datetime
        det.update(time)
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        channelResampler.run(evt,stn,det,sampling_rate=1*units.GHz)
        channelSignalReconstructor.run(evt,stn,det)
        channelTemplateCorrelation.run(evt,stn,det,cosmic_ray=True,n_templates=1, channels_to_use=[4,5,6])
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=True)
        eventWriter.run(evt)
    return output
    print('Complete')
output_path  = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output'




path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig'
input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig_hasXcorr/'
def SNR_Xcorr_Scatter(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io,zorder=1,color='r',alpha=1):
    ax.set_title(name)
    # ax.set_xlabel('SNR')
    ax.set_ylabel('Xcorr')
    SNR_dic = []
    X_dic   = []
    for evt in readARIANNAData.get_events():   
        stn = evt.get_station(51)
        Xcorr=[]     
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        X_dic.append(np.max(Xcorr))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        SNR_dic.append(max(trace_up)/Vrms)   
    ax.scatter(SNR_dic,X_dic,s=5,c=color,label=f'{name}:{len(SNR_dic)}',zorder=zorder,alpha=alpha)
    ax.set_xscale('log')
    ax.grid()

def SNR_Xcorr_Scatter_sim(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
    SNR_dic = []
    X_dic   = []
    weights=[]
    # ax.set_title(f'{name} chn{chn}')
    ax.set_ylabel('Xcorr')
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        X_dic.append(np.max(Xcorr))
        trace_up    = []
        weights.append(evt.get_parameter(evtp.event_rate))
        trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        SNR_dic.append(max(trace_up)/Vrms)
    ic(len(SNR_dic),len(X_dic))
    # ax.set_xscale('log')
    SNR_bins=np.linspace(np.min(SNR_dic),np.max(SNR_dic),101)
    X_bins=np.linspace(0,1,101)
    ax.set_xlim(3,900)
    ax.set_ylim(0,1)
    hist,_,_=np.histogram2d(SNR_dic,X_dic,bins=(SNR_bins,X_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.set_xlabel(f'SNR {np.sum(weights):.2f}')
    ax.legend()


def get_eventWriter(name):
    writ_path = os.path.join(output_path,name)
    if not os.path.isdir(writ_path):
        os.makedirs(writ_path)
    eventWriter.begin(os.path.join(writ_path,f'{name}.nur'))
    return eventWriter

def SNR_cut_line(ax):
    x=np.linspace(0,1000,1001)
    k=0.3
    y=k*np.log10(x)+0.2
    ax.plot(x,y,color='blue',linestyle='--',zorder=3)



def SNR_Scattering(path1,name1,
                   path2,name2,
                   path3,name3,
                   path4,name4,
                   sim1,sim2,sim3,sim4):
    fig,Axes = plt.subplots(2,2,figsize=(10,8),layout='constrained')
    # Axes= fig.subplots(2,2,sharey=True)
    ax1 = Axes[0][0]
    ax2 = Axes[0][1]
    ax3 = Axes[1][0]
    ax4 = Axes[1][1]

    # ax5 = fig.add_subplot(2,3,5)
    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path5))
    # SNR_Xcorr_Scatter(ax5,name5,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path4))
    # SNR_Xcorr_Scatter(ax4,name4,Reader,alpha=0.5)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path3))
    # SNR_Xcorr_Scatter(ax3,name3,Reader,alpha=0.3)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path2))
    SNR_Xcorr_Scatter(ax2,name2,Reader,alpha=0.1)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path1))
    # SNR_Xcorr_Scatter(ax1,name1,Reader)


    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim1))
    # SNR_Xcorr_Scatter_sim(ax1,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim2))
    SNR_Xcorr_Scatter_sim(ax2,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim3))
    # SNR_Xcorr_Scatter_sim(ax3,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim4))
    # SNR_Xcorr_Scatter_sim(ax4,Reader)

    plt.show()

sim_bic='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Bicone/X_Ratio'
sim_zen='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_Ratio_Zen'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen_TrigR8_cut/SNR_cut'
raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
X='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR_cut'
bic='/Users/david/PycharmProjects/Demo1/Research/Repository/Det_Bic/X_Ratio'
Ratio='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio'
Zen='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_X_output/X_Ratio_Zen'
SNR_Scattering(raw_ngoso,'Raw',
               X,'X',
               bic,'Ratio',
               Zen,'Zen',
               sim_zen,sim_zen,sim_bic,sim_zen,)

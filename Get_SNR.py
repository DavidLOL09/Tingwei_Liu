Vrms=(9.71+9.66+8.94)/3
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from icecream import ic
import matplotlib.patches as mpatches
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
import ToolsPac
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

def annotate_scatter(ax,x,y,labels):
    for xi, yi, txt in zip(x, y, labels):
        ax.annotate(
            txt,                 # text to draw
            xy=(xi, yi),         # point to annotate
            xytext=(5, 5),       # (dx, dy) offset in points
            textcoords='offset points',
            fontsize=9, weight='bold',
            ha='left', va='bottom'
        )


path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig'
input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig_hasXcorr/'
def SNR_Xcorr_Scatter(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io,zorder,color='r',alfa=1):
    # ax.set_title('SNR')
    # ax.set_xlabel('SNR')
    ax.set_ylabel('Xcorr')
    SNR_dic_r = []
    X_dic_r   = []
    SNR_dic_g = []
    X_dic_g   = []  
    iden=[]
    for evt in readARIANNAData.get_events():   
        stn = evt.get_station(51)
        Xcorr=[]    
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=np.max(Xcorr)
        trace_up=np.max(trace_up)
        if Xcorr>=SNR_cut_line_cut(trace_up/Vrms):
            SNR_dic_r.append(trace_up/Vrms)  
            X_dic_r.append(Xcorr) 
            iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
        else:
            SNR_dic_g.append(trace_up/Vrms)
            X_dic_g.append(Xcorr)
    # annotate_scatter(ax,SNR_dic_r,X_dic_r,iden)
    ax.set_ylim(0.2,1)
    ax.scatter(SNR_dic_r,X_dic_r,s=20,c=color,label=f'{name}:{len(SNR_dic_r)}',zorder=zorder,alpha=alfa)
    # ax.scatter(SNR_dic_g,X_dic_g,s=5,c='grey',label=f'No-pass:{len(SNR_dic_g)}',zorder=zorder,alpha=alfa)
    ax.set_xscale('log')
    # ax.grid()
def SNR_cut_line_cut(x):
    k=0.3
    y=k*np.log10(x)+0.2
    return y

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
            # Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
            Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp]['R243E512']['chi_max'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        # if np.max(Xcorr)<=SNR_cut_line_cut(max(trace_up)/Vrms):
        #     continue
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        weights.append(evt.get_parameter(evtp.event_rate))
    ic(len(SNR_dic),len(X_dic))
    # ax.set_xscale('log')
    # SNR_bins=np.linspace(np.min(SNR_dic),np.max(SNR_dic),101)
    SNR_bins = np.logspace(np.log10(np.min(SNR_dic)), np.log10(np.max(SNR_dic)), 101)
    weights=np.array(weights)*31/365
    X_bins=np.linspace(0,1,101)
    ax.set_xlim(3,900)
    ax.set_ylim(0.2,1)
    hist,_,_=np.histogram2d(SNR_dic,X_dic,bins=(SNR_bins,X_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    # patch = mpatches.Patch(color='lightblue', label='Your Label Here')
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    # ax.legend(handles=[patch],fontsize=20)
    ax.legend(loc='lower right',fontsize=40)

def SNR_Xcorr_Scatter_Gradient(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
    SNR_dic = []
    X_dic   = []
    # ax.set_title(f'{name} chn{chn}')
    ax.set_ylabel('Xcorr')
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        # if np.max(Xcorr)<=SNR_cut_line_cut(max(trace_up)/Vrms):
        #     continue
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
    ic(len(SNR_dic),len(X_dic))
    # ax.set_xscale('log')
    # SNR_bins=np.linspace(np.min(SNR_dic),np.max(SNR_dic),101)
    SNR_bins = np.logspace(np.log10(np.min(SNR_dic)), np.log10(np.max(SNR_dic)), 51)
    X_bins=np.linspace(0,1,51)
    ax.set_xlim(3,900)
    ax.set_ylim(0,1)
    hist,_,_=np.histogram2d(SNR_dic,X_dic,bins=(SNR_bins,X_bins))
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.legend()


def get_eventWriter(name):
    writ_path = os.path.join(output_path,name)
    if not os.path.isdir(writ_path):
        os.makedirs(writ_path)
    eventWriter.begin(os.path.join(writ_path,f'{name}.nur'))
    return eventWriter

def SNR_cut_line(ax):
    x=np.linspace(1,1000,1001)
    k=0.3
    y=k*np.log10(x)+0.2
    ax.plot(x,y,color='blue',linestyle='--',zorder=3)
    # for i in np.linspace(0.4,1,7):
    #     ax.axhline(y=i,color='blue',linestyle='--',zorder=3)
    # for i in np.logspace(0.5,2,11):
    #     ax.axvline(x=i,color='blue',linestyle='--',zorder=3)

# ic| f'trace: {trace_max}': 'trace: 90.47757795735635'
# ic| f'Xcorr: {Xcorr}  exp: {SNR_cut_line(trace_max)}': 'Xcorr: 0.6869060315157663  exp: 0.786962289863568'


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
    # SNR_Xcorr_Scatter(ax4,name4,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path3))
    # SNR_Xcorr_Scatter(ax3,name3,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path2))
    # SNR_Xcorr_Scatter(ax2,name2,Reader)

    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(path1))
    # SNR_Xcorr_Scatter(ax1,name1,Reader)


    Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim1))
    SNR_Xcorr_Scatter_sim(ax1,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim2))
    SNR_Xcorr_Scatter_sim(ax2,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim3))
    SNR_Xcorr_Scatter_sim(ax3,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim4))
    SNR_Xcorr_Scatter_sim(ax4,Reader)

    plt.show()

sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_bef_cut'
sim_bef='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X'
sim_aft = '/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_with_direct/Candi_with_direct/withTemp_R243E512'

sim_zen='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output/X_Zen_UD'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Final_Candi'
raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'

Before='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X'
After='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR'

raw='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'

fig,ax = plt.subplots(1,1,figsize=(10,8),layout='constrained')
Reader_candi = NuRadioRecoio.NuRadioRecoio(get_input(candi))
SNR_Xcorr_Scatter(ax,'CR Candi',Reader_candi,2,color='red')

# Reader_rem = NuRadioRecoio.NuRadioRecoio(get_input(Before))
# id_lst=[]
# for evt in Reader_candi.get_events():
#     id_lst.append(ToolsPac.get_id_info(evt))
# grey_scatter=[]
# for evt in Reader_rem.get_events():
#     id=ToolsPac.get_id_info(evt)
#     if id in id_lst:
#         continue
#     grey_scatter.append(evt)


# Reader_raw=NuRadioRecoio.NuRadioRecoio(get_input(raw))
# SNR_Xcorr_Scatter(ax,'Trig',Reader_raw,1,color='grey',alfa=0.3)

# raw_Reader = NuRadioRecoio.NuRadioRecoio(get_input('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/raw_with_X'))
# SNR_Xcorr_Scatter_Gradient(ax,raw_Reader)
sim_Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim_aft))
SNR_Xcorr_Scatter_sim(ax,sim_Reader)
ax.tick_params(axis='x', labelsize=40)
ax.tick_params(axis='y', labelsize=40)

SNR_cut_line(ax)

# plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR_Final.png')
plt.show()
# plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/SNR.png')


# Incoporate_main()
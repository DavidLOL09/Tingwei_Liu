Vrms=(9.71+9.66+8.94)/3
import os
import matplotlib.pyplot as plt
import numpy as np
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
channelResampler.begin(debug=False)
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

def Analyze2(input):
    # 33Vrms_Ratio
    print('1')
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    print('2')
    Ratio = os.path.join(output_path,'33Vrms_Ratio_')
    print('1')
    os.makedirs(Ratio)
    print('1')
    eventWriter.begin(os.path.join(Ratio,'33Vrms_Ratio.nur'))
    print('1')
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time = stn.get_station_time().datetime
        det.update(time)
        trace_down  = []
        print('6')
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace())))
        trace_up    = []
        print('8')
        for channel in stn.iter_channels(use_channels=[4,5,6]):
            trace_up.append(np.max(np.abs(channel.get_trace())))   
        if np.max(trace_down)/np.max(trace_up)>=0.5:
            continue
        print('7')
        trace_bic=[]
        trace_bic.append(np.max(np.abs(stn.get_channel(7).get_trace())))
        if np.max(trace_bic)/np.max(trace_up)>=0.333 and np.max(trace_bic)>=3*Vrms:
            continue
        print('4')
        eventWriter.run(evt)
        print('5')
    print('Ratio Completed')
    return Ratio

def Analyze3(input):
    # X
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    X = os.path.join(output_path,'33Vrms_Ratio_X')
    os.makedirs(X)
    eventWriter.begin(os.path.join(X,'33Vrms_Ratio_X.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        Xcorr   =[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
        Chi = np.max(Xcorr)
        if Chi>0.4:
            templateDirectionFitter.run(
                evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
            eventWriter.run(evt)
    print('X Completed')
    return X

def Analyze4(input):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    zen_path= os.path.join(output_path,'33Vrms_Ratio_X_Zen')
    os.makedirs(zen_path)
    eventWriter.begin(os.path.join(zen_path,'33Vrms_Ratio_X_Zen.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        if zenith>85:
            continue
        eventWriter.run(evt)
    print('Zen Complete')
    return zen_path

def Analyze5(input):
    # Time_window, <10 events/h
    raw_input='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
    raw_input=NuRadioRecoio.NuRadioRecoio(get_input(raw_input))
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(input))
    TW_path= os.path.join(output_path,'33Vrms_Ratio_X_Zen_TimeWindow')
    if not os.path.isdir(TW_path):
        os.makedirs(TW_path)
    eventWriter.begin(os.path.join(TW_path,'33Vrms_Ratio_X_Zen_TimeWindow.nur'))
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time = stn.get_station_time().datetime
        hour_c=0
        for raw in raw_input.get_events():
            raw_stn=raw.get_station(51)
            raw_time=raw_stn.get_station_time().datetime
            if raw_time-time<=datetime.timedelta(minutes=30):
                hour_c+=1
            if hour_c==10:
                break
        if hour_c==10:
            continue
        eventWriter.run(evt)
        print('TW Complete')
        return TW_path


    print(type(raw_input))
    print(type(readARIANNAData))




path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig'
input_dir='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig_hasXcorr/'
def SNR_Xcorr_Scatter(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io):
    ax.set_title(name)
    ax.set_xlabel('SNR')
    ax.set_ylabel('Xcorr')
    ax.grid()
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
            trace_up.append(np.max(np.abs(channel.get_trace())))
        SNR_dic.append(max(trace_up)/Vrms)   
    ax.scatter(SNR_dic,X_dic,s=5,c='r',alpha=0.5,label=len(SNR_dic))
    ax.set_yscale('log')
    ax.legend()

def Incoporator(readARIANNAData:NuRadioReco.modules.io,eventWriter):
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        hardwareResponseIncorporator.run(evt, stn, det, sim_to_data=True)
        eventWriter.run(evt)
    print('Complete')

def Incoporate_main():
    Vrms_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig_hasXcorr'
    eventWriter = get_eventWriter('Vrms_Xcorr&Incop2')
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_path))
    Incoporator(readARIANNAData,eventWriter)

    Vrms_Ratio_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio'
    eventWriter = get_eventWriter('Vrms_Ratio_Xcorr&Incop2')
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Ratio_path))
    Incoporator(readARIANNAData,eventWriter)

    Vrms_Ratio_X_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio_X'
    eventWriter = get_eventWriter('Vrms_Ratio_X_Xcorr&Incop2')
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Ratio_X_path))
    Incoporator(readARIANNAData,eventWriter)
    print('Incoporate Complete')

    # Vrms_Ratio_X_Zen_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio_X_Zen'
    # Vrms_Ratio_X_Zen_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Ratio_X_Zen_Xcorr&Incop'
    # eventWriter = get_eventWriter('Vrms_Ratio_X_Zen_Xcorr&Incop2')
    # readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Ratio_X_Zen_path))
    # Incoporator(readARIANNAData,eventWriter)
    # print('Incoporate Complete')


def get_eventWriter(name):
    writ_path = os.path.join(output_path,name)
    if not os.path.isdir(writ_path):
        os.makedirs(writ_path)
    eventWriter.begin(os.path.join(writ_path,f'{name}.nur'))
    return eventWriter


def SNR_Scattering(path1,name1,path2,name2,path3,name3,path4,name4,path5,name5):
    fig,Axes = plt.subplots(3,2,figsize=(10,8),layout='constrained')
    # Axes= fig.subplots(2,2,sharey=True)
    ax1 = Axes[0][0]
    ax2 = Axes[0][1]
    ax3 = Axes[1][0]
    ax4 = Axes[1][1]
    ax5 = Axes[2][1]
    # ax5 = fig.add_subplot(2,3,5)
    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path5))
    SNR_Xcorr_Scatter(ax5,name5,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path4))
    SNR_Xcorr_Scatter(ax4,name4,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path3))
    SNR_Xcorr_Scatter(ax3,name3,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path2))
    SNR_Xcorr_Scatter(ax2,name2,Reader)

    Reader = NuRadioRecoio.NuRadioRecoio(get_input(path1))
    SNR_Xcorr_Scatter(ax1,name1,Reader)

    # Vrms_Ratio_X_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Ratio_X_Xcorr&Incop'
    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Ratio_X_path))
    # SNR_Xcorr_Scatter(ax3,'33Vrms_Ratio_X',Reader)

    # Vrms_Ratio_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Ratio_Xcorr&Incop'
    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Ratio_path))
    # SNR_Xcorr_Scatter(ax2,'33Vrms_Ratio',Reader)

    # Vrms_path = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig_hasXcorr'
    # Vrms_Incop='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Xcorr&Incop'
    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(Vrms_Incop))
    # SNR_Xcorr_Scatter(ax1,'33Vrms',Reader)

    # raw = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
    # Reader = NuRadioRecoio.NuRadioRecoio(get_input(raw))
    # SNR_Xcorr_Scatter(ax0,'Raw',Reader)

    plt.show()

# SNR_Scattering()
output = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Xcorr&Incop'
input  = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig'
# output = making_Xcorr(input,output)
output='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/Vrms_Xcorr&Incop'
# Ratio = Analyze2(output)
# X = Analyze3(Ratio)
# Zen = Analyze4(X)
Chanel33='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/3of35sig'
Ratio='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio_'
X='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio_X'
Zen='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_output/33Vrms_Ratio_X_Zen'
TW=Analyze5(Zen)
SNR_Scattering(output,'3/3Vrms',Ratio,'3/3Vrms_Ratio',X,'3/3Vrms_Ratio_X',Zen,'3/3Vrms_Ratio_X_Zen',TW='3/3Vrms_Ratio_X_Zen_TimeWindow')


# Incoporate_main()
import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation')
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import pandas as pd
import polynomial_regression
poly_reger = polynomial_regression.polynomial_regression()
from NuRadioReco.modules.channelLengthAdjuster import channelLengthAdjuster
import numpy as np
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.utilities import units
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.utilities.fft as fft
import NuRadioReco.modules.channelBandPassFilter
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
import matplotlib
import datetime
import send2trash
import os
from FFT_cut import flatVolt_remove
# import plot_waveform
from pathlib import Path
savename = 'Tingwei_Stn51'
trigger_name = 'direct_LPDA_3of3_3.5sigma'
save_channels = [4, 5, 6]
station_id = 51
import matplotlib.pyplot as plt
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.channelStopFilter
channelStopFilter = NuRadioReco.modules.channelStopFilter.channelStopFilter()
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
channelResampler.begin()
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import astropy
from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))
channels_to_use=[4,5,6]
import ToolsPac
import custimizedTemplateCorrelation
output_triggered='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/front_back_sep/Waveform'
# template_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template_with_backlope'

candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio'
trigger_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/'
simulation='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Simulation_weighted/'
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
import custimizedTemplateCorrelation
# from plot_waveform import plot_wave
Vrms=(9.71+9.66+8.94)/3
# from FFT_plot import fft_plot_det,fft_plot_sim
good_candi=['R243E531','R243E589','R243E1331']

def check_incop(input_path):
    candi_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    for evt in candi_reader.get_events():
        stn=evt.get_station(51)
        for ch in channels_to_use:
            chn=stn.get_channel(ch)
            trace=chn.get_trace()/units.mV
            ic(np.max(np.abs((trace))))
    ic(candi_reader.get_n_events())

def if_chiPass(evt):
    x_chn=[]
    stn=evt.get_station(51)
    for i in channels_to_use:
        chn=stn.get_channel(i)
        x_chn.append(chn[chp.cr_xcorrelations]['cr_ref_xcorr'])
    if min(x_chn)<0:
        ic('xcorr negative')
        exit()
    if max(x_chn)<0.4:
        return False
    if min(x_chn)<0.3:
        return False
    return True

def chi_cut(input_path,output_path,filename):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    writer=ToolsPac.set_writer(output_path,filename)
    for evt in reader.get_events():
        if if_chiPass(evt):
            writer.run(evt)
    

# check_incop(simulation)
def apply_xcorr(input_path,output_path,filename):
    weight_bef=[]
    weight_aft=[]
    candi_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    candi_writer=ToolsPac.set_writer(output_path,filename)
    for evt in candi_reader.get_events():
        stn=evt.get_station(51)
        # weight_bef.append(evt.get_parameter(evtp.event_rate))
        channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
        channelStopFilter.run(evt,stn,det,append=0,prepend=0)
        # flatVolt_remove(evt)
        custimizedTemplateCorrelation.run(evt,channels_to_use,gauss_check=True)
        # if if_chiPass(evt):

        # weight_aft.append(evt.get_parameter(evtp.event_rate))

        candi_writer.run(evt)
    # ic(weight_bef)
    # ic(weight_aft)
trigger_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/Freqs'
# apply_xcorr(candi,trigger_path,'Trig_Freqs_X')

def apply_BandPassFilter(evt:NuRadioReco.framework.event.Event):
    stn=evt.get_station(51)
    channelBandPassFilter.run(evt, stn, det, passband=[80 * units.MHz, 500 * units.MHz], filter_type='butter', order = 10)
    return evt
def apply_channelStopFilter(evt:NuRadioReco.framework.event.Event):
    stn = evt.get_station(51)
    channelStopFilter.run(evt,stn,det,append=0,prepend=0)
    return evt
def apply_direction_reconstruct(evt:NuRadioReco.framework.event.Event):
    stn = evt.get_station(51)
    time = stn.get_station_time()
    det.update(time)

    templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)


def process_template(input_path,output,filename_general):
    e_range = np.arange(16.0, 18.6, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)
    for e in e_range:
        for sin2 in sin2Val:
            filename=f'Stn51_IceTop_{e:.1f}-{e+0.1:.1f}eV_{sin2:.1f}sin2'
            files=[]
            for file in os.listdir(input_path):
                if filename in file:
                    files.append(os.path.join(input_path,file))
            if files==[]:
                continue
            count=0
            output_path=os.path.join(output,filename_general)
            readARIANNAData=NuRadioRecoio.NuRadioRecoio(files)
            writer=ToolsPac.set_writer(output_path,filename,False)
            for evt in readARIANNAData.get_events():
                Freqs=Freqs_evt(evt)>=0.115
                if Freqs:
                    continue
                stn=evt.get_station(51)
                trace=ToolsPac.get_Max_trace(stn,[4,5,6])/Vrms<5
                if trace:
                    continue
                evt=apply_BandPassFilter(evt)
                evt=apply_channelStopFilter(evt)
                evt.set_parameter(evtp.evt_id,count)
                count+=1
                writer.run(evt)



    

def SNR_Xcorr_scatter_candi(ax:plt.axes,reader:NuRadioReco.modules.io,has_cutline=False,c_pass='r',c_fail='g'):
    SNR_dic = []
    X_dic   = []
    SNR_dic_bad = []
    X_dic_bad = []
    # Ratio_X=['R266E2270', 'R247E1149', 'R243E15', 'R243E103', 'R243E311', 'R243E1192']
    # Drive_X=['R266E1720', 'R256E732', 'R256E1414', 'R256E1694', 'R256E2108', 'R243E2', 
    #     'R243E6', 'R243E89', 'R243E294', 'R243E314', 'R243E324', 'R243E330', 'R243E537', 'R243E589']
    # bad_evts=['R247E831','R263E708','R263E734','R263E735','R263E736','R263E737']
    Ratio_X_SNR=[]
    Drive_X_SNR=[]
    for evt in reader.get_events():
        stn = evt.get_station(51)
        trace_up = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
        id=f'R{evt.get_run_number()}E{evt.get_id()}'
        # if not SNR_cut(np.max(trace_up)/Vrms,np.max(Xcorr)):
        #     SNR_dic_bad.append(np.max(trace_up)/Vrms)
        #     X_dic_bad.append(np.max(Xcorr))
        #     continue
        iden=ToolsPac.get_id_info(evt)
        # if iden in Ratio_X:
        #     Ratio_X_SNR.append([np.max(trace_up)/Vrms,np.max(Xcorr)])
        #     continue
        # if iden in Drive_X:
        #     Drive_X_SNR.append([np.max(trace_up)/Vrms,np.max(Xcorr)])
        #     continue
        SNR_dic.append(np.max(trace_up)/Vrms)
        X_dic.append(np.max(Xcorr))
    Ratio_X_SNR=np.array(Ratio_X_SNR)
    Drive_X_SNR=np.array(Drive_X_SNR)
    # if len(Ratio_X_SNR)==0:
    #     pass
    # else:
    #     ax.scatter(Ratio_X_SNR[:,:1],Ratio_X_SNR[:,1:],color='red',label=f'Ratio only:{len(Ratio_X_SNR)}')
    
    # ax.scatter(Drive_X_SNR[:,:1],Drive_X_SNR[:,1:],color='yellow',label=f'Drive only:{len(Drive_X_SNR)}')
    ax.scatter(SNR_dic,X_dic,color=c_pass,label=f'evt:{len(X_dic)}',alpha=0.5)
    # ax.scatter(SNR_dic_bad,X_dic_bad,color=c_fail,label=f'bad:{len(X_dic_bad)}',alpha=0.2)

    return SNR_dic,X_dic
    # snr_dis=[]
    # chi_dis=[]
    # for isnr,snr in enumerate(SNR_dic):
    #     if snr>26:
    #         continue
    #     snr_dis.append(snr)
    #     chi_dis.append(X_dic[isnr])
    # return snr_dis,chi_dis


def if_existence(input_path,id_lst):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    exist=[]
    for evt in reader.get_events():
        iden=ToolsPac.get_id_info(evt)
        if iden in id_lst:
            exist.append(iden)
    ic(exist)

def Trig_threshold(input_path,output,filename):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    writer=ToolsPac.set_writer(output,filename)
    for evt in reader.get_events():
        stn = evt.get_station(51)
        run=evt.get_run_number()
        id=evt.get_id()
        trig=[]
        for ch in [4,5,6]:
            chn=stn.get_channel(ch)
            trace=np.max(np.abs(chn.get_trace()/units.mV))/Vrms
            trig.append(trace)
        trig=max(trig)
        if trig<5:
            if f'R{run}E{id}' in good_candi:
                ic(f'Freqs_cut:R{run}E{id}')
            continue
        writer.run(evt)
    return os.path.join(output,filename)

def threshold_check(input_path):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    lowest=100
    for evt in reader.get_events():
        stn=evt.get_station(51)
        max=ToolsPac.get_Max_trace(stn,[4,5,6])/Vrms
        if max<5:
            ic(ToolsPac.get_id_info(evt))
        if max<lowest:
            lowest=max
    ic(lowest)

def Logeqs(k,b,x):
    return k*np.log10(x)+b
def SNR_cut(SNR,Xcorr):
    # 2 backlope
    x=SNR
    y1=np.full_like(x[x<6.566],0.46)

    x2=x[(x>6.566)&(x<8.32)]
    y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    x3=x[(x>8.32)&(x<8.822)]
    y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    x4=x[(x>8.822)&(x<11.306)]
    y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    x5=x[(x>11.306)&(x<14.541)]
    y5=Logeqs(k=0.48497,b=0.20218,x=x5)

    y6=np.full_like(x[x>14.541],0.766)
    y=np.concatenate((y1,y2,y3,y4,y5,y6))

    # 1 backlope
    # x=SNR
    # y1=np.full_like(x[x<6.566],0.46)

    # x2=x[(x>6.566)&(x<8.32)]
    # y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    # x3=x[(x>8.32)&(x<8.822)]
    # y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    # x4=x[(x>8.822)&(x<11.306)]
    # y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    # x5=x[(x>11.306)]
    # y5=Logeqs(k=0.48497,b=0.20218,x=x5)
    # y=np.concatenate((y1,y2,y3,y4,y5))




    return Xcorr>y

def SNR_cut_line(ax):
    x=np.linspace(1,1000,1001)
    # 2 backlope
    y1=np.full_like(x[x<6.566],0.46)

    x2=x[(x>6.566)&(x<8.32)]
    y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    x3=x[(x>8.32)&(x<8.822)]
    y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    x4=x[(x>8.822)&(x<11.306)]
    y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    x5=x[(x>11.306)&(x<14.541)]
    y5=Logeqs(k=0.48497,b=0.20218,x=x5)

    y6=np.full_like(x[x>14.541],0.766)
    y=np.concatenate((y1,y2,y3,y4,y5,y6))

    # 1 backlope
    # y1=np.full_like(x[x<6.566],0.46)

    # x2=x[(x>6.566)&(x<8.32)]
    # y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    # x3=x[(x>8.32)&(x<8.822)]
    # y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    # x4=x[(x>8.822)&(x<11.306)]
    # y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    # x5=x[(x>11.306)]
    # y5=Logeqs(k=0.48497,b=0.20218,x=x5)
    # y=np.concatenate((y1,y2,y3,y4,y5))

    ax.plot(x,y,color='black',linestyle='--',zorder=3)


def Analyze_SNR(input_path,output,filename):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    writer=ToolsPac.set_writer(output,filename)
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)/Vrms
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            Xcorr.append(Xmax)
        Xcorr=np.max(Xcorr)
        if not SNR_cut(trace_max,Xcorr):
            continue
        writer.run(evt)
    ic('SNR Complete')
    return os.path.join(output,filename)

def Analyze_SNR_sus(input_path,output):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    filename='Trig_Freqs_335_X_Ratio_SNR_sus'
    writer=ToolsPac.set_writer(output,filename)
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)/Vrms
        Xcorr=[]
        for i in [4,5,6]:
            channel = stn.get_channel(i)
            Xmax=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            Xcorr.append(Xmax)
        Xcorr=np.max(Xcorr)
        if not SNR_cut(trace_max,Xcorr):
            if Xcorr>=0.7:
                writer.run(evt)
    ic('SNR Complete')
    return os.path.join(output,filename)

def Analyze_zen(input,output):
    # Zen,<=85deg
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input))
    filename='Trig_Freqs_335_X_Ratio_withZen'
    writer=ToolsPac.set_writer(output,filename)
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        time= stn.get_station_time().datetime
        det.update(time)
        templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
        zenith=stn.get_parameter(stnp.zenith)/units.deg
        # if zenith>85:
        #     continue
        writer.run(evt)
    ic('Zen Complete')
    return
def log_cut_line(x,UD_Bic):
    # UD:
    if UD_Bic=='UD':
        k=3.358751507788999
        y=k*np.log10(x)-5.067864845613618
        return y
    elif UD_Bic=='Bic':
    # Bic:
        k=3.9015114425732005
        y=k*np.log10(x)-6.360165150568652
        return y

def Analyze_Ratio(input_path,output_path):
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    filename='Trig_335_Freqs_Ratio'
    writer=ToolsPac.set_writer(output_path,filename)
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        trace_down=[]
        for channel in stn.iter_channels(use_channels=[0,1,2,3]):
            trace_down.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_down=np.max(trace_down)
        trace_max    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_max.append(np.max(np.abs(channel.get_trace()/units.mV)))
        trace_max=np.max(trace_max)
        channel = stn.get_channel(7)
        trace_bic = np.max(np.abs(channel.get_trace()/units.mV))
        ratio_bic=trace_max/trace_bic
        ratio_UD =trace_max/trace_down
        if ratio_bic<=log_cut_line(trace_max,'Bic'):
            continue
        if ratio_UD<=log_cut_line(trace_max,'UD'):
            continue
        evt.set_parameter(evtp.UD_Ratio,trace_max/trace_down)
        evt.set_parameter(evtp.Bic_Ratio,trace_max/trace_bic)
        writer.run(evt)
    ic('Ratio_complete')
    return

def Freqs_evt(evt:NuRadioReco.framework.event.Event):
    def get_trace_by_chn(i,evt):
        stn=evt.get_station(51)
        chn=stn.get_channel(i)
        trace_spectrum=chn.get_frequency_spectrum()
        return trace_spectrum
    def normalize_wave(trace):
        trace=np.abs(trace)
        return trace/np.sqrt(np.dot(trace,trace))
    def find_closest_index(criti_num,arr:np.array):
        try:
            for i in range(len(arr)):
                if criti_num-arr[i]<=0:
                    return i
            raise ValueError
        except ValueError:
            ic('Critical Number is bigger than every elemtns in array')
    def get_low_amp_ratio(criti_amp,evt,chn_num):
        sample_rate=1*units.GHz
        spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
        freqs = fft.freqs(256,sample_rate)/units.MHz
        index=find_closest_index(criti_amp,freqs)-1
        tot_amp = np.sum(spectrum)
        low_amp = np.sum(spectrum[0:index+1])
        ratio = low_amp/tot_amp
        return spectrum,freqs,ratio
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    largest=[0,0]
    time = stn.get_station_time().datetime
    # largest:[max_amp,ratio]
    # flatVolt_remove(evt)
    for i in range(4,7):
        spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
        if ratio>largest[1]:
            stn=evt.get_station(51)
            chn=stn.get_channel(i)
            trace=np.max(np.abs(chn.get_trace()/units.MeV))
            largest=[trace,ratio]
    # if largest[1]>=0.115:
    return largest[1]


def Analyze_Freqs(input_path,output_path):
    def get_trace_by_chn(i,evt):
        stn=evt.get_station(51)
        chn=stn.get_channel(i)
        trace_spectrum=chn.get_frequency_spectrum()
        return trace_spectrum
    def normalize_wave(trace):
        trace=np.abs(trace)
        return trace/np.sqrt(np.dot(trace,trace))
    def find_closest_index(criti_num,arr:np.array):
        try:
            for i in range(len(arr)):
                if criti_num-arr[i]<=0:
                    return i
            raise ValueError
        except ValueError:
            ic('Critical Number is bigger than every elemtns in array')
    def get_low_amp_ratio(criti_amp,evt,chn_num):
        sample_rate=1*units.GHz
        spectrum = normalize_wave(get_trace_by_chn(chn_num,evt))
        freqs = fft.freqs(256,sample_rate)/units.MHz
        index=find_closest_index(criti_amp,freqs)-1
        tot_amp = np.sum(spectrum)
        low_amp = np.sum(spectrum[0:index+1])
        ratio = low_amp/tot_amp
        return spectrum,freqs,ratio
    readARIANNAData = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    filename='Trig_335_Freqs'
    pass_weight = []
    no_pass_w   = []
    writer=ToolsPac.set_writer(output_path,filename)
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        run = evt.get_run_number()
        id = evt.get_id()
        largest=[0,0]
        time = stn.get_station_time().datetime
        # largest:[max_amp,ratio]
        # flatVolt_remove(evt)
        for i in range(4,7):
            spectrum,freqs,ratio=get_low_amp_ratio(80,evt,i)
            if ratio>largest[1]:
                stn=evt.get_station(51)
                chn=stn.get_channel(i)
                trace=np.max(np.abs(chn.get_trace()/units.MeV))
                largest=[trace,ratio]
        if largest[1]>=0.115:
            # no_pass_w.append(evt.get_parameter(evtp.event_rate))
            if f'R{run}E{id}' in good_candi:
                ic(f'Freqs_cut:R{run}E{id}')
            continue
        writer.run(evt)
        # pass_weight.append(evt.get_parameter(evtp.event_rate))
    ic('Freqs Complete')
    return output_path

# apply_xcorr(input_path,output_path,'Chi_research')
def get_Chi_spectrum(input_path):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    for evt in reader.get_events():
        fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=3, sharex='col', sharey='col')
        stn = evt.get_station(51)
        iden=f'R{evt.get_run_number()}E{evt.get_id()}'
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            # Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
            Xcorr=channel[chp.cr_xcorrelations]['cr_ref_xcorr_all']
            xcorrelations = channel[chp.cr_xcorrelations]
            ic(xcorrelations.keys())
            bin = range(0,len(Xcorr))
            ax=axes[chn-4]
            ax.plot(bin,Xcorr)
        fig.suptitle(iden)
        exit()
        plt.savefig(f'{os.path.join(input_path,iden)}.png')

def get_plot_info_sim(reader:NuRadioReco.modules.io):
    SNR_dic = []
    X_dic   = []
    weights = []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        # if max(trace_up)/Vrms<=4.5:
        #     continue

        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            # Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp]['R243E512']['chi_max'])))
            Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        weights.append(evt.get_parameter(evtp.event_rate))
    weights = np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
    SNR_dic = np.array(SNR_dic)
    X_dic   = np.array(X_dic)
    # data= { 'SNR':SNR_dic,
    #         'chi':X_dic,
    #         'weights':weights}
    # df  = pd.DataFrame(data)
    # df.to_excel('/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/Analyze_Trig_335_Freqs_X.xlsx', index=False)
    return SNR_dic,X_dic,weights



def SNR_Xcorr_Scatter_sim(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io,has_cutline=False):
    SNR_dic = []
    X_dic   = []
    # ax.set_title(f'{name} chn{chn}')
    ax.set_ylabel('Xcorr')
    weights=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        # if not stn.has_triggered('direct_LPDA_2of3_3.5sigma'):
        #     continue

        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        # if max(trace_up)/Vrms<=4.5:
        #     continue

        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            # Xcorr.append(np.max(np.abs(channel[chp.Chi_Temp]['R243E512']['chi_max'])))
            Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
        # if np.max(Xcorr)<=SNR_cut_line_cut(max(trace_up)/Vrms):
        #     continue
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        weights.append(evt.get_parameter(evtp.event_rate))
    ic(len(SNR_dic),len(X_dic))
    # ax.set_xscale('log')
    # SNR_bins=np.linspace(np.min(SNR_dic),np.max(SNR_dic),101)
    SNR_bins = np.logspace(np.log10(np.min(SNR_dic)), np.log10(np.max(SNR_dic)), 101)
    weights=np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
    # for i in weights:
    #     ic(i,type(i))
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

def sim_plots(ax:plt.axes,SNR:np.array,chi:np.array,weights:np.array):
    SNR_bins = np.logspace(np.log10(np.min(SNR)), np.log10(np.max(SNR)), 101)
    # weights=np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
    # for i in weights:
    #     ic(i,type(i))
    X_bins=np.linspace(0,1,101)
    ax.set_xlim(3,900)
    ax.set_ylim(0.2,1)
    hist,_,_=np.histogram2d(SNR,chi,bins=(SNR_bins,X_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    # patch = mpatches.Patch(color='lightblue', label='Your Label Here')
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)
    # ax.legend(handles=[patch],fontsize=20)
    ax.legend(loc='lower right',fontsize=40)



template_path_no_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_final'
template_path_1_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_1backL_Template_final'
template_path_2_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_2backlope_Template_final'
template_path_4_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/template_4_backlope'
template_path_elder_2='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template2backlope_bandpass_stopfilter'
custimizedTemplateCorrelation = custimizedTemplateCorrelation.custimizedTemplateCorrelation()
# custimizedTemplateCorrelation.begin(template_path_4_backlope)
det_input='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs'
det_output='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Xcorr_check'

# ic(custimizedTemplateCorrelation.get_template_size())
det_input='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/candidates'
det_output='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze4'
sim_input='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/sim/Trig_335_Freqs_X'
sim_output='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/sim'
# Trig_threshold(sim_input,sim_output,'Template_Trig_335')
# apply_xcorr(det_input,det_output,'Trig_335_Freqs_X')
# apply_xcorr(sim_input,sim_output,'Trig_335_Freqs_X')
# Analyze_SNR(det_input,det_output,'Trig_335_Freqs_X_SNR')
# Analyze_SNR(sim_input,sim_output,'Trig_335_Freqs_X_SNR')
# exit()
# apply_xcorr(det_input,det_output,'Trig_335_Freqs_Ratio_X_elder_2backlope')
ic('2 BL det complete')
# apply_xcorr(sim_input,sim_output,'Trig_335_Freqs_Ratio_X')
ic('2 BL sim complete')
# exit()
# Analyze_SNR(det_input,det_output,'Trig_335_Freqs_Ratio_X_SNR')
# Analyze_SNR(sim_input,sim_output,'Trig_335_Freqs_Ratio_X_SNR')
# exit()
# apply_xcorr(det_input,det_output,'Trig_335_Freqs_Ratio_X')
# apply_xcorr(sim_input,sim_output,'Trig_335_Freqs_Ratio_X')
# Thresh=Trig_threshold(sim_input,sim_output,'Trig_335')
# Analyze_Freqs(sim_input,sim_output)
# Analyze_Ratio(sim_input,sim_output)

# Analyze_Ratio(sim_input,sim_output)

# Analyze_SNR(det_input,det_output,'Trig_335_Freqs_Ratio_X_SNR')j
# Analyze_SNR(sim_input,sim_output,'Trig_335_Freqs_Ratio_X_SNR')
# Trig,Threshold,Freqs,Ratio,X,SNR
# Trig_threshold(det_input,det_output,'Trig_Threshold')
# Analyze_Freqs(det_input,det_output)
# Analyze_Ratio(det_input,det_output)
# Analyze_Ratio(sim_input,sim_output)
# apply_xcorr(det_input,det_output,'Trig_335_Freqs_Ratio_X')
# apply_xcorr(sim_input,sim_output,'Trig_335_Freqs_Ratio_X')
# exit()

# reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(det_input))
# writer =ToolsPac.set_writer(os.path.join(det_output,'High_SNR_check'),'bad')
# for evt in reader.get_events():
#     stn=evt.get_station(51)
#     SNR=ToolsPac.get_Max_trace(stn,[4,5,6])/Vrms
#     X=ToolsPac.get_Xcorr(stn,[4,5,6])
#     if SNR>15:
#         if X>0.766:
#             ic('here')
#             # writer.run(evt)
#             continue
#         elif X>0.7:
#             writer.run(evt)
#             pass
# exit()

def get_some_info(input_path,markname):
    ic(markname)
    reader_candi=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    ic(reader_candi.get_n_events())
    max_lst=[]
    for evt in reader_candi.get_events():
        stn=evt.get_station(51)
        max_lst.append(ToolsPac.get_Max_trace(stn,range(8)))
    ic(max(max_lst))
    print()

def check_if_superior_files(superior,subset):
    super_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(superior))
    sub_reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(subset))
    id_lst=[]
    for evt in super_reader.get_events():
        id_lst.append(ToolsPac.get_id_info(evt))
    for evt in sub_reader.get_events():
        iden=ToolsPac.get_id_info(evt)
        if iden not in id_lst:
            ic(iden)
            return False
    return True

def find_repeat_events(input_path1,name1,
                       input_path2,name2):
    reader1=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path1))
    reader2=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path2))
    id_lst=[]
    for evt in reader1.get_events():
        id_lst.append(ToolsPac.get_id_info(evt))
    common_lst=[]
    path1_only=[]
    path2_only=[]
    for evt in reader2.get_events():
        iden=ToolsPac.get_id_info(evt)
        if iden in id_lst:
            common_lst.append(iden)
            id_lst.remove(iden)
        elif iden not in id_lst:
            path2_only.append(iden)
    path1_only=id_lst
    ic(f'{name1}:{path1_only}')
    ic(f'{name2}:{path2_only}')
    ic(f'Both:{common_lst}')
    return path1_only,path2_only,common_lst

def fit_line(k_lst,x_lst):
    y_lst=[]
    for i in range(len(k_lst)):
        y=k_lst[i]*(x_lst**i)
        y_lst.append(y)
    y_lst=np.array(y_lst)
    # ic(np.shape(y_lst))
    y_lst=np.sum(y_lst,axis=0)
    return y_lst

def func_poly(k,x):
    y=np.zeros_like(x,dtype=np.float64)
    for i in range(len(k)):
        y+=k[i]*(x**i)
    return y


input_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/sim/Trig_335_Freqs_X_SNR'
input_det='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze4/analyze_candi'

def read_from_excel(input_path):
    df = pd.read_excel(input_path)
    SNR = df['SNR']
    X   = df['chi']
    weights = df['weights']
    return SNR,X,weights
# find_repeat_events(input_det,'SNR Drive',input_det_Ratio_X_SNR,'Ratio X SNR')
# apply_xcorr(input_det_Freqs,det_output,'Trig_335_Freqs_X')
# apply_xcorr(input_det_Freqs_Ratio,det_output,'Trig_335_Freqs_Ratio_X')
# Analyze_SNR(input_det_Freqs_X,det_output,'Trig_335_Freqs_X_SNR')
# Analyze_SNR(input_det_Freqs_Ratio_X,det_output,'Trig_335_Freqs_Ratio_X_SNR')
# Analyze_SNR(input_det,det_output,'X_SNR_Drive')
# Analyze_Ratio(input_det_Freqs,det_output)

# ic(check_if_superior_files(input_det_Freqs_X,input_det))
# get_some_info(input_det_Freqs_X,'Freqs_X')
# get_some_info(input_det_Freqs_Ratio_X,'Freqs_Ratio_X')

# apply_xcorr(input_path,output_path,'Freqs_Trig')
fig,ax = plt.subplots(figsize=(10,8),layout='constrained')
sim_Reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_sim))
reader_candi=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))
# reader_candi1=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det_Drive_SNR))
# reader_candi2=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))

# input_candi='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/candidates'
# output_path='/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze2/'
# reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_candi))
# writer = ToolsPac.set_writer(output_path,'candidates',sub_dir=False)
# ic(reader.get_n_events())
# apply_xcorr(input_candi,output_path,'analyze_candi')
# exit()


# for evt in reader_candi.get_events():
#     plot_wave(evt,os.path.join(candi,'waveform'))
# exit()

SNR,chi,weights=get_plot_info_sim(sim_Reader)
SNR,chi,weights=read_from_excel('/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/Analyze4_Trig_335_Freqs_X.xlsx')
# coeff_start=np.array([-2,5.2,-3.1,0.6])

# coeff=np.array([-0.6770314 , -0.02724029,  0.46074547,  0.66572675])

# coeff=[-52.1750008 ,   0.96321299,   1.99998365,   2.99999999]

SNR_bins = np.logspace(np.log10(np.min(SNR)), np.log10(np.max(SNR)), 10001)

# ic(np.min(SNR),np.max(SNR))
# ic(np.min(SNR_bins),np.max(SNR_bins))
X_bins=np.linspace(0,1,10001)

ax.set_xlim(3,900)
ax.set_ylim(0.2,1)

# poly_reger.begin(3,np.log10(SNR),chi,coeff_start,5+np.log10(weights))
# coeff,new_err,err,iter=poly_reger.run()

poly_reger.begin([0,1,2,3],np.log10(SNR),chi,regression='polynomial',demo_size=10,y_weights=weights,zoom=True,descent='Normal',learningR=1)
coeff,err,iteration,training_x = poly_reger.run()

# ic(coeff,new_err,err,iter)

def distance(dot_a:np.array,dot_b:np.array):
        return np.sum((dot_a-dot_b)**2)

def minimize_distance(x_bins:np.array,y_lst:np.array,tar_lst:np.array):
    def distance(dot_a:np.array,dot_b:np.array):
        return np.sum((dot_a-dot_b)**2)
    x_bins=np.log10(np.array(x_bins))
    tar_lst=np.array([np.log10(tar_lst[0]),tar_lst[1]])
    mini=100
    min_index=0
    for ix,x in enumerate(x_bins):
        dot_a=np.array([x_bins[ix],y_lst[ix]])
        distan=distance(dot_a,tar_lst)
        if distan<mini:
            mini=distan
            min_index=ix
    return mini,min_index

def get_minimized_couples(event_list:np.array,SNR_bins:np.array,y_exp:np.array):
    mini_lst=[]
    for event in event_list:
        snr = event[0]
        chi = event[1]
        dot = [snr,chi]
        mini,mini_index=minimize_distance(SNR_bins,y_exp,dot)
        fit_dot=[SNR_bins[mini_index],y_exp[mini_index]]
        mini_lst.append([mini,np.array(fit_dot)])
    # ic(mini_lst)
    return mini_lst

def plot_couples(event_list,close_fit,ax:plt.axes):
    for i in range(0,len(event_list)):
        snr=[event_list[i][0],close_fit[i][0]]
        chi=[event_list[i][1],close_fit[i][1]]
        ax.plot(snr,chi,c='blue')






# coeff=np.array([-1.78876845,  5.1553756 , -3.21896167,  0.66262541])
# tar=np.array([[9,0.9]])
# y_exp=fit_line(coeff,np.log10(SNR_bins))
# ic(coeff)
# coeff = [-1.78876845,  5.1553756 , -3.21896167,  0.66262541]
y_exp=func_poly(coeff,np.log10(SNR_bins))
for isnr,snr in enumerate(SNR_bins):
    if abs(snr-26)<=1:
        ic(isnr,snr)
        y_exp[isnr:]=y_exp[isnr]
        break
# y_exp1=fit_line(coeff_start,np.log10(SNR_bins))


# mini,min_index=minimize_distance(SNR_bins,y_exp,tar)




sim_plots(ax,SNR,chi,weights)
# SNR_Xcorr_Scatter_sim(ax,sim_Reader)
# SNR_Xcorr_scatter_candi(ax,reader_candi,c_pass='blue',c_fail='black')
snr_det,chi_det=SNR_Xcorr_scatter_candi(ax,reader_candi)

det_dots        = np.array([[snr_det[i],chi_det[i]] for i in range(0,len(snr_det))])
mini_lst        = get_minimized_couples(det_dots,SNR_bins,y_exp)
fit_dot         = np.array([mini_lst[i][1] for i in range(0,len(mini_lst))])
distance_lst    = np.array([mini_lst[i][0] for i in range(0,len(mini_lst))])

# ax.plot(SNR_bins,y_exp,c='red')

ax.plot(SNR_bins,y_exp,label=f'sample_size:{len(det_dots)} \naverage Variance:{np.mean(distance_lst):.8f}',c='red')

# ax.plot(SNR_bins,y_exp1,label='human fits',c='green')
SNR_cut_line(ax)
ax.grid()
ax.set_ylim(0,1)
ax.set_xscale('log')
# ax.scatter(fit_dot[:,:1],fit_dot[:,1:],c='green')
# plot_couples(det_dots,fit_dot,ax)
# ax.scatter(fit_dot[0],fit_dot[1],c='green')
ax.tick_params(axis='x', labelsize=40)
ax.tick_params(axis='y', labelsize=40)
plt.legend()
# plt.savefig(os.path.join(output_path,'Trig.png'))
plt.show()

# 2backlope:    coeff: array(   [-1.81057262,  5.16506113, -3.19452077,  0.65009633])
# 1backlope:    coeff: array(   [-1.79827926,  5.16493962, -3.20673635,  0.65560509])
# Nobacklope:   coeff: array(   [-1.77684555,  5.16588946, -3.21983238,  0.66077437])
# 4backlope:    coeff: array(   [-1.78876845,  5.1553756 , -3.21896167,  0.66262541])
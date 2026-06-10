import matplotlib.pyplot as plt
import numpy as np
import datetime
from icecream import ic
time_A=datetime.timedelta(hours=1,seconds=3)
hour = datetime.timedelta(hours=1)
import random
from icecream import ic
import matplotlib.pyplot as plt
from NuRadioReco.utilities import templates
import numpy as np
template_path='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/templates_cr_station_51.pickle'
# template_path='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/'
import pickle
# import NuRadioMC.NuRadioReco.utilities.templates

# Create a sine wave
# x = np.linspace(0, 5.5 * np.pi, 1000)
# x1= np.linspace(5.5*np.pi,10*np.pi,1000)
# y = np.sin(x)
# y1= 0.5*np.sin(x1+np.pi/3)+0.5*np.sin(x1)
# x = np.concatenate((x, x1))
# y = np.concatenate((y, y1))
# # Plot
# plt.figure(figsize=(8, 4))
# plt.plot(x, y, label='sin(x)')
# # plt.plot(x1,y1,label='sin(x+3)')
# plt.title('Sine Wave')
# plt.xlabel('x')
# plt.ylabel('sin(x)')
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()

# {template_id:{ch_id:[chi_max,chi_phase]}}

# xcorrelations['{}_ref_xcorr'.format(ref_str)] = np.abs(xcorrs_ch).mean()
# xcorrelations['{}_ref_xcorr_all'.format(ref_str)] = np.abs(xcorrs_ch)
# xcorrelations['{}_ref_xcorr_max'.format(ref_str)] = np.abs(xcorrs_ch[np.argmax(np.abs(xcorrs_ch))])
# xcorrelations['{}_ref_xcorr_time'.format(ref_str)] = np.mean(xcorrpos_ch[np.argmax(np.abs(xcorrs_ch))]) * dt
# xcorrelations['{}_ref_xcorr_template'.format(ref_str)] = template_key[np.argmax(np.abs(xcorrs_ch))]
# channel[chp.cr_xcorrelations] = xcorrelations

with open(template_path, 'rb') as file:
    template = pickle.load(file)

def get_klog(arr1,arr2):
    k=(arr1[1]-arr2[1])/(np.log10(arr1[0])-np.log10(arr2[0]))
    b=arr1[1]-k*np.log10(arr1[0])
    return k,b

def test_logeqs(k,b,arr1):
    exp=k*np.log10(arr1[0])+b
    ic(exp)
    return exp==arr1[1]

# arr1=[14.541,0.766] 
# arr2=[11.306,0.713]
# k,b=get_klog(arr1,arr2)
# ic(k,b)
# ic(test_logeqs(k,b,arr1))

A=np.array([[1,2],[3,4]])
# ic(A[:,:])
theta = 0.11186
p_t = 40*np.tan(theta)/np.sqrt(np.tan(theta)**2+1)
y = np.sqrt(1640-(1600*(np.tan(theta)**2))/np.sqrt(np.tan(theta)+1))+40/np.sqrt(np.tan(theta)**2+1)
ic(y)
ic(np.log(np.e))

ic(np.log(1000))
ic(3*np.log(10))
ic(np.log(np.e))
ic(np.e**(-4.2*np.log(10)))
ic(10*np.e**(-4.2))
# exit()

# fig,ax = plt.subplots(1,1,figsize=(5,5))
# x = np.logspace(-1,4,1001)
# # x=np.array([1,1000])
# a = 1/(np.log(1000))
# b = 10**(-4.2)
# y = a*((1+x**2)/(x**2))*np.log(x/b)
# ic(y)
# ax.plot(x,y)
# ax.set_ylim(1,10)
# ax.set_xscale('log')
# ax.set_yscale('log')

# plt.show()

from scipy.integrate import quad

# Define your function
def integrand(z):
    a = 1/(3*np.log(10))
    b = 10**-4.2
    dE_dx = a*((1+z**2)/(z**2))*np.log(z/b)
    y = z*100/(dE_dx*np.sqrt(z**2+1))
    return y

# Integrate from 0 to 1
result, error = quad(integrand, 0, 1000)
ic(result-50000)
ic((result-50000)/result)
print(f"Result: {result}, Estimated Error: {error}")

# self.__cr_templates[station_id][0][zen_ref][az_ref]
# 'templates_cr_station_{}.pickle'.format(station_id))
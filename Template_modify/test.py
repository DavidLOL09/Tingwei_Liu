

from astropy.io import fits
from icecream import ic
import os
import numpy as np
import matplotlib.pyplot as plt

# hdul2 = fits.open('/Users/david/Desktop/FOCexample.fits')
# ic(np.size(hdul2))
# hdul2.info( )
# img = fits.open('/Users/david/Desktop/FOCexample.fits')[0].data
# plt.style.use('_mpl-gallery-nogrid')

# make data with uneven sampling in x

x = np.array([0,1,2,3,4])
ic(np.linspace(0,len(x)-1,len(x)))
exit()
data = [[0, 'a'], [5, 'b'], [2, 'c']]

best = max(data, key=lambda x: x[0])
print(best)  # → [5, 'b']
import pandas as pd
exit()

# Option A: Labels from Dictionary keys
data = {
    'First Name': ['Alice', 'Bob'], 
    'Age': [25, 30],
    'Occupation': ['Engineer', 'Designer']
}
df = pd.DataFrame(data)

# Option B: Renaming columns of an existing DataFrame
df.columns = ['User_Name', 'User_Age', 'User_Job']

# Save to Excel
df.to_excel('labeled_data.xlsx', index=False)
exit()

x1=np.linspace(10,1000,991)
x2=np.logspace(1,5,901)
print(x2)
def func(x,kcons):
    return (2*kcons)*(np.pi/2-(np.arccos((4*x*140)/(4*x**2+140**2))))
y_lin=func(x1,1)
print(y_lin)
y_log=func(x2,1)
fig,axes=plt.subplots(1,2,figsize=(10,5),layout='constrained')
ax=axes[0]
ax.plot(x1,y_lin)
ax.set_xlabel(r'$E_\gamma$')
ax.set_ylabel(r'$\frac{dN_\gamma}{dE_\gamma}$',rotation='horizontal')
ax.set_title('linear')
ax.grid()

ax=axes[1]
ax.plot(x2,y_log)
ax.set_xlabel(r'$E_{\gamma}$')
ax.set_ylabel(r'$\frac{dN_\gamma}{dE_\gamma}$',rotation=0)
ax.set_title('log')
ax.set_xscale('log')
ax.grid()

plt.show()


import numpy as np
import matplotlib.pyplot as plt

# Constants
K_jupiter = 12.5  # m/s
P_jupiter = 11.86 # years
K_saturn = 2.76   # m/s
P_saturn = 29.5   # years

# Time setup (25 years)
t_model = np.linspace(0, 25, 1000)
t_obs = np.sort(np.random.uniform(0, 25, 500))

# Radial Velocity Function (Sum of Jupiter and Saturn)
# We assume arbitrary phases since they weren't specified, but distinct enough to show the effect.
def rv_sun(t):
    v_jup = K_jupiter * np.sin(2 * np.pi * t / P_jupiter)
    v_sat = K_saturn * np.sin(2 * np.pi * t / P_saturn + 2.0) # Offset phase for Saturn
    return v_jup + v_sat

# Generate Data
rv_true = rv_sun(t_model)
rv_obs_clean = rv_sun(t_obs)
noise = np.random.normal(0, 3.0, 500) # +/- 3 m/s Gaussian noise
rv_obs = rv_obs_clean + noise

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(t_model, rv_true, color='green', linewidth=2, label='True Sun RV (Jupiter + Saturn)')
plt.errorbar(t_obs, rv_obs, yerr=3.0, fmt='o', color='blue', alpha=0.5, markersize=3, label='Alien Observations (+/- 3 m/s error)')

plt.title("Radial Velocity of the Sun (Last 25 Years)")
plt.xlabel("Time (Years)")
plt.ylabel("Radial Velocity (m/s)")
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
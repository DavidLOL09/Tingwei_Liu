import numpy as np
from icecream import ic
sin2Val = np.arange(0, 1.01, 0.1)   #Bin edges evenly spaces in sin^2(angle) in radians
zen_bins = np.rad2deg(np.arcsin(np.sqrt(sin2Val))) 
ic(sin2Val)
ic(zen_bins)

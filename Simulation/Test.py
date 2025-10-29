from icecream import ic
import matplotlib.pyplot as plt
add_noise='False'
if add_noise=='False':
    add_noise=False
if add_noise=='True':
    add_noise==True
ic(add_noise)
if add_noise:
    ic(add_noise)
import numpy as np
num=100
a=np.linspace(-50,50,num)
error=np.random.normal(loc=0,scale=10,size=num)
def func(k,x):
    y=np.zeros_like(x,dtype=np.float64)
    for i in range(len(k)):
        ic(i)
        ic(k)
        print()
        y+=k[i]*(x**i)
    return y
k_lst=[6.7,95000,20000,70]
b=func(k_lst,a)+error


m=[[1,2,3,4],[1,2,3,4]]
ic(np.shape(m))
ic(np.sum(m,axis=0))
import pandas as pd

# Example: Creating a DataFrame from a dictionary
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'Los Angeles', 'Chicago']}
df = pd.DataFrame(data)
df.to_excel('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/my_data.xlsx', index=False)
# b1=func(k_lst,a)
# import polynomial_regression
# poly_reger = polynomial_regression.polynomial_regression()
# poly_reger.begin(len(k_lst)-1,a,b)
# coeff,new_err,err=poly_reger.run()
# ic(coeff,new_err,err)

# c=func(coeff,a)

# fig,ax=plt.subplots(1,1,figsize=(10,8))
# ax.scatter(a,b,alpha=0.3)
# ax.plot(a,c,label='regression',c='r',zorder=0)
# ax.plot(a,b1,label='real',zorder=-1,alpha=0.1)
# ax.legend()
# plt.show()
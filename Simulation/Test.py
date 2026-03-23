from icecream import ic
import matplotlib.pyplot as plt

add_noise='False'
if add_noise=='False':
    add_noise=False
if add_noise=='True':
    add_noise==True
# ic(add_noise)
if add_noise:
    ic(add_noise)
import numpy as np
num=100
a=np.linspace(15,21,num)
error=np.random.normal(loc=0,scale=3,size=num)
def func_poly(k,x):
    y=np.zeros_like(x,dtype=np.float64)
    for i in range(len(k)):
        y+=k[i]*(x**i)
    return y
# k_lst=[5000,8000,10000,15000]
# k_lst=[2,-110,2005,-12100]
k_lst = [-12100,2005,-110,2]
b=func_poly(k_lst,a)+error


# def begin(self, exp_max, x_lst, y_lst, coeff_start=[0,0,0,0], y_weights=None):

# Example: Creating a DataFrame from a dictionary
# data = {'Name': ['Alice', 'Bob', 'Charlie'],
#         'Age': [25, 30, 35],
#         'City': ['New York', 'Los Angeles', 'Chicago']}
# df = pd.DataFrame(data)
# df.to_excel('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/my_data.xlsx', index=False)
b1=func_poly(k_lst,a)
import polynomial_regression
poly_reger = polynomial_regression.polynomial_regression()
poly_reger.begin([0,1,2,3],a,b,regression='polynomial',demo_size=10,zoom=True,descent='Normal',learningR=1)
coeff,err,iteration,training_x=poly_reger.run()
ic(coeff,err,iteration)
ic(training_x[0]==training_x[1])
ic(np.shape(training_x))
c=func_poly(coeff,training_x[:,1])


fig,ax=plt.subplots(1,1,figsize=(10,8))
ax.scatter(a,b,alpha=0.3)
ax.plot(a,c,label='regression',c='r',zorder=0)
ax.plot(a,b1,label='real',zorder=-1,alpha=0.1)
ax.legend()
plt.show()



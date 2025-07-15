import numpy as np
import matplotlib.pyplot as plt

# Define a square matrix
e=0.2
A = np.array([[1,e,0,0],[e,2,e,0],[0,e,2,e],[0,0,e,1]])

# Compute eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

print("Eigenvalues:")
print(eigenvalues)
x=np.linspace(0,3,4)
print(x)
print("\nEigenvectors (each column is an eigenvector):")
target=eigenvectors/eigenvectors[0][0]
y1=target[:,0]
y2=target[:,1]
y3=target[:,2]
y4=target[:,3]
fig,ax=plt.subplots(2,2,figsize=(10,4))

ax[0][0].plot(x,y1,label=f'{eigenvalues[0]:.2f}')
ax[0][1].plot(x,y2,label=f'{eigenvalues[1]:.2f}')
ax[1][0].plot(x,y4,label=f'{eigenvalues[3]:.2f}')
ax[1][1].plot(x,y3,label=f'{eigenvalues[2]:.2f}')
for i in ax:
    for j in i:
        j.legend()
        j.grid()
plt.show()
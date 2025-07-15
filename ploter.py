import numpy as np
import matplotlib.pyplot as plt

# Create a grid of x and y values
x = np.linspace(-2, 2, 40)
y = np.linspace(-2, 2, 40)
X, Y = np.meshgrid(x, y)

# Avoid division by zero at the origin
epsilon = 1e-10
R_squared = X**2 + Y**2 + epsilon

# Scalar field
phi = 0.5 * np.log(R_squared)

# Compute gradient components
dphi_dx = X / R_squared
dphi_dy = Y / R_squared

# Plotting
plt.figure(figsize=(6,6))
plt.quiver(X, Y, dphi_dx, dphi_dy, color='blue')
plt.title(r'Gradient of $\phi(x, y) = \frac{1}{2} \ln(x^2 + y^2)$')
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.grid(True)
plt.show()


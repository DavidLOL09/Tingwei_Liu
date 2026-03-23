# import numpy as np
# from icecream import ic
# A=np.array([[1,2,3,4],
#             [1,2,3,4],
#             [1,2,3,4],
#             [1,2,3,4]])
# ic(A[:,2])
import matplotlib.pyplot as plt

def draw_abc_feynman_diagram():
    # Set up the figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # 1. Draw Incoming particles (Left side)
    ax.plot([-2, 0], [2, 0], color='blue', linewidth=2.5)   # Incoming A
    ax.plot([-2, 0], [-2, 0], color='green', linewidth=2.5) # Incoming B

    # 2. Draw Internal virtual particle (Middle)
    # Often, virtual particles are drawn with dashed lines
    ax.plot([0, 2], [0, 0], color='red', linestyle='--', linewidth=2.5) # Internal C

    # 3. Draw Outgoing particles (Right side)
    ax.plot([2, 4], [0, 2], color='blue', linewidth=2.5)    # Outgoing A
    ax.plot([2, 4], [0, -2], color='green', linewidth=2.5)  # Outgoing B

    # 4. Add labels for the particles
    ax.text(-1.5, 1.7, 'A', fontsize=16, color='blue', fontweight='bold')
    ax.text(-1.5, -1.7, 'B', fontsize=16, color='green', fontweight='bold')
    ax.text(1, 0.2, 'C (Virtual)', fontsize=14, color='red', fontweight='bold', ha='center')
    ax.text(3.5, 1.7, 'A', fontsize=16, color='blue', fontweight='bold')
    ax.text(3.5, -1.7, 'B', fontsize=16, color='green', fontweight='bold')

    # 5. Highlight the vertices (The most important part of ABC theory)
    ax.plot([0], [0], marker='o', color='black', markersize=8) # Vertex 1
    ax.plot([2], [0], marker='o', color='black', markersize=8) # Vertex 2

    # Annotate the vertices to show the rule is followed
    ax.text(0, -0.5, 'Vertex 1\n(A, B, C meet)', ha='center', fontsize=10, style='italic')
    ax.text(2, -0.5, 'Vertex 2\n(A, B, C meet)', ha='center', fontsize=10, style='italic')

    # 6. Clean up the plot (remove axes for a clean diagram look)
    ax.set_xlim(-3, 5)
    ax.set_ylim(-3, 3)
    ax.axis('off') 
    ax.set_title("Feynman Diagram: A + B -> A + B in Toy Model ABC", fontsize=16, pad=20)

    # Display the plot
    plt.tight_layout()
    plt.show()

# Run the function to generate the diagram
draw_abc_feynman_diagram()
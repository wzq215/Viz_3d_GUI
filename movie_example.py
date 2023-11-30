import pyvista as pv
import numpy as np

x = np.arange(-10, 10, 0.5)
y = np.arange(-10, 10, 0.5)
x, y = np.meshgrid(x, y)
r = np.sqrt(x**2 + y**2)
z = np.sin(r)

# Create and structured surface
grid = pv.StructuredGrid(x, y, z)
grid.plot()
# Create a plotter object and set the scalars to the Z height
plotter = pv.Plotter(notebook=False, off_screen=True)
plotter.add_mesh(
    grid,
    scalars=z.ravel(),
    lighting=False,
    show_edges=True,
    scalar_bar_args={"title": "Height"},
    clim=[-1, 1],
)

# Open a gif
plotter.open_gif("wave.gif")

pts = grid.points.copy()

# Update Z and write a frame for each updated position
nframe = 15
for phase in np.linspace(0, 2 * np.pi, nframe + 1)[:nframe]:
    z = np.sin(r + phase)
    pts[:, -1] = z.ravel()
    plotter.update_coordinates(pts, render=False)
    plotter.update_scalars(z.ravel(), render=False)

    # Write a frame. This triggers a render.
    plotter.write_frame()

# Closes and finalizes movie
plotter.show(interactive=True,auto_close=False,interactive_update=True,)
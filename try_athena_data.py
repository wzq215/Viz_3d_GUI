import numpy as np
import pyvista as pv
# from pyvistaqt import BackgroundPlotter
from pathlib import Path
from spacepy.pybats import IdlFile
# import vtk

filepath = './data/3D_5au_current_density_00.vtk'


file_path = Path(filepath)
pv_3d_data = pv.read(file_path)
# pv_3d_data = pv_3d_data.cell_data_to_point_data(progress_bar=True)
# %%
print(pv_3d_data.array_names)
pv_3d_data.set_active_scalars('density')
print(np.shape(pv_3d_data['density']))
print(np.shape(pv_3d_data['velocity']))
print(np.shape(pv_3d_data['pressure']))
print(np.shape(pv_3d_data['cell_centered_B']))
print(np.shape(pv_3d_data['current_density']))
print(np.shape(pv_3d_data['Zp']))
print(np.shape(pv_3d_data['Zm']))
# %%
print(pv_3d_data['current_density'])
pv_3d_data.set_active_vectors('current_density')
print(pv_3d_data.active_scalars)
p = pv.Plotter()
# p.add_mesh_slice_orthogonal(pv_3d_data)
# isos=pv_3d_data.contour(isosurfaces=10)
# p.add_mesh(isos)
stream, src = pv_3d_data.streamlines(return_source=True, source_radius=10., n_points=10,
                                       progress_bar=True, max_time=100.)
p.add_mesh(stream.tube(radius=0.1))
p.show()


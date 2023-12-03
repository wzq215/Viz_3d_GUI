import numpy as np
import pyvista as pv
# from pyvistaqt import BackgroundPlotter
from pathlib import Path
from spacepy.pybats import IdlFile
# import vtk

filepath = './data/output_5aunew/3D_5au_current_density_0017.vtk'


file_path = Path(filepath)
pv_3d_data = pv.read(file_path)
# pv_3d_data = pv_3d_data.cell_data_to_point_data(progress_bar=True)
# %%
print(pv_3d_data.array_names)
pv_3d_data.set_active_scalars('density')
# print(np.shape(pv_3d_data['density']))
# print(np.shape(pv_3d_data['velocity']))
# print(np.shape(pv_3d_data['pressure']))
# print(np.shape(pv_3d_data['cell_centered_B']))
# print(np.shape(pv_3d_data['current_density']))
# print(np.shape(pv_3d_data['Zp']))
# print(np.shape(pv_3d_data['Zm']))
# %%
# print(pv_3d_data['current_density'])
pv_3d_data.set_active_vectors('Zp')

p = pv.Plotter()
p.add_mesh_slice_orthogonal(pv_3d_data)
# isos=pv_3d_data.contour(isosurfaces=10)
# p.add_mesh(isos)
plane_mesh = pv.Plane(center=(1.5,1.5,1.5),direction=(0,0,1),i_size=3,j_size=3,i_resolution=30,j_resolution=30)
p.add_mesh(plane_mesh)
# reduced_mesh = pv_3d_data.decimate(0.9)
# stream, src = pv_3d_data.streamlines(return_source=True, source_center=(1.5,1.5,1.5),source_radius=1., n_points=100,
#                                        progress_bar=True, max_time=100.)
stream = pv_3d_data.streamlines_from_source(plane_mesh)
p.add_mesh(stream.tube(radius=0.01),color='w')
p.show_grid()
p.show()


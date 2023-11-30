import numpy as np
import pyvista as pv
# from pyvistaqt import BackgroundPlotter
from pathlib import Path
from spacepy.pybats import IdlFile
# import vtk

filepath = '/Users/ephe/THL8/OH_THC/box_mhd_5_n00020000.out'
var_select_lst = [None]

file_path = Path(filepath)
swmf_3d_data = IdlFile(file_path)
var_list = list(swmf_3d_data.keys())[4:]
unit_list = swmf_3d_data.meta['header'].split()[3:]
x = swmf_3d_data['x']
y = swmf_3d_data['y']
z = swmf_3d_data['z']
dimensions = swmf_3d_data['grid']
spacing = (abs(x[1] - x[0]), abs(y[1] - y[0]), abs(z[1] - z[0]))
origin = (x[0], y[0], z[0])

pv_3d_data = pv.UniformGrid(dimensions=(dimensions[0], dimensions[1], dimensions[2]), spacing=spacing,
                               origin=origin)
if var_select_lst == [None]:
    var_select_lst = var_list
print(var_list)
print(unit_list)
var_bin = [var in var_select_lst for var in var_list]
unit_select_lst = np.array(unit_list)[var_bin]
for var_str in var_select_lst:
    print(var_str)
    pv_3d_data.point_data[var_str] = np.array(swmf_3d_data[var_str]).ravel('F')
print('Reading SWMF output from: '+filepath)
print('var_list: ', var_select_lst)
print('unit_list: ', unit_select_lst)


p = pv.Plotter()
p.add_mesh_slice_orthogonal(pv_3d_data)
isos=pv_3d_data.contour(isosurfaces=10)
p.add_mesh(isos)
p.show()


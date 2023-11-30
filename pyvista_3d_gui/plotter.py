from pathlib import Path
import numpy as np
import pyvista as pv
from spacepy.pybats import IdlFile
class TresPlotter:
    def __init__(self):
        self._plotter = pv.Plotter()
        self.camera = self._plotter.camera
        self.all_meshes={}

    def plotter(self):
        return self._plotter

    def show(self,*args,**kwargs):
        self._plotter.show(*args,**kwargs)

    def _add_mesh_to_dict(self,block_name,mesh):
        if block_name in self.all_meshes:
            self.all_meshes[block_name].append(mesh)
        else:
            self.all_meshes[block_name] = [mesh]

    def save(self, filepath, *, overwrite=False):
        file_path = Path(filepath)
        directory_path = file_path.with_suffix("")

        if not overwrite:
            if file_path.is_file():
                raise ValueError(
                    f"VTM file '{directory_path.absolute()}' already exists",
                )
        if directory_path.exists():
            raise ValueError(f"Directory '{directory_path.absolute()}' already exists")

        mesh_block = pv.MultiBlock()
        for objects in self.all_meshes:
            for meshes in self.all_meshes[objects]:
                mesh_block.append(meshes)
        mesh_block.save(file_path)

    def _loop_through_meshes(self,mesh_block):
        for block in mesh_block:
            if isinstance(block,pv.MultiBlock):
                self._loop_through_meshes(block)
            else:
                color = dict(block.field_data).get('color',None)
                cmap = dict(block.field_data).get('cmap',[None])[0]
                self.plotter.add_mesh_slice_orthogonal(block,color=color,cmap=cmap)

    def load(self,filepath):
        file_path = Path(filepath)
        mesh_block = pv.read(file_path)
        self._loop_through_meshes(mesh_block)

    def load_swmf_box_data(self, filepath, var_select_lst=[None]):
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
        self._add_mesh_to_dict(block_name='swmf_box',mesh=pv_3d_data)
        print('Reading SWMF output from: '+filepath)
        print('var_list: ', var_select_lst)
        print('unit_list: ', unit_select_lst)
        return pv_3d_data




    def plot_orthogonal_slices(self, mesh, **kwargs):
        self.plotter().add_mesh_slice_orthogonal(mesh)
        print(self._plotter.plane_sliced_meshes)
        self._add_mesh_to_dict(block_name='ortho_slices',mesh=mesh)




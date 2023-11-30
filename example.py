from pyvista_3d_gui import TresPlotter


filepath = '/Users/ephe/THL8/OH_THC/box_mhd_5_n00020000.out'
plotter = TresPlotter()
pv_data = plotter.load_swmf_box_data(filepath=filepath,var_select_lst=['Rho'])
plotter.plot_orthogonal_slices(pv_data)
# print(plotter.plane_sliced_meshes)
isos = pv_data.contour(isosurfaces=10,rng=[0.01,0.09])
plotter.add_mesh(isos)
plotter.show()

import sys

# Setting the Qt bindings for QtPy
import os

os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QMovie

from pathlib import Path
import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor, MainWindow
from spacepy.pybats import IdlFile


# import vtkmodules.all as vtk

class MyMainWindow(MainWindow):

    def __init__(self, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.resize(1200, 600)
        self.setWindowTitle('3D Visualization (TEST)')

        self.filePath_lst = []
        self.mainFilePath = ''
        self.pv_mesh = None
        self.do_plot_slice = True
        self.do_plot_isos = False
        self.do_plot_streamlines = False

        self.var_lst = []
        self.scalar_lst = []
        self.vector_lst = []
        self.active_scalar = ''
        self.active_vector = ''

        # create the frame
        self.frame = QtWidgets.QFrame()
        leftBox = QtWidgets.QVBoxLayout()


        # Edit Left Box
        # leftBox-fileBox
        fileBox = QtWidgets.QVBoxLayout()
        fileBox_upper = QtWidgets.QHBoxLayout()

        self.label_filename = QtWidgets.QLabel('Loaded Files: ', )
        btn_delFile = QtWidgets.QPushButton('Delete')
        btn_delFile.clicked.connect(self.delete_file)
        fileBox_upper.addWidget(self.label_filename)
        fileBox_upper.addWidget(btn_delFile)

        self.fileList = QtWidgets.QListWidget()
        self.fileList.itemClicked.connect(self.select_main_file)
        splitter1 = QtWidgets.QSplitter(Qt.Horizontal)
        fileBox.addLayout(fileBox_upper)
        fileBox.addWidget(self.fileList)
        fileBox.addWidget(splitter1)

        # leftBox.addWidget(splitter1)
        label_varScalar = QtWidgets.QLabel('Select Scalar: ', )
        self.varScalarCombo = QtWidgets.QComboBox()
        self.varScalarCombo.currentIndexChanged.connect(self.set_scalar)

        btn_slice = QtWidgets.QCheckBox('Plot Slices')
        btn_slice.setChecked(True)
        btn_slice.toggled.connect(self.btn_slice_click)

        isosBox = QtWidgets.QHBoxLayout()
        btn_isos = QtWidgets.QCheckBox('Plot Isosurfaces')
        btn_isos.setChecked(False)
        btn_isos.toggled.connect(self.btn_isos_click)
        label_isos_n = QtWidgets.QLabel('Number')
        self.isos_n = 1
        intInput_isos = QtWidgets.QLineEdit()
        intInput_isos.setPlaceholderText('1')
        int_validator = QIntValidator(1, 10, self)
        intInput_isos.setValidator(int_validator)
        intInput_isos.textChanged.connect(self.set_isos_n)
        isosBox.addWidget(btn_isos)
        isosBox.addWidget(label_isos_n)
        isosBox.addWidget(intInput_isos)

        # leftBox.addWidget(self.label_filename)
        leftBox.addLayout(fileBox)
        leftBox.addWidget(label_varScalar)
        leftBox.addWidget(self.varScalarCombo)
        leftBox.addWidget(btn_slice)
        leftBox.addLayout(isosBox)

        splitter2 = QtWidgets.QSplitter(Qt.Horizontal)
        leftBox.addWidget(splitter2)

        label_varVector = QtWidgets.QLabel('Select Vector: ', )
        self.varVectorCombo = QtWidgets.QComboBox()
        self.varVectorCombo.currentIndexChanged.connect(self.set_vector)

        streamlineBox = QtWidgets.QHBoxLayout()

        btn_stream = QtWidgets.QCheckBox('Plot Streamlines')
        btn_stream.setChecked(False)
        btn_stream.toggled.connect(self.btn_stream_click)

        label_stream_n = QtWidgets.QLabel('Src Point Number')
        self.stream_n = 10
        intInput_stream = QtWidgets.QLineEdit()
        intInput_stream.setPlaceholderText('10')
        int_validator = QIntValidator(1, 100, self)
        intInput_stream.setValidator(int_validator)
        intInput_stream.textChanged.connect(self.set_stream_n)

        label_stream_src_radius = QtWidgets.QLabel('Src Sphere Radius')
        self.stream_src_radius = 1.
        dblInput_stream_src_radius = QtWidgets.QLineEdit()
        dblInput_stream_src_radius.setPlaceholderText('1.')
        dbl_validator = QDoubleValidator()
        dblInput_stream_src_radius.setValidator(dbl_validator)
        dblInput_stream_src_radius.textChanged.connect(self.set_stream_src_radius)

        streamlineBox.addWidget(btn_stream)
        streamlineBox.addWidget(label_stream_n)
        streamlineBox.addWidget(intInput_stream)
        streamlineBox.addWidget(label_stream_src_radius)
        streamlineBox.addWidget(dblInput_stream_src_radius)

        leftBox.addWidget(label_varVector)
        leftBox.addWidget(self.varVectorCombo)
        leftBox.addLayout(streamlineBox)

        plotBox = QtWidgets.QHBoxLayout()
        btn_plot = QtWidgets.QPushButton('PLOT')
        btn_plot.clicked.connect(self.update_plotter)

        btn_animate = QtWidgets.QPushButton('ANIMATE')
        btn_animate.clicked.connect(self.plot_movie)

        plotBox.addWidget(btn_plot)
        plotBox.addWidget(btn_animate)

        leftBox.addLayout(plotBox)

        self.logOutput = QtWidgets.QLabel('Welcome!')
        leftBox.addWidget(self.logOutput)


        self.centerBox = QtWidgets.QVBoxLayout()
        # add the pyvista interactor object
        self.plotter = QtInteractor(self.frame)
        # self.plotter.theme = pv.themes.DocumentTheme()
        self.centerBox.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)



        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addLayout(leftBox)
        hlayout.addLayout(self.centerBox)
        # hlayout.addWidget(self.stackedWidget)
        #
        self.frame.setLayout(hlayout)
        self.setCentralWidget(self.frame)


        # simple menu to demo functions
        mainMenu = self.menuBar()
        # file loader
        fileMenu = mainMenu.addMenu('File')
        # SWMF .out
        self.load_swmf_file_action = QtWidgets.QAction('Load SWMF File (*.out)', self)
        self.load_swmf_file_action.triggered.connect(self.load_swmf_file)
        fileMenu.addAction(self.load_swmf_file_action)
        # .vtk
        self.load_vtk_file_action = QtWidgets.QAction('Load VTK File (*.vtk)', self)
        self.load_vtk_file_action.triggered.connect(self.load_mhd_athena_file)
        fileMenu.addAction(self.load_vtk_file_action)

        # TODO: ADD SAVE STL / SNAPSHOT

        exitButton = QtWidgets.QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        if show:
            self.show()

    # +++++++++++++++++ LOAD & READ ++++++++++++++++ #
    def _add_mesh_to_self(self, mesh):
        self.pv_mesh = mesh

    def load_mhd_athena_file(self):
        filePath_lst, filetype = QtWidgets.QFileDialog.getOpenFileNames(self, "Load", "./", "*.vtk")
        self.filePath_lst = filePath_lst
        self.mainFilePath = filePath_lst[0]
        self._print('Loading Files from ' + '\n'.join(self.filePath_lst))
        self._print_filenames()
        self._create_file_lst()
        self.read_mhd_athena_data()
        self.do_plot_slice = True

    def read_mhd_athena_data(self):
        self.pv_mesh = pv.read(self.mainFilePath)
        self.var_lst = self.pv_mesh.array_names
        self.scalar_lst = []
        self.vector_lst = []
        for var in self.var_lst:
            if len(np.shape(self.pv_mesh[var])) == 1:
                self.scalar_lst.append(var)
            elif len(np.shape(self.pv_mesh[var])) == 2:
                self.vector_lst.append(var)
        self.active_scalar = self.scalar_lst[0]
        self.active_vector = self.vector_lst[0]
        self._create_combo_lst()
        self.update_plotter()

    def load_swmf_file(self):
        filePath_lst, filetype = QtWidgets.QFileDialog.getOpenFileNames(self, "Load", "./", "*.out")
        self.filePath_lst = filePath_lst
        self.mainFilePath = filePath_lst[0]
        self._print('Loading Files from ' + '\n'.join(self.filePath_lst))
        self._print_filenames()
        self._create_file_lst()
        self.read_swmf_box_data()
        self.do_plot_slice = True

    def read_swmf_box_data(self):
        file_path = Path(self.mainFilePath)
        swmf_3d_data = IdlFile(file_path)
        var_list = list(swmf_3d_data.keys())[4:]
        unit_list = swmf_3d_data.meta['header'].split()[3:]

        print(var_list)
        print(unit_list)

        self.scalar_lst = []
        self.vector_lst = []

        x = swmf_3d_data['x']
        y = swmf_3d_data['y']
        z = swmf_3d_data['z']
        dimensions = swmf_3d_data['grid']
        spacing = (abs(x[1] - x[0]), abs(y[1] - y[0]), abs(z[1] - z[0]))
        origin = (x[0], y[0], z[0])

        pv_3d_data = pv.UniformGrid(dimensions=(dimensions[0], dimensions[1], dimensions[2]), spacing=spacing,
                                    origin=origin)

        var_list_lower = [varname.lower() for varname in var_list]

        skip_indexs = []
        for i in range(len(var_list)):
            if i in skip_indexs:
                continue

            var_tmp = var_list[i]
            var_tmp_lower = var_list_lower[i]
            # CAUTION: 此处假设了x总是出现在y，z的前面
            if var_tmp_lower[-1] == 'x':
                print('Find x in '+var_tmp)
                try:
                    j = var_list_lower.index(var_tmp_lower[:-1] + 'y')
                    k = var_list_lower.index(var_tmp_lower[:-1] + 'z')

                    vec_tmp_x_name = var_tmp
                    vec_tmp_y_name = var_list[j]
                    vec_tmp_z_name = var_list[k]

                    vec_tmp_name = var_tmp[:-1]
                    if unit_list:
                        vec_unit_tmp = vec_tmp_name + ' (' + unit_list[i] + ')'
                    else:
                        vec_unit_tmp = vec_tmp_name

                    vec_tmp_x = swmf_3d_data[vec_tmp_x_name].ravel('F')
                    vec_tmp_y = swmf_3d_data[vec_tmp_y_name].ravel('F')
                    vec_tmp_z = swmf_3d_data[vec_tmp_z_name].ravel('F')

                    skip_indexs.append(j)
                    skip_indexs.append(k)

                    vec_tmp = np.vstack([vec_tmp_x, vec_tmp_y, vec_tmp_z]).T
                    pv_3d_data.point_data[vec_unit_tmp] = vec_tmp

                    self.vector_lst.append(vec_unit_tmp)
                except:
                    self._print('Failed to find -y, -z var for ' + var_tmp + ', treat as scalar.')
                    if unit_list:
                        var_unit_tmp = var_tmp + ' (' + unit_list[i] + ')'
                    else:
                        var_unit_tmp = var_tmp
                    pv_3d_data.point_data[var_unit_tmp] = np.array(swmf_3d_data[var_tmp]).ravel('F')
                    self.scalar_lst.append(var_unit_tmp)
            else:
                if unit_list:
                    var_unit_tmp = var_tmp + ' (' + unit_list[i] + ')'
                else:
                    var_unit_tmp = var_tmp
                pv_3d_data.point_data[var_unit_tmp] = np.array(swmf_3d_data[var_tmp]).ravel('F')
                self.scalar_lst.append(var_unit_tmp)

        self.var_lst = self.scalar_lst + self.vector_lst
        self._create_combo_lst()
        self._add_mesh_to_self(pv_3d_data)
        self.update_plotter()

    # ++++++++++++++++++++ PLOT ++++++++++++++++++++
    def plot_3d_slices(self, mesh):
        self._print('Plotting Slice ...')
        self.plotter.add_mesh_slice_orthogonal(mesh)
        self.plotter.reset_camera()

    def plot_isosurfaces(self, mesh, ):
        self._print('Plotting Isosurfaces ...')
        isos_mesh = mesh.contour(isosurfaces=self.isos_n, rng=[0., 0.09])
        self.plotter.add_mesh(isos_mesh, opacity=0.5)
        # self.plotter.reset_camera()

    def plot_streamlines(self, mesh):
        self._print('Plotting Streamlines ...')
        stream, src = mesh.streamlines(return_source=True, source_radius=self.stream_src_radius, n_points=self.stream_n,
                                       progress_bar=True)
        self.plotter.add_mesh(stream.tube(radius=1.), color='silver')
        # self.plotter.reset_camera()

    # +++++++++++++++++++ UPDATE +++++++++++++++++++
    def update_plotter(self):
        # self.stackedWidget.setCurrentIndex(0)
        # try:
        #     self.centerBox.removeWidget(self.movieLabel)
        #     # self.movieLabel.close()
        #     self.plotter = QtInteractor(self.frame)
        #     self.centerBox.addWidget(self.plotter.interactor)
        #
        # except Exception as e:
        #     self._print(str(e))
        #     pass
        print(self.plotter.interactor)
        # self.plotter = QtInteractor(self.frame)
        # self.stackedWidget.addWidget(self.plotter.interactor)

        # self.plotter.show()

        self.plotter.clear()
        try:
            self.centerBox.removeWidget(self.movieLabel)
            self.movieLabel.deleteLater()
        except:
            print('NOTHING TO BE DELETED')
            pass

        try:
            self.plotter.add_axes()
        except:
            self.plotter = QtInteractor(self.frame)
            self.centerBox.addWidget(self.plotter.interactor)
            self.plotter.add_axes()


        self.pv_mesh.set_active_scalars(self.active_scalar)
        self.pv_mesh.set_active_vectors(self.active_vector)

        if self.do_plot_isos:
            try:
                self.plot_isosurfaces(self.pv_mesh)
            except Exception as e:
                print(str(e))

        if self.do_plot_streamlines:
            try:
                self.plot_streamlines(self.pv_mesh)
            except Exception as e:
                print(str(e))

        if self.do_plot_slice:
            # try:
            self.plot_3d_slices(self.pv_mesh)
            # except Exception as e:
            #     print(str(e))


        self.plotter.show_grid()

        self._print('Done!')

    def plot_movie(self):

        self._print('Generating Movie ...')
        # if Path('./movie.gif').exists():
        #     Path('./movie.gif').unlink()
        self.plotter.open_gif('./movie.gif')
        nframe = len(self.filePath_lst)
        print(nframe)
        for i in range(nframe):
            self.mainFilePath = self.filePath_lst[i]
            self.set_main_file()
            self.plotter.write_frame()
        self.plotter.close()
        # self.plotter.deleteLater()
        self._print('Movie Generated!')
        self.play_movie()

    def play_movie(self):
        # self.stackedWidget.setCurrentIndex(1)
        self.movieLabel = QtWidgets.QLabel()
        moviemovie = QMovie('./movie.gif')
        self.movieLabel.setMovie(moviemovie)
        moviemovie.start()
        self.centerBox.addWidget(self.movieLabel)
        self._print('Movie Started!')

    def set_scalar(self):
        self.active_scalar = self.varScalarCombo.currentText()
        self._print('Setting Active Scalar to ' + self.varScalarCombo.currentText())

    def set_vector(self):
        self.active_vector = self.varVectorCombo.currentText()
        self._print('Setting Active Vector to ' + self.varVectorCombo.currentText())

    def btn_slice_click(self, ):
        self.do_plot_slice = self.sender().isChecked()
        if self.sender().isChecked():
            self._print('Plot Slices Checked.')
        else:
            self._print('Plot Slices Cancelled.')

    def btn_isos_click(self, ):
        self.do_plot_isos = self.sender().isChecked()
        if self.sender().isChecked():
            self._print('Plot Isosurfaces Checked.')
        else:
            self._print('Plot Isosurfaces Cancelled.')

    def set_isos_n(self):
        self.isos_n = int(self.sender().text())

    def btn_stream_click(self):
        self.do_plot_streamlines = self.sender().isChecked()
        if self.sender().isChecked():
            self._print('Plot Streamlines Checked.')
        else:
            self._print('Plot Streamlines Cancelled.')

    def set_stream_n(self):
        self.stream_n = int(self.sender().text())

    def set_stream_src_radius(self):
        self.stream_src_radius = float(self.sender().text())

    def set_main_file(self):
        if self.mainFilePath == []:
            self._print('Please load files.')
            return
        try:
            # self.mainFilePath = self.sender().selectedItems()[0].text()
            f = Path(self.mainFilePath)
            if f.suffix == '.out':
                self.read_swmf_box_data()
                self._print('Select ' + self.mainFilePath + '. Treat as SWMF file.')
            elif f.suffix == '.vtk':
                self.read_mhd_athena_data()
                self._print('Select ' + self.mainFilePath + '. Treat as MHD athena file.')
        except Exception as e:
            self._print(str(e))

    def select_main_file(self):
        self.mainFilePath = self.sender().selectedItems()[0].text()
        self.set_main_file()

    def delete_file(self):
        item = self.fileList.currentItem()
        self.filePath_lst.pop(self.fileList.row(item))
        self.fileList.takeItem(self.fileList.row(item))
        self.pv_mesh = None
        self.plotter.clear()
        self.varScalarCombo.clear()
        self.varVectorCombo.clear()
        self.var_lst = []
        self.scalar_lst = []
        self.vector_lst = []
        if self.fileList.currentItem():
            self.mainFilePath = self.fileList.currentItem().text()
        else:
            self.mainFilePath = []
        self.set_main_file()
        self._print_filenames()

    # +++++++++++++++++++ MESSAGE +++++++++++++++++++
    def _print(self, message_str):
        self.logOutput.setText(message_str)

    def _print_filenames(self):
        self.label_filename.setText('File Loaded. N_files = ' + str(len(self.filePath_lst)) + '.')

    def _create_file_lst(self):
        self.fileList.addItems(self.filePath_lst)

    def _create_combo_lst(self):
        self.varScalarCombo.clear()
        self.varVectorCombo.clear()
        self.varScalarCombo.addItems(self.scalar_lst)
        self.varVectorCombo.addItems(self.vector_lst)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())

# Time Stepping
# STATIC 3D
# ANIMATED GIF
# 测试机器的win版本，打包成静态的安装文件，
# 操作说明
# 测试大纲

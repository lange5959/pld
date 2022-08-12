# -*- coding: utf-8 -*-
# Time    : 2021/6/15 11:40
# Author  : MengWei

import os
import sys
import re
import tempfile
import shutil
import getpass
import contextlib
import traceback
import time
from datetime import datetime

from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm
import maya.mel as mel

# import pipe_utils as pipe
# from maya_tools.utils import get_maya_main_window
# from pipe_utils import ffm
import ffm
reload(ffm)
# from pipe_utils import parser
import utils
reload(utils)
from utils import get_next_available_version
# from variables import width, height
width, height = 2048, 1028
from utils import load_config

__version__ = 'v1.1.6'


def playblast_maya(output, w, h, start, end):
    pm.playblast(compression="jpg",
                 format="image",
                 viewer=False,
                 framePadding=4,
                 quality=100,
                 widthHeight=[w, h],
                 showOrnaments=False,
                 clearCache=0,
                 sequenceTime=False,
                 offScreen=False,
                 fp=4,
                 percent=100,
                 filename=output,
                 startTime=start,
                 endTime=end)

    # pm.playblast(startTime=start_frame, endTime=end_frame,
    #              format="image", filename=imageName,
    #              forceOverwrite=True, offScreen=offScreen,
    #              sequenceTime=0, clearCache=False,
    #              viewer=False, showOrnaments=True, fp=4,
    #              percent=100, compression=img_ext,
    #              widthHeight=wh, quality=100)

def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def get_fps():

    unit = pm.currentUnit(query=True, time=True)

    fps_by_unit = {
        'film': 24.0,
        'pal': 25.0,
        '29.97fps': 29.97,
        'ntsc': 30.0,
        '59.94fps': 59.94,
    }
    return fps_by_unit.get(unit)


@contextlib.contextmanager
def applied_view(cam, panel, options):
    """Apply options to panel"""

    original = {}
    for key in options:
        original[key] = pm.modelEditor(
            panel, query=True, **{key: True})
    pm.modelEditor(panel, edit=True, **options)
    ct = pm.currentTime()
    try:
        yield
    finally:
        pm.modelEditor(panel, edit=True, **original)
        pm.lookThru(cam)
        pm.currentTime(ct)


def get_sound(fps, start):
    """
    sound_offset--second
    Args:
        fps:
    Returns: sound_path(str), sound_offset(float)
    """
    sound_path = None
    sound_offset = 0
    sounds = pm.ls(type='audio')
    if not sounds:
        return sound_path, sound_offset, None
    time_control = mel.eval("$gPlayBackSlider = $gPlayBackSlider")
    sound_name = pm.timeControl(time_control, query=True, sound=True)
    sounds = [sound for sound in sounds if sound.name() == sound_name]
    sound = next(iter(sounds), None)
    if sound:
        sound_path = sound.getAttr('filename')
        sound_offset = sound.getAttr('offset')
        if os.path.exists(sound_path):
            # sound_offset--second
            return sound_path, float(start-sound_offset)/fps, sound_offset

    return None, None, None


def mov_output_path(output_dir, name):
    mov_dir = os.path.join(output_dir, 'playblast').replace('\\', '/')
    if not os.path.exists(mov_dir):
        os.makedirs(mov_dir)
    name = os.path.splitext(name)[0]
    mov_output = os.path.join(mov_dir, name+'.mov').replace('\\', '/')
    if os.path.exists(mov_output):
        mov_output = get_next_available_version(mov_output)
    return mov_output


class UI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        self.setWindowTitle('Playblast_{}'.format(__version__))
        self.resize(500, 100)

        main_layout = QtWidgets.QVBoxLayout(self)
        pb_btn = QtWidgets.QPushButton(u'开始拍屏')
        pb_btn.setStyleSheet(
            "QPushButton{border:1px solid gray; color:white; "
            "font-family: \"微软雅黑\"; font-size: 15px}"
            "QPushButton:hover{background:skyblue; }"
        )

        output_layout = QtWidgets.QHBoxLayout()
        output_label = QtWidgets.QLabel(u'输出位置:')
        output_label.setStyleSheet(
            "QLabel{border:1px solid gray; color:white; "
            "font-family: \"微软雅黑\"; font-size: 15px}"
        )
        self.output_lineedit = QtWidgets.QLineEdit()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_lineedit)
        self.current_file = str(pm.sceneName())
        ma_name = os.path.basename(self.current_file)
        self.version_name = os.path.splitext(ma_name)[0]
        self.output_lineedit.setText(os.path.dirname(self.current_file))
        self.pbar = QtWidgets.QProgressBar(self)

        self.wm_checkbox = QtWidgets.QCheckBox(u'加水印')

        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.wm_checkbox)
        main_layout.addWidget(self.pbar)
        main_layout.addWidget(pb_btn)
        pb_btn.clicked.connect(self.run)

    def add_wm(self, maya_output_parent, output_ffm):
        """
        add water mark to images
        Args:
            maya_output_parent:
            output_ffm:

        Returns:

        """
        imgs = os.listdir(maya_output_parent)
        imgs_len = len(imgs)
        progress_step = 0
        for img in imgs:
            progress_step += 1
            input = os.path.join(
                maya_output_parent, img
            ).replace('\\', '/')
            ffm_img_output = os.path.join(
                output_ffm, img).replace('\\', '/')
            # 从图片读取当前帧号
            frame = re.search('\w+\.(\d{4})\.\w+', img).group(1)
            args = {
                'camera': self.version_name,
                'frame_num': int(self.frame_num),
                'time_code': self.time_code,
                'frame': str(frame),
                # 'user': self.user,
                'focal_length': self.fl,
            }
            ffm.img2img(input, ffm_img_output, args)
            self.pbar.setValue(progress_step * 100 / imgs_len)

    def run(self):
        # todo: 可选是否加水印
        fps = get_fps()
        # todo: set local mov output position

        # todo: 后加水印，保留images, 后续单独再加水印
        wm = self.wm_checkbox.isChecked()
        # if wm:
        #     print '='*100
        # wm = True
        output = self.output_lineedit.text().strip()
        cam = pm.ui.PyUI(pm.playblast(activeEditor=True)).getCamera()
        start, end = map(
            int,
            [pm.playbackOptions(query=True, minTime=True),
             pm.playbackOptions(query=True, maxTime=True)]
        )

        # 路径中不能有空格；不能中英文混用
        if ' ' in output:
            raise Exception(u'当前输出路径中有空格，建议去掉')
        mov_output = mov_output_path(output, os.path.basename(self.current_file))

        # options = load_config('playblast/maya_playblast.yaml', 'Test')['ViewportOptions']
        options = load_config(
            'playblast/maya_playblast.yaml',
            'Test'
        )['ViewportOptions']
        options['shadows'] = True

        # self.user = getpass.getuser()
        panel = pm.ui.PyUI(pm.playblast(activeEditor=True)).shortName()
        temp_dir = os.path.join(tempfile.gettempdir(), 'playblast')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        with applied_view(cam, panel, options):
            # cam.setDisplayGateMask(False)
            cam.setDisplayGateMask(True)
            # todo: focalLength可能有动画
            self.fl = cam.getAttr('focalLength')

            try:
                pm.setAttr(cam + '.overscan', lock=False)
                pm.setAttr(cam + '.overscan', 1.0)
            except:
                pass

            camera_name = cam.name()
            self.camera_name = camera_name
            pm.lookThru(camera_name)
            self.time_code = datetime.now().strftime(
                '%Y/%m/%d %H\\\\:%M\\\\:%S')
            maya_output = os.path.join(temp_dir, 'maya_out', 'pb')
            maya_output_parent = os.path.dirname(maya_output)
            self.frame_num = end - start + 1
            sound_path, sound_offset, sound_offset_sec = get_sound(fps, start)
            print(sound_path, sound_offset, sound_offset_sec)
            if is_contain_chinese(unicode(sound_path)):
                raise Exception(u'音频路径不能中英文混用')
            # pm.playblast
            playblast_maya(maya_output, width, height, start, end)
            start_code = time.time()
            img_dir = maya_output_parent
            output_ffm = os.path.join(temp_dir, 'ffm_out')
            if not os.path.exists(output_ffm):
                os.makedirs(output_ffm)
            if wm:
                # add water mark to images
                self.add_wm(maya_output_parent, output_ffm)
                img_dir = output_ffm
            # maya_output_parent
            input = os.path.join(
                img_dir,
                'pb.%04d.jpg').replace('\\', '/')
            # mov_output = mov_output_path(output, self.current_file)
            comment = '"{}-{} {} {} {}"'.format(
                start, end, self.current_file, sound_path, sound_offset_sec)
            ffm.seq2mov(
                input,
                mov_output,
                fps=fps,
                start=start,
                sound_path=sound_path,
                frame_num=self.frame_num,
                sound_offset=sound_offset,
                comment=comment
            )
            try:
                os.startfile(mov_output)
            except:
                traceback.print_exc()
            print(time.time()-start_code, '<<<time cost')
            # if os.path.exists(temp_dir):
            #     shutil.rmtree(temp_dir)
        # end with


def main():
    import pymel.core as pm
    mayaWindow = pm.ui.Window('MayaWindow')
    mayaQtWindow = mayaWindow.asQtObject()

    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    ex = UI(None)
    ex.setParent(mayaQtWindow)
    ex.setWindowFlags(QtCore.Qt.Window)
    ex.show()

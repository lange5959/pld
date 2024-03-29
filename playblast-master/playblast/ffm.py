# -*- coding: utf-8 -*-

import os
import subprocess
import getpass

import load_xml
from PySide2 import QtGui
import utils
reload(utils)
from utils import load_config

current_path = os.path.dirname(__file__)
FFMPEG = r'W:\home\mengwei1\software\Tools\ffmpeg.exe'.replace('\\', '/')
xml_full_path = os.path.join(current_path, 'playblast\drawtext.xml').replace('\\', '/')


def scale_image(path, factor=0.5):

    image = QtGui.QImage(path)
    return image.width() * factor, image.height() * factor


def font_path():
    font_name = 'fonts/msyh2.ttc'
    font_path = os.path.join(current_path, font_name)
    return font_path.split(':')[0]+'\\\\:'+font_path.split(':')[1].replace(
        '\\', '/')


class Base(object):
    def __init__(self):
        super(Base, self).__init__()

        # self.user = 'Jack'
        self.user = getpass.getuser()
        self.commit = 'Hello world!'
        self.ffm_path = r'W:\home\mengwei1\software\Tools\ffmpeg.exe'.replace('\\', '/')


class Drawtext(Base):
    def __init__(self, text=None, position=None, fontsize=20, margin=10):
        super(Drawtext, self).__init__()

        self.position = position
        self.fontsize = fontsize
        self.text = text
        self.drawtext_position = {
            u'TopLeft': u'x={}:y={}'.format(margin, margin),
            u'TopCenter': u'x=(w-text_w)/2:y={}'.format(margin),
            u'TopRight': u'x=w-tw-{}:y={}'.format(margin, margin),
            u'BottonCenter': u'x=w-w/2-text_w/2: y=h-th-{}'.format(margin),
            u'BottonLeft': u'x={}:y=h-th-{}'.format(margin, margin),
            u'BottonRight': u'x=w-tw-{}:y=h-th-{}'.format(margin, margin),
            u'Centered': u'x=(w-text_w)/2:y=(h-text_h)/2',
        }

    def font_string(self, t=None, p=None, s=None):
        """ build font string
        Args:
            t: text
            p: position
            s: size

        Returns: drawtext string
        """
        # font： msyhbd.ttc(微软雅黑-粗体)， msyh.ttc(微软雅黑-常规)， msyhl.ttc(微软雅黑-细体)
        drawtext =u"drawtext=fontfile={fontfile}:text={text}: " \
                   u"{pos}: fontcolor=white :fontsize={fontsize}: " \
                   u"box=1: boxcolor=0x00000099: ".format(
            pos=self.drawtext_position[p or self.position],
            text=t.decode('gbk') or self.text,
            fontsize=s, fontfile=font_path(),
        )
        return drawtext

    def load_string_xml(self, xml_path='playblast/drawtext.xml'):
        # return load_config(xml_path, '')['submenu']
        return utils.load_xml_ffm(xml_full_path)['submenu']

    def font_strings(self, args):
        """drawtext strings all together

        Args:
            args (dict):

        Returns (string): drawtexts

        """
        if not args.get('user'):
            args['user'] = self.user
        drawtexts = []
        for info in self.load_string_xml():
            drawtext = self.font_string(
                info['text'],
                info['position'],
                info['size'],
            ).format(**args)

            drawtexts.append(drawtext)
        drawtext = '[a];[a]'.join(drawtexts)
        return u'\"{}\"'.format(drawtext)


class Watermark(Base):
    def __init__(self, pos='TopRight', scale=None, alpha=0.3, margin=10):
        super(Watermark, self).__init__()

        # w  tw, h  th
        # main_w  overlay_w, main_h, overlay_h
        self.watermark_path = ''
        self.watermark_position = {
            'TopLeft': 'x={}:y={}'.format(margin, margin),
            'TopCenter': 'x=(main_w-overlay_w)/2:y={}'.format(margin),
            'Middle': 'x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2',
            'TopRight': 'x=main_w-overlay_w-{}:y={}'.format(margin, margin),
            'BottonLeft': 'x={}:y=main_h-overlay_h-{}'.format(margin, margin),
            'BottonCenter': 'x=(main_w-overlay_w)/2:y=main_h-overlay_h-{}'.format(
                margin),
            'BottonRight': 'x=main_w-overlay_w-{}:y=main_h-overlay_h-{}'.format(
                margin, margin),
        }

        self.wm_pos = self.watermark_position[pos]
        self.wm_cmd = "[1:v]scale={scale}[img1];" \
                 "[img1]lut=a=val*{alpha}[a];" \
                 "[0][a]overlay={wm_pos}".format(
            scale=scale, alpha=alpha, wm_pos=self.wm_pos
        )

    def load_watermark_xml(self, xml_path='playblast/watermark.xml'):
        return load_config(xml_path).get('submenu', None)

    def get_watermark_string(self):

        info = self.load_watermark_xml()
        if not info:
            return
        wm_pos = self.watermark_position[info['position']]
        self.watermark_path = info['path']
        scale_factor = info['scale']
        w, h = scale_image(self.watermark_path, float(scale_factor))
        scale = '{}:{}'.format(w, h)  # w:h watermark scale
        wm_cmd = u"[1:v]scale={scale}[img1];" \
                      u"[img1]lut=a=val*{alpha}[a];" \
                      u"[0][a]overlay={wm_pos}".format(
            scale=scale, alpha=info['alpha'], wm_pos=wm_pos
        )
        return wm_cmd


class Output(Base):
    def __init__(self):
        super(Output, self).__init__()

    def cmd(self):

        comment = "1001-1011 " \
                  "W:/projects/can/shot/b40/b40053/ani/task/maya/b40053.ani.animation.v013.001.ma " \
                  "Z:/projects/can/preproduction/b40/story/aud/publish/b40.aud.audio.v014/b40053.wav " \
                  "1001.0"

        output_mov = 'G:/temp/0711/bb/aa.mov'
        # t = float(frame_num) / fps

        return ' -crf 18 -preset ultrafast -vcodec libx264 ' \
               '-pix_fmt yuv420p -c:a aac -t 0.458333333333 ' \
               '-metadata comment={comment} {output_mov}'.format(
            comment=comment,
            output_mov=output_mov,
        )


def seq2mov(input, output, fps, start, sound_path, frame_num, sound_offset=0, comment=''):
    """
    将序列转视频（可以+音频）

    """

    # vcodec: prores(lossless), libx264
    # pix_fmt: yuv444p(lossless),  yuv420p
    pix_fmt = 'yuv420p'
    vcodec = 'libx264'
    crf = 18  # crf: value smaller -- quality higher; Max:51
    if sound_path:
        # 带声音轨道, t(second)
        t = float(frame_num)/fps
        cmd = r'{ffm_path} -framerate {fps} -y ' \
              r'-start_number {start} ' \
              r'-i {input} ' \
              r'-itsoffset {offset} -i {sound_path} ' \
              r'-crf {crf} -preset ultrafast -vcodec {vcodec} -pix_fmt {pix_fmt} ' \
              r'-c:v copy -c:a aac -t {t} -metadata comment={comment} {output}'.format(
            ffm_path=FFMPEG,
            input=input,
            output=output, fps=fps,
            pix_fmt=pix_fmt,
            vcodec=vcodec,
            crf=crf,
            start=start,
            sound_path=sound_path,
            t=t,
            offset=sound_offset,
            comment=comment
        )
        out = subprocess.Popen(cmd, shell=True)
        out.wait()

    else:
        # 不带声音
        cmd = r'{ffm_path} -framerate {fps} -y ' \
              r'-start_number {start} ' \
              r'-i {input} ' \
              r'-crf {crf} -preset ultrafast -vcodec {vcodec} -pix_fmt {pix_fmt} ' \
              r'-an -metadata comment={comment} {output}'.format(
            ffm_path=FFMPEG,
            input=input,
            output=output, fps=fps,
            pix_fmt=pix_fmt,
            vcodec=vcodec,
            crf=crf,
            start=start,
            comment=comment,
        )
    print cmd
    out = subprocess.Popen(cmd, shell=True)
    out.wait()


def img2img(input, output, args):
    drawtext = Drawtext()
    drawtext = drawtext.font_strings(args)
    watermark = Watermark()
    wm_string = watermark.get_watermark_string()
    vcodec = 'libx264'

    if wm_string and drawtext:
        watermark_and_drawtext = u','.join([wm_string, drawtext])
        cmd = u'{ffm_path} ' \
              u'-i {input} ' \
              u'-i {wm_path} ' \
              u'-filter_complex {watermark_and_drawtext} ' \
              u'-q:v 1 ' \
              u'-y {output}'.format(
            ffm_path=FFMPEG,
            input=input,
            output=output,
            wm_path=watermark.watermark_path,
            watermark_and_drawtext=watermark_and_drawtext,
            vcodec=vcodec,
        )
    else:
        watermark_and_drawtext = wm_string or drawtext

        cmd = u'{ffm_path} ' \
              u'-i {input} ' \
              u'-filter_complex {watermark_and_drawtext} ' \
              u'-q:v 1 ' \
              u'-y {output}'.format(
            ffm_path=FFMPEG,
            input=input,
            output=output,
            wm_path=watermark.watermark_path,
            watermark_and_drawtext=watermark_and_drawtext,
            vcodec=vcodec,
        )

    print(cmd)
    out = subprocess.Popen(cmd.encode('GBK'), shell=True)
    out.wait()
    return watermark.watermark_path

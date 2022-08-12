# coding=utf8

import os
import sys
import re
import os
import yaml
import pipe_utils as pipe
from pipe_utils import load_xml


def get_next_available_version(path):
    """
    Returns (str): full path
    """
    name = os.path.basename(path)
    pre = os.path.splitext(name)[0]
    name_pre = re.sub('\.v\d{3}', '', pre)
    suf = os.path.splitext(name)[1]

    def get_version(name):
        result = re.match(name_pre + '\.v(\d{3})\.\w+', name)
        if result:
            return int(result.group(1))
    parent_dir = os.path.dirname(path)
    current_v = get_version(name)
    names = os.listdir(parent_dir)
    version_max = max(map(get_version, names))
    next_version = version_max + 1 if version_max else 1
    if current_v:
        new_version_str = '.v' + str(next_version).zfill(3) + '.'
        return re.sub('\.v\d{3}\.', new_version_str, path)
    else:
        return os.path.join(
            parent_dir,
            pre + '.v' + str(next_version).zfill(3) + suf
        )


def load_config(path='global.yaml', show=None):
    if not show:
        show = pipe.load_local_config().get('show') or 'ttt'
    config_data = {}
    root_path = pipe.code_root_path()
    config_path = os.path.join(root_path, 'config_data', 'DEFAULT', path)
    config_path_ = os.path.join(root_path, 'config_data', show, path)

    if path.endswith('.yaml'):
        config_data = pipe.yml_load(config_path)
        if os.path.exists(config_path_):
            config_data_by_show = pipe.yml_load(config_path_)
            config_data.update(config_data_by_show)
    elif path.endswith('.xml'):
        if os.path.exists(config_path_):
            config_path = config_path_
        # print config_path
        config_data = load_xml.load(config_path)

    return config_data


def load_xml_ffm(path):
    return load_xml.load(path)


if __name__ == '__main__':
    # print load_config('playblast/maya_playblast.yaml')
    print load_config('playblast\drawtext.xml')

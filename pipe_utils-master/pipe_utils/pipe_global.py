# -*- coding: utf-8 -*-

import os
import sys
import re
import shutil
import pkgutil
import json
import yaml

from configuration.utils import load_config


def code_root_path():
    return os.path.dirname(os.path.dirname(__file__))


def yml_load(path):
    with open(path, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


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


def guess_current_dcc():
    moudle_by_dcc = {
        'maya': 'maya',
        'houdini': 'hou',
        'clarisse': 'ix',
        'nuke': 'nuke',
        'unreal': 'unreal',
        'hiero': 'hiero',
    }
    current_dcc = None
    for name, moudle in moudle_by_dcc.items():
        if pkgutil.find_loader(name):
            current_dcc = name
            break
    return current_dcc


def config_path():
    root = os.path.expanduser('~')
    if root.endswith('Documents'):
        root = os.path.dirname(root)
    return os.path.join(root, 'config.json')


def load_local_config():
    """
    从本地config文件读取任务信息

    Returns:

    """

    config_path_ = config_path()
    if not os.path.exists(config_path_):
        return
    with open(config_path_, 'r') as f:
        return json.load(f)


def write_local_config(data):
    """
    记录当前任务信息（dict）
    Returns:

    """
    old_config = load_local_config() or {}
    new_config = old_config.copy()
    new_config.update(data)
    config_path_ = config_path()
    with open(config_path_, 'w') as f:
        json.dump(new_config, f, indent=4)


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


if __name__ == '__main__':
    print code_root_path()
    data = {
        'show': 'proj_test',
        'user': 'mw',
    }
    # write_local_config(data)
# -*- coding: utf-8 -*-
# Time    : 2021/10/18 18:37
# Author  : MengWei


from parse import parse

print parse(r'{task}.v{version:03d}.ma', 'mod.v001.ma')
print parse(r'{task}.v{version:03d}.ma', 'mod.v001.ma')['task']
print parse(r'{task}.v{version:03d}.ma', 'mod.v001.ma')['version']



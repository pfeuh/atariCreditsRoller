#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory
import disk
import sys
import shutil
import subprocess

# labels got from "mapping the Atari"
# https://www.atariarchives.org/mapping/memorymap.php

def getDefine(value, label):
    if value < 0:
        value += 65536
    if value >= 32768:
        value2 = -(65536 - value)
        text = "#define %-6s %6d // 0x%04x %d\n"%(label, value2, value, value)
    else:
        value2 = value
        text = "#define %-6s %6d // 0x%04x\n"%(label, value2, value)
    return text

def_list=(
(18, "RTCLOK"),
(82, "LMARGN"),
(83, "RMARGN"),
(106, "RAMTOP"),
(512, "VDSLST"),
(560, "SDLSTL"),
(704, "PCOLR0"),
(705, "PCOLR1"),
(706, "PCOLR2"),
(707, "PCOLR3"),
(708, "COLOR0"),
(709, "COLOR1"),
(710, "COLOR2"),
(711, "COLOR3"),
(712, "COLOR4"),
(743, "MEMLO",),
(756, "CHBAS",),
(-12257, "CONSOL",),
(53266, "COLPM0"),
(53267, "COLPM1"),
(53268, "COLPM2"),
(53269, "COLPM3"),
(53270, "COLPF0"),
(53271, "COLPF1"),
(53272, "COLPF2"),
(53273, "COLPF3"),
(53274, "COLBK"),
(54276, "HSCROL",),
(54277, "VSCROL",),
(54282, "WSYNC",),
)

table = {}
for record in def_list:
    key = record[0]
    label = record[1]
    if key < 0:
        key += 65536
    table[key] = label

keys = table.keys()
keys.sort()
for key in keys:
    sys.stdout.write(getDefine(key, table[key]))

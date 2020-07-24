#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory
import disk
import sys
import shutil
import subprocess

def getDefine(value, label):
    if value < 0:
        value += 65536
    if value >= 32768:
        value2 = -(65536 - value)
        text = "#define %-20s %6d // 0x%04x %d\n"%(label, value2, value, value)
    else:
        value2 = value
        text = "#define %-20s %6d // 0x%04x\n"%(label, value2, value)
    return text

def_list=(
("ATA_FRM_CNT_HI", 18),
("ATA_FRM_CNT_MID", 19),
("ATA_FRM_CNT_LOW", 20),
("ATA_LMARGIN", 82),
("ATA_RMARGIN", 83),
("ATA_RAMTOP", 106),
("ATA_DLIST", 560),
("ATA_TEXT_COLOR", 709),
("ATA_BG_COLOR", 710),
("ATA_BORDER_COLOR", 712),
("ATA_MEMLO", 743),
("ATA_CHBAS", 756),
("ATA_SCREEN_ADDR", -25568),
("ATA_CONSOL", -12257),)

for label, value in def_list:
    sys.stdout.write(getDefine(value, label))



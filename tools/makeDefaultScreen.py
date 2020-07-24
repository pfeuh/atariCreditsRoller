#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory
from disk import *
import sys
import shutil
import subprocess

# gnome-system-monitor

disk = VIRTUAL_DISK("./TITREUSE")
mem = memory.MEMORY()

bytes = disk.readFile("AIDE.ECR")
with open("./AIDE.ECR", "wb") as fp:
    fp.write(bytes)
print mem.loadFile("./AIDE.ECR", 32768)
print mem.map()

disk = VIRTUAL_DISK("/home/pfeuh/CREDITS")
bytes = disk.readFile("PRG.LST")
with open("./PRG.LST", "wb") as fp:
    fp.write(bytes)


sys.exit(0)

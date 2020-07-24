#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory
from disk import *
import sys
import shutil
import subprocess

# gnome-system-monitor
# ROUTINE=36864

ATARI_DISK_NAME = "./../out/DISK.XFD"
VERBOSE = "-verbose" in sys.argv
FILE_SHOWED = False

def copyFileToToAtari(ifname, ofname, disk):
    global FILE_SHOWED
    if VERBOSE:
        sys.stdout.write("copying %s -> %s->%s\n"%(ifname, disk.name, ofname))
    with open(ifname, "rb") as fp:
        bytes = fp.read(-1)
    if not FILE_SHOWED:
        sys.stdout.write("%d bytes\n"%(len(bytes)))
        FILE_SHOWED = True
    disk.writeFile(ofname, bytes)

def copyAtariToToAtari(ifname, idiskname, ofname, odisk):
    if VERBOSE:
        sys.stdout.write("copying %s->%s -> %s->%s\n"%(idiskname, ifname, odisk.name, ofname))
    temp_disk = VIRTUAL_DISK(idiskname)
    bytes = temp_disk.readFile(ifname)
    odisk.writeFile(ofname, bytes)

def getInfo(dname, fname):
    temp_disk = VIRTUAL_DISK(dname)
    bytes = temp_disk.readFile("A")
    with open(fname, "wb") as fp:
      fp.write(bytes)  
    
    mem = memory.MEMORY()
    mem.loadAtariBinaryFile(fname, strict=False)
    return mem.map() + str(mem.getModifiedRange())

#create a brand new Atari disk
params = ["./createDisk.sh"]
if VERBOSE:
    sys.stdout.write("creating disk ./../out/DISK.XFD\n")
errnum = subprocess.call(params)
if errnum:
    sys.exit(errnum)
disk = VIRTUAL_DISK(ATARI_DISK_NAME)
#add some fonts and credits on disk
copyAtariToToAtari("ACCENTUE.FNT", "./TITREUSE", "ACCENTUE.FNT", disk)
copyAtariToToAtari("KAISER.FNT", "./TITREUSE", "KAISER.FNT", disk)
copyAtariToToAtari("NIKON.SCR", "./TITREUSE", "NIKON.SCR", disk)
copyAtariToToAtari("AIDE.ECR", "./TITREUSE", "HELP.SCR", disk)

#compile .C to binary file
params = ["./compile.sh"]
errnum = subprocess.call(params)
if errnum:
    sys.exit(errnum)

#write the executable on Atari disk
copyFileToToAtari("./../src/CREDITS.COM", "CREDITS.COM", disk)
copyFileToToAtari("./../src/CREDITS.COM", "A", disk)
sys.stdout.write(getInfo(ATARI_DISK_NAME,  "A"))
#~ copyFileToToAtari("./../src/CREDITS.COM", "DUP.SYS", disk)

params = ["atari800"]
params.append("-nobasic")
params.append("-xl")
params.append("-xlxe_rom")
params.append("./ATARIXL.ROM")
errnum = subprocess.call(params)
if errnum:
    sys.exit(errnum)


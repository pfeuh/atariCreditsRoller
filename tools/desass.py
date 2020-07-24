#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory
from disk import *
import sys

# FLAG=ROUTINE+4:INDEX=ROUTINE+5:SPEEDTAB=ROUTINE+6:

disk = VIRTUAL_DISK("./TITREUSE")

ROUTINE = 36864

disk = VIRTUAL_DISK("./TITREUSE")
mem = memory.MEMORY()

bytes = disk.readFile("ROUTINE")
with open("ROUTINE", "wb") as fp:
    fp.write(bytes)
mem.loadAtariBinaryFile("ROUTINE")

bytes = disk.readFile("PAGE6")
with open("PAGE6", "wb") as fp:
    fp.write(bytes)
mem.loadAtariBinaryFile("PAGE6")

desass = memory.DESASS_6502()
desass_antic = memory.DESASS_ANTIC()
labels = {
    560:"DLIST_LO",
    561:"DLIST_HI",
    0x0601:"TEXTCOLOR",
    0x9004:"FLAG",
    0x9005:"INDEX",
    0x9006:"SPEEDTAB",
    0x9014:"DLIST_START",
    0x9035:"KB_NAME",
    0x9536:"mystere",
    0x94f9:"PROGRAM",
    }
desass.setAddr16Table(labels)
desass_antic.setAddr16Table(labels)
with open("DISASSEMBLED.TXT", "wb") as fp:
    #~ fp.write(desass.desass(ROUTINE, mem.peek, nb_lines=2))
    #~ fp.write(mem.dump(0x9000))
    #~ fp.write(desass.desass(0x94f9, mem.peek, nb_lines=213))
    #~ fp.write(desass.desass(0x921f, mem.peek, nb_lines=213))
    #~ fp.write("\n\n")
    #~ fp.write(desass.desass(0x600, mem.peek, nb_lines=200))
    #~ fp.write(mem.dump(0x600))
    fp.write(desass_antic.desass(0x9014, mem.peek))
    fp.write(desass.desass(0x934, mem.peek, nb_lines=200))

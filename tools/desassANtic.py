#!/usr/bin/python
# -*- coding: utf-8 -*-

import memory

OLD_HEX  = 0 # $1234 
OLD_HEX2 = 1 # 01234h
HEX      = 2 # 0x1234
DEC      = 3 # 4660
PROG     = 4 # 1234
SHOW_MODE_TAB = (OLD_HEX, OLD_HEX2, HEX, DEC, PROG)
SHOW_MODE = PROG

def word2hex(value):
    if value == None:
        size = len(word2hex(0))
        return " " * size
    elif SHOW_MODE == OLD_HEX:
        return "$%04X"%value
    elif SHOW_MODE == OLD_HEX2:
        return "0%04xh"%value
    elif SHOW_MODE == HEX:
        return "0x%04x"%value
    elif SHOW_MODE == DEC:
        return "%05d"%value
    elif SHOW_MODE == PROG:
        return "%04x"%value
    raise Exception("Unexpected SHOW_MODE %s!"%str(SHOW_MODE))

def byte2hex(value):
    if value == None:
        size = len(byte2hex(0))
        return " " * size
    elif SHOW_MODE == OLD_HEX:
        return "$%02X"%value
    elif SHOW_MODE == OLD_HEX2:
        return "0%02xh"%value
    elif SHOW_MODE == HEX:
        return "0x%02x"%value
    elif SHOW_MODE == DEC:
        return "%03d"%value
    elif SHOW_MODE == PROG:
        return "%02x"%value
    raise Exception("Unexpected SHOW_MODE %s!"%str(SHOW_MODE))

def getGlyphe(value):
    return "?"
    if x < 32:
        return "."
    elif x < 128:
        return chr(x)
    else:
        return "."
        
class DESASS_ANTIC():
    def __init__(self):
        self.__pc = None
        self.__getByte = None
        self.__addr16label={}
        self.__data_end = None

    def __getNextByte(self):
        byte = self.__getByte(self.__pc)
        self.__pc += 1
        return byte
        
    def __oneLine(self):
        pc = self.__pc
        byte1 = self.__getNextByte()
        byte2 = None
        byte3 = None
        line = ""

        if (byte1 & 0x0f) in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
            line += "MODE_%02d"%(byte1 & 0x0f)
            if byte1 & 0x10:
                line += " | HSCROL_ON"
            if byte1 & 0x20:
                line += " | VSCROL_ON"
            if byte1 & 0x80:
                line += " | DLI_ON"
            if byte1 & 0x40:
                byte2 = self.__getNextByte()
                byte3 = self.__getNextByte()
                target = byte2 + byte3 * 256
                if target in self.__addr16label.keys():
                    valuestr = self.__addr16label[target]
                else:
                    valuestr = word2hex(byte2 + byte3 * 256)
                line += " | setScreenMemory %s"%valuestr
        elif byte1 in [0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, ]:
            line += "BLANK_%02d"%(byte1 / 16 + 1)
        elif byte1 == 0x01:
                byte2 = self.__getNextByte()
                byte3 = self.__getNextByte()
                target = byte2 + byte3 * 256
                if target in self.__addr16label.keys():
                    valuestr = self.__addr16label[target]
                else:
                    valuestr = word2hex(byte2 + byte3 * 256)
                line += "jmp %s"%valuestr
        elif byte1 == 0x41:
                byte2 = self.__getNextByte()
                byte3 = self.__getNextByte()
                target = byte2 + byte3 * 256
                if target in self.__addr16label.keys():
                    valuestr = self.__addr16label[target]
                else:
                    valuestr = word2hex(byte2 + byte3 * 256)
                line += "jmp %s & wait VBI"%valuestr
                self.__data_end = True
        else:
            line += "unknow ANTIC opcode %s"%byte2hex(byte1)
        if pc in self.__addr16label.keys():
            prefix = "%s %s:\n%s"%(word2hex(pc), self.__addr16label[pc], word2hex(None))
        else:
            prefix = word2hex(pc)
        ret_line = "%s %s %s %s %s\n"%(prefix, byte2hex(byte1), byte2hex(byte2), byte2hex(byte3), line)
        return ret_line

    def setAddr16Table(self, table):
        self.__addr16label = table

    def desass(self, addr, get_byte_hook):
        self.__data_end = False
        self.__pc = addr
        self.__getByte = get_byte_hook
        text = ""
        while not self.__data_end:
            text += self.__oneLine()
        return text

class DESASS_8():
    def __init__(self):
        self.__pc = None
        self.__getByte = None
        self.__addr16label={}

    def __getNextByte(self):
        byte = self.__getByte(self.__pc)
        self.__pc += 1
        return byte
        
    def setAddr16Table(self, table):
        self.__addr16label = table

    def desass(self, addr, get_byte_hook, nb_bytes=256):
        text = ""
        self.__pc = addr
        self.__getByte = get_byte_hook
        index = 0
        line = ""
        while nb_bytes:
            pc = self.__pc
            byte = self.__getNextByte()
            if pc in self.__addr16label.keys():
                text += "%s %s:\n%s .byte %s\n"%(word2hex(pc), self.__addr16label[pc], word2hex(None), byte2hex(byte))
            else:
                text += "%s .byte %s\n"%(word2hex(pc), byte2hex(byte))
            nb_bytes -= 1
        return text
    
class DESASS_16():
    def __init__(self):
        self.__pc = None
        self.__getByte = None
        self.__addr16label={}

    def __getNextByte(self):
        byte = self.__getByte(self.__pc)
        self.__pc += 1
        return byte
        
    def setAddr16Table(self, table):
        self.__addr16label = table

    def desass(self, addr, get_byte_hook, nb_bytes=256):
        text = ""
        self.__pc = addr
        self.__getByte = get_byte_hook
        index = 0
        line = ""
        while nb_bytes:
            pc = self.__pc
            byte1 = self.__getNextByte()
            byte2 = self.__getNextByte()
            value = byte1 + byte2 * 256
            if value in self.__addr16label.keys():
                valuestr = self.__addr16label[value]
            else:
                valuestr = word2hex(value)
            if pc in self.__addr16label.keys():
                text += "%s %s:\n%s .word %s\n"%(word2hex(pc), self.__addr16label[pc], word2hex(None), valuestr)
            else:
                text += "%s .word %s\n"%(word2hex(pc), valuestr)
            nb_bytes -= 1
        return text
    
if __name__ == '__main__':
    
    import sys
    mem = memory.MEMORY()
    
    dlist = 1536
    screen = 40000
    dlist_code = [0x70, 0x70, 0x70, 0x42, screen & 255, screen/256, 0x02, 0x02,
        0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
        0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
        0x02, 0x02, 0x02, 0x02, 0x02, 0x41, dlist & 255, dlist/256]
    for x, value in enumerate(dlist_code):
        mem.poke(dlist + x, value)

    desass = memory.DESASS_6502()
    labels = {
        dlist:"DLIST",
        screen:"SCREEN_START",
        }
    
    unass = memory.DESASS_ANTIC()
    unass.setAddr16Table(labels)
    #~ sys.stdout.write(unass.desass(dlist, mem.peek))

    dump8 = memory.DESASS_8()
    dump8.setAddr16Table(labels)
    sys.stdout.write( dump8.desass(dlist, mem.peek, nb_bytes=32))
    
    dump16 = memory.DESASS_16()
    dump16.setAddr16Table(labels)
    sys.stdout.write( dump16.desass(dlist, mem.peek, nb_bytes=16))

    for x, car in enumerate("Hello, World!\n\000"):
        mem.poke(dlist + x, ord(car), strict=False)
    sys.stdout.write( mem.dump(dlist))

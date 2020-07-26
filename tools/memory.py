#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

MEMORY_SIZE = 0x10000
BYTE_MIN_VALUE = 0
BYTE_MAX_VALUE = 0xff

LITTLE_ENDIAN = 1
BIG_ENDIAN = 2

EXE_FILE_MAGIC_NUMBER = 0xffff
NOT_MODIFIED = 0
MODIFIED = 1

DFLAGS = 0x0240
BOOTAD = 0x0242
DOSINI = 0x000C

SECTOR_SIZE = 0x80
BOOT_HEADER_SIZE = 6
DUMP_SIZE = 0x100

ascii2glyphe = ['.' for x in range(32)] + [chr(x) for x in range(32, 128)] + ['.' for x in range(128)]

ZERO = ' '
ONE = 'X'
CR = '\n'

TEMPLATE_HEADER = """#ifndef %LABEL%_HEADER
#define %LABEL%_HEADER

#include "datatype.h"

extern const byte %DATANAME%[%SIZE%];

#define %SIZENAME%_SIZE %SIZE%

#endif
"""

TEMPLATE_SOURCE = """

#include "%HEADERNAME%"

const byte %DATANAME%[%SIZE%] = 
{
%VALUES%};

"""

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
    if value < 32:
        return "."
    elif value < 128:
        return chr(value)
    else:
        return "."
        
class DESASS_6502():
    def __init__(self):
        self.__pc = None
        self.__getByte = None
        self.__addr16label={}
        self.__mnemo=[
        {'mnemo':'BRK','hook':self.inherent},
        {'mnemo':'ORA','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ORA','hook':self.zeropage},
        {'mnemo':'ASL','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'PHP','hook':self.inherent},
        {'mnemo':'ORA','hook':self.immediate},
        {'mnemo':'ASL','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ORA','hook':self.absolute},
        {'mnemo':'ASL','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BPL','hook':self.relative},
        {'mnemo':'ORA','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ORA','hook':self.zeropagex},
        {'mnemo':'ASL','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CLC','hook':self.inherent},
        {'mnemo':'ORA','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ORA','hook':self.absolx},
        {'mnemo':'ASL','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'JSR','hook':self.absolute},
        {'mnemo':'AND','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BIT','hook':self.zeropage},
        {'mnemo':'AND','hook':self.zeropage},
        {'mnemo':'ROL','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'PLP','hook':self.inherent},
        {'mnemo':'AND','hook':self.immediate},
        {'mnemo':'ROL','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BIT','hook':self.absolute},
        {'mnemo':'AND','hook':self.absolute},
        {'mnemo':'ROL','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BMI','hook':self.relative},
        {'mnemo':'AND','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'AND','hook':self.zeropagex},
        {'mnemo':'ROL','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'SEC','hook':self.inherent},
        {'mnemo':'AND','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ORA','hook':self.absolx},
        {'mnemo':'ASL','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'RTI','hook':self.inherent},
        {'mnemo':'EOR','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'EOR','hook':self.zeropage},
        {'mnemo':'LSR','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'PHA','hook':self.inherent},
        {'mnemo':'EOR','hook':self.immediate},
        {'mnemo':'LSR','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'JMP','hook':self.absolute},
        {'mnemo':'EOR','hook':self.absolute},
        {'mnemo':'LSR','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BVC','hook':self.relative},
        {'mnemo':'EOR','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'EOR','hook':self.zeropagex},
        {'mnemo':'LSR','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CLI','hook':self.inherent},
        {'mnemo':'EOR','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'EOR','hook':self.absolx},
        {'mnemo':'LSR','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'RTS','hook':self.inherent},
        {'mnemo':'ADC','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ADC','hook':self.zeropage},
        {'mnemo':'ROR','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'PLA','hook':self.inherent},
        {'mnemo':'ADC','hook':self.immediate},
        {'mnemo':'ROR','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'JMP','hook':self.indirect},
        {'mnemo':'ADC','hook':self.absolute},
        {'mnemo':'ROR','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BCS','hook':self.relative},
        {'mnemo':'ADC','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ADC','hook':self.zeropagex},
        {'mnemo':'ROR','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'SEI','hook':self.inherent},
        {'mnemo':'ADC','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'ADC','hook':self.absolx},
        {'mnemo':'ROR','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'STA','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'STY','hook':self.zeropage},
        {'mnemo':'STA','hook':self.zeropage},
        {'mnemo':'STX','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'DEY','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'TXA','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'STY','hook':self.absolute},
        {'mnemo':'STA','hook':self.absolute},
        {'mnemo':'STX','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BCC','hook':self.relative},
        {'mnemo':'STA','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'STY','hook':self.inherent},
        {'mnemo':'STA','hook':self.zeropagex},
        {'mnemo':'STX','hook':self.zeropagey},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'TYA','hook':self.inherent},
        {'mnemo':'STA','hook':self.absoly},
        {'mnemo':'TXS','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'STA','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'LDY','hook':self.immediate},
        {'mnemo':'LDA','hook':self.indzerox},
        {'mnemo':'LDX','hook':self.immediate},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'LDY','hook':self.zeropage},
        {'mnemo':'LDA','hook':self.zeropage},
        {'mnemo':'LDX','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'TAY','hook':self.inherent},
        {'mnemo':'LDA','hook':self.immediate},
        {'mnemo':'TAX','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'LDY','hook':self.absolute},
        {'mnemo':'LDA','hook':self.absolute},
        {'mnemo':'LDX','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BCS','hook':self.relative},
        {'mnemo':'LDA','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'LDY','hook':self.zeropagex},
        {'mnemo':'LDA','hook':self.zeropagex},
        {'mnemo':'LDX','hook':self.zeropagey},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CLV','hook':self.inherent},
        {'mnemo':'LDA','hook':self.absoly},
        {'mnemo':'TSX','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'LDY','hook':self.inherent},
        {'mnemo':'LDA','hook':self.absolx},
        {'mnemo':'LDX','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CPY','hook':self.immediate},
        {'mnemo':'CMP','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CPY','hook':self.zeropage},
        {'mnemo':'CMP','hook':self.zeropage},
        {'mnemo':'DEC','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'INY','hook':self.inherent},
        {'mnemo':'CMP','hook':self.immediate},
        {'mnemo':'DEX','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CPY','hook':self.absolute},
        {'mnemo':'CMP','hook':self.absolute},
        {'mnemo':'DEC','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BNE','hook':self.relative},
        {'mnemo':'CMP','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CMP','hook':self.zeropagex},
        {'mnemo':'DEC','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CLD','hook':self.inherent},
        {'mnemo':'CMP','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CMP','hook':self.absolx},
        {'mnemo':'DEC','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CPX','hook':self.immediate},
        {'mnemo':'SBC','hook':self.indzerox},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'CPX','hook':self.zeropage},
        {'mnemo':'SBC','hook':self.zeropage},
        {'mnemo':'INC','hook':self.zeropage},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'INX','hook':self.inherent},
        {'mnemo':'SBC','hook':self.immediate},
        {'mnemo':'NOP','hook':self.inherent},
        {'mnemo':'SBC','hook':self.inherent},
        {'mnemo':'CPX','hook':self.absolute},
        {'mnemo':'SBC','hook':self.absolute},
        {'mnemo':'INC','hook':self.absolute},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'BEQ','hook':self.relative},
        {'mnemo':'SBC','hook':self.indzeroy},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'SBC','hook':self.zeropagex},
        {'mnemo':'INC','hook':self.zeropagex},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'SED','hook':self.inherent},
        {'mnemo':'SBC','hook':self.absoly},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'???','hook':self.inherent},
        {'mnemo':'SBC','hook':self.absolx},
        {'mnemo':'INC','hook':self.absolx},
        {'mnemo':'???','hook':self.inherent},]


    def __oneLine(self):
        label_line = ""
        if self.__pc in self.__addr16label.keys():
            label_line = "%s %s:\n"%(word2hex(self.__pc), self.__addr16label[self.__pc])
            line = word2hex(None)
        else:   
            label_line = ""
            line = word2hex(self.__pc)
        byte = self.__getNextByte()
        return "%s%s %s\n"%(label_line, line, self.__mnemo[byte]["hook"](byte))

    def setAddr16Table(self, table):
        self.__addr16label = table

    def desass(self, addr, get_byte_hook, nb_lines=24):
        self.__pc = addr
        self.__getByte = get_byte_hook
        text = ""
        while nb_lines:
            text += self.__oneLine()
            nb_lines -= 1
        return text

    def __getNextByte(self):
        byte = self.__getByte(self.__pc)
        self.__pc += 1
        return byte
        
    def GetPc(self):
        return self.__pc

    def Add1Value(self,value1):
        return "%s %s %s"%(byte2hex(value1), byte2hex(None), byte2hex(None))

    def Add2Values(self,value1,value2):
        return "%s %s %s"%(byte2hex(value1), byte2hex(value2), byte2hex(None))

    def Add3Values(self,value1,value2,value3):
        return "%s %s %s"%(byte2hex(value1), byte2hex(value2), byte2hex(value3))

    def GetRel(self,byterel):
        if byterel<128:
            return self.GetPc()+byterel
        else:
            return self.GetPc()-256+byterel

    #----------------#
    # Mnemonic Hooks #
    #----------------#

    def immediate(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += "#%s"%byte2hex(b2)
        return retval
        
    def inherent(self,opcode):
        return "%s %s"%(self.Add1Value(opcode), self.__mnemo[opcode]["mnemo"])
        
    def zeropage(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += byte2hex(b2)
        return "%s"%retval
        
    def zeropagex(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += " %s,X"%byte2hex(b2)
        return retval
        
    def zeropagey(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += "%s,Y"%(byte2hex(b2))
        return retval
        
    def indzerox(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += "(%s,X)"%(byte2hex(b2))
        return retval
        
    def indzeroy(self,opcode):
        b2 = self.__getNextByte()
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += "(%s),Y"%(byte2hex(b2))
        return retval
        
    def absolute(self,opcode):
        b2 = self.__getNextByte()
        b3 = self.__getNextByte()
        value = b3*256+b2
        valuestr = word2hex(value)
        if value in self.__addr16label.keys():
            valuestr=self.__addr16label[value]
        retval = "%s %s "%(self.Add3Values(opcode,b2,b3), self.__mnemo[opcode]["mnemo"])
        retval+="%s"%valuestr
        return retval
        
    def absolx(self,opcode):
        b2 = self.__getNextByte()
        b3 = self.__getNextByte()
        value =b3*256+b2
        valuestr = word2hex(value)
        if value in self.__addr16label.keys():
            valuestr=self.__addr16label[value]
        retval = "%s %s "%(self.Add3Values(opcode,b2,b3), self.__mnemo[opcode]["mnemo"])
        retval += "%s,X"%valuestr
        return retval
        
    def absoly(self,opcode):
        b2 = self.__getNextByte()
        b3 = self.__getNextByte()
        value = b3*256+b2
        valuestr = word2hex(value)
        if value in self.__addr16label.keys():
            valuestr=self.__addr16label[value]
        retval = "%s %s "%(self.Add3Values(opcode,b2,b3), self.__mnemo[opcode]["mnemo"])
        retval+="%s,Y"%valuestr
        return retval
        
    def indirect(self,opcode):
        b2 = self.__getNextByte()
        b3 = self.__getNextByte()
        value = b3*256+b2
        valuestr = word2hex(value)
        if value in self.__addr16label.keys():
            valuestr=self.__addr16label[value]
        retval = "%s %s "%(self.Add3Values(opcode,b2,b3), self.__mnemo[opcode]["mnemo"])
        retval+="(%s)"%valuestr
        return retval
        
    def relative(self,opcode):
        b2 = self.__getNextByte()
        target = self.GetRel(b2)
        retval = "%s %s "%(self.Add2Values(opcode,b2), self.__mnemo[opcode]["mnemo"])
        retval += "%s"%word2hex(target)
        return retval

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
    
class MEMORY:
    def __init__(self, endianess=LITTLE_ENDIAN):
        self.endianess = endianess
        self.data      = [0 for x in range(MEMORY_SIZE)]
        self.modified  = [NOT_MODIFIED for x in range(MEMORY_SIZE)]
        #~ self.glyphes = ['.' for x in range(32)]+[chr(x) for x in range(32, 128)]+['.' for x in range(128)]
        
    def setPC(self, pc):
        self.__pc = pc

    def getByte(self):
        byte = mem.peek(self.__pc)
        self.__pc = (self.__pc + 1) & 0xff
        return byte
        
    def __str__(self):
        return "<MEMORY_instance 0x%x bytes v 0.99>"%MEMORY_SIZE

    def poke(self, addr, value, strict=1):
        if addr >= MEMORY_SIZE or addr < 0:
            raise Exception("addr 0x%x is out of range"%addr)
        if value > BYTE_MAX_VALUE or value < BYTE_MIN_VALUE:
            raise Exception("byte 0x%x is out of range"%value)
        self.data[addr] = value
        if strict:
            if self.modified[addr] != NOT_MODIFIED:
                raise Exception("addr 0x%x is overwritten!"%addr)
        self.modified[addr] = MODIFIED

    def wpoke(self, addr, value):
        lovalue = value & 0xff
        hivalue = value / 0x100
        if self.endianess == BIG_ENDIAN:
            self.poke(addr, hivalue)
            self.poke(addr + 1, lovalue)
        elif self.endianess == LITTLE_ENDIAN:
            self.poke(addr, lovalue)
            self.poke(addr + 1, hivalue)
        else:
            raise Exception("unknown endianess!")

    def peek(self, addr):
        if addr >= MEMORY_SIZE or addr < 0:
            raise Exception("addr 0x%x is out of range"%addr)
        return self.data[addr]

    def wpeek(self, addr):
        if self.endianess == BIG_ENDIAN:
            hivalue = self.peek(addr)
            lovalue = self.peek(addr + 1)
        elif self.endianess == LITTLE_ENDIAN:
            hivalue = self.peek(addr + 1)
            lovalue = self.peek(addr)
        else:
            raise Exception("unknown endianess!")
        return hivalue * 256 + lovalue
        
    def getModifiedRange(self, start=0):
        modified = []
        for x in range(start,MEMORY_SIZE):
            if self.modified[x]:
                modified.append(x)
        if len(modified):
            return (modified[0], modified[-1] - modified[0] + 1)

    def getMemlo(self, start=0):
        # returns address of first not modified byte after last modified bytes area
        memlo = None
        for addr in range(start,MEMORY_SIZE):
            if self.modified[addr]:
                memlo = addr
        if memlo == None:
            return 0
        else:
            return memlo + 1

    def getBloc(self, start, size):
        text = ""
        max = start+size
        for addr in range(start, start+size):
            text += chr(self.peek(addr))
        return text

    def dump(self, addr):
        text = ""
        for index in range(DUMP_SIZE):
            if index % 16 == 0:
                asciibuffer = ""
                text += "%04x "%(addr + index)
            text += "%02x "%self.peek(addr + index)
            asciibuffer += getGlyphe(self.peek(addr + index))
            if index % 16 == 15:
                text += asciibuffer + "\n"
        return text

    def getByte(self, fp):
        car = fp.read(1)
        if car == '':
            return None
        return ord(car)

    def getWord(self, fp):
        # *** WARNING! In an Atari binary file, 16 bits values are in LITTLE ENDIAN! ***
        byte2 = self.getByte(fp)
        byte1 = self.getByte(fp)
        if byte2 == None:
            return None
        return byte1 * 256 + byte2

    def getSegment(self, fp):
        start = self.getWord(fp)
        if start == None:
            return None
        if start == EXE_FILE_MAGIC_NUMBER:
            start = self.getWord(fp)
        last = self.getWord(fp)
        if last == None:
            raise Exception("Unexpected end of executable file!")
        size = 1 + last - start
        bytes = fp.read(size)
        if len(bytes) != size:
            raise Exception("Unexpected end of executable file!")
        return (start, bytes)

    def loadFile(self, fname, addr=0, verbose=False):
        fp = open(fname, 'rb')
        bytes = fp.read(-1)
        for car in bytes:
            if addr > MEMORY_SIZE:
                raise Exception("%s Loading out of memory range!"%fname)
            self.poke(addr, ord(car))
            addr += 1
        return len(bytes)

    def loadAtariBinaryFile(self, fname, verbose=False, strict=True):
        fp = open(fname, 'rb')
        if self.getWord(fp) != EXE_FILE_MAGIC_NUMBER:
            raise Exception("%s is not an executable file!"%shortname)
        while 1:
            bloc = self.getSegment(fp)
            if bloc == None:
                break
            if verbose:
                sys.stdout.write("$%04x %d\n"%(bloc[0], len(bloc[1])))
            addr = bloc[0]
            bytes = bloc[1]
            for index in range(len(bytes)):
                self.poke(addr + index, ord(bytes[index]), strict=strict)

    def loadAtariBootDisk(self, dname):
        fp = open(dname, 'rb')
        flags = self.getByte(fp)
        self.poke(DFLAGS, flags)
        nb_sectors = self.getByte(fp)
        size = nb_sectors * SECTOR_SIZE
        start_addr = self.getWord(fp)
        self.wpoke(BOOTAD, start_addr) 
        init_addr = self.getWord(fp)
        self.wpoke(DOSINI, init_addr) 
        fp.seek(0)
        addr = start_addr# - BOOT_HEADER_SIZE
        try:
            for x in range(size):
                self.poke(addr + x, self.getByte(fp))
        except:
            raise Exception("Unexpected end of disk!")

    def compare(self, other, max=20):
        differences = 0
        text = ""
        for addr in range(MEMORY_SIZE):
            if self.peek(addr) != other.peek(addr):
                text += "%04x %02x %02x\n"%(addr, self.peek(addr), other.peek(addr))
                differences += 1
                if differences == max:
                    text += "Too much errors, abort!\n"
                    break
        return text

    def find(self, bytes, start=0, stop=MEMORY_SIZE, max_occurences=MEMORY_SIZE):
        addresses = []
        size = len(bytes)
        max_index = size - 1
        for addr in range(start, stop):
            for index in range(size):
                if self.peek(addr + index) != bytes[index]:
                    break
                elif index == max_index:
                    addresses.append(addr)
                    if len(addresses) == max_occurences:
                        break
        return addresses

    def map(self):
        values = []
        for pagenum in range(0x100):
            addr = pagenum * 0x100
            addr_max = addr + 0x100
            while(1):
                if addr == addr_max:
                    values.append("  ")
                    break
                if self.modified[addr] != NOT_MODIFIED:
                    values.append(" X")
                    break
                addr += 1
        text = ""
        for pagenum in range(0x100):
            addr = pagenum * 0x100
            if not pagenum % 16:
                text += "%04x "%addr
            text += "%s"%values[pagenum]
            if pagenum % 16 == 15:
                text += "\n"
        return text

    def load(self, fname, addr=0, size=None):
        with open(fname, 'rb') as fp:
            body = fp.read(-1)
        if size == None:
            size = len(body)
        if addr + size > MEMORY_SIZE:
            size = MEMORY_SIZE - addr
        body = body[:size]
        for car in body:
            self.poke(addr, ord(car))
            addr += 1

    def getBitmap(self, byte):
        text = " // "
        for cpt in range(8):
            if byte & 0x80:
                text += ONE
            else:
                text += ZERO
            byte <<= 1
        return text
    
    def getDatalines(self, data, cols=8, glypheview=0):
        datalines = ""
        max = len(data) -1
        if cols == 1:
            for index, byte in enumerate(data):
                line = "    0x%02x"%byte
                if index == max:
                    line += ' '
                else:
                    line += ','
                if glypheview:
                    line += self.getBitmap(byte)
                
                line += CR
                datalines += line
        else:
            for index, byte in enumerate(data):
                if index % cols == 0:
                    datalines += "    "
                datalines += "0x%02x"%byte
                if index == max:
                    datalines += ' '
                else:
                    datalines += ','
                if (index % cols == (cols - 1)) or (index == max):
                    datalines += "\n"
        return datalines

    def bytes2C(self, start, size, fbasename, dataname, cols=8, glypheview=0):
        data = [self.peek(pbyte) for pbyte in range(start, start + size)]
        headername = "%s.h"%(fbasename)
        headerbody = TEMPLATE_HEADER
        headerbody = headerbody.replace("%LABEL%", fbasename.upper())
        headerbody = headerbody.replace("%DATANAME%", dataname)
        headerbody = headerbody.replace("%SIZE%", "%u"%size)
        headerbody = headerbody.replace("%SIZENAME%", dataname.upper())
        with open(headername, "w") as fp:
            fp.write(headerbody)
        sourcename = "%s.c"%(fbasename)
        sourcebody = TEMPLATE_SOURCE
        sourcebody = sourcebody.replace("%HEADERNAME%", headername)
        sourcebody = sourcebody.replace("%DATANAME%", dataname)
        sourcebody = sourcebody.replace("%SIZE%", "%u"%size)
        datalines = self.getDatalines(data, cols, glypheview)
        sourcebody = sourcebody.replace("%VALUES%", datalines)
        with open(sourcename, "w") as fp:
            fp.write(sourcebody)
            

if __name__ == '__main__':

    from disk import *

    def utest():
        mem=MEMORY()
        mem.poke(0x1000, 255)
        mem.poke(0x1fff, 255)
        start, size = mem.getModifiedRange()
        assert start == 0x1000
        assert size == 0x1000
        
        mem=MEMORY(endianess=BIG_ENDIAN)
        mem.poke(0, 0x12)
        mem.poke(1, 0x34)
        assert mem.wpeek(0) == 0x1234
        mem.wpoke(5, 0xcafe)
        assert mem.peek(5) == 0xca
        assert mem.peek(6) == 0xfe
        
        mem=MEMORY()
        mem.poke(0, 0x12)
        mem.poke(1, 0x34)
        mem.endianess = LITTLE_ENDIAN
        assert mem.wpeek(0) == 0x3412
        mem.wpoke(5, 0xcafe)
        assert mem.peek(5) == 0xfe
        assert mem.peek(6) == 0xca

        mem=MEMORY()
        for x in range(256):
            mem.poke(34567 + x, x)
        start, size = mem.getModifiedRange()
        assert start == 34567
        assert size == 0x100
        bytes = mem.getBloc(start, size)
        for index, car in enumerate(bytes):
            assert ord(car) == index
            
        mem=MEMORY()
        mem.poke(34567, 1)
        memlo = mem.getMemlo()
        assert memlo == 34568
        mem=MEMORY()
        memlo = mem.getMemlo()
        assert memlo == 0
            
        sys.stdout.write("A L L   T E S T S   P A S S E D !\n")
    
    utest()
    
    from disk import *
    
    disk = VIRTUAL_DISK("./../out/DISK.XFD")
    #~ sys.stdout.write(str(disk.directory()))
    bytes = disk.readFile("A")
    with open("./A", "wb") as fp:
        fp.write(bytes)
    mem = MEMORY()
    mem.loadAtariBinaryFile("A", strict=False)
    sys.stdout.write("MEMLO 0x%04x %05d\n"%(mem.getMemlo(), mem.getMemlo()))
    
    

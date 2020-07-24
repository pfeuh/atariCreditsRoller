#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from constants import *

def textToBytes(text):
    return [ord(car) for car in text]

def bytesToText(bytes):
    text = ""
    for byte in bytes:
        text += chr(byte)
    return text

def extractHtmlCodes(text):
    text2 = ""
    freezed = False
    for index, car in enumerate(text):
        if not freezed:
            if car == '&':
                if text[index + 1] == "#":
                    if ';' in text[index + 2:index + 7]:
                        code = 0
                        idx = index + 2
                        while 1:
                            if text[idx] in '0123456789':
                                code = code * 10 + int(text[idx])
                            elif text[idx] ==';':
                                text2 += chr(code)
                                freezed = True
                                break
                            else:
                                break
                            idx += 1
            if not freezed:
                text2 += car
        else:
            if car == ';':
                freezed = False
    return text2

def asciiToAtascii(text):
    text2 = ""
    for car in text:
        if ord(car) > 255:
            raise Exception(ATARI_ERR_UNICODE_CHAR)
        if car == '\n':
            text2 += chr(0x9b)
        elif car == '\r':
            pass
        else:
            text2 += chr(ord(car))
    text = extractHtmlCodes(text2)
    return text

def atasciiToAscii(text):
    text2 = ""
    for car in text:
        if ord(car) > 255:
            raise Exception(ATARI_ERR_UNICODE_CHAR)
        if car == chr(0x9b):
            text2 += chr(0x0a)
        elif ord(car) < 32 or ord(car) > 127:
            text2 += "&#%u;"%ord(car)
        else:
            text2 += car
    return text2

def secnumToVtocIdx(secnum):
    return ATARI_OFS_VTOC + secnum / 8, secnum % 8
    
def getStatusStr(byte):
    text = ""
    if byte & ATARI_SIO_STATUS_BIT_INVALID_COMMAND:
        text += "Invalid command\n"
    if byte & ATARI_SIO_STATUS_BIT_INVALID_DATA:
        text += "Invalid data\n"
    if byte & ATARI_SIO_STATUS_BIT_BAD_PUT:
        text += "Invalid put\n"
    if byte & ATARI_SIO_STATUS_BIT_WRITE_PROTECTED:
        text += "read only\n"
    if byte & ATARI_SIO_STATUS_BIT_ACTIVE:
        text += "active\n"
    else:
        text += "sleeping\n"
    return text

def serialize(bytes):
    """ input data should be a bytes list"""
    if type(bytes) == str:
        bytes = [ord(car) for car in bytes]
    text = MAGIC_WORD_TEXT
    for byte in bytes:
        text += "%02x"%byte
    return text

def unserialize(text):
    if type(text) != str:
        return None
    if len(text) % 2 != len(MAGIC_WORD_TEXT) % 2:
        return None
    if len(text) < len(MAGIC_WORD_TEXT):
        return None
    if text[:len(MAGIC_WORD_TEXT)] != MAGIC_WORD_TEXT:
        return None
    bytes = []
    for idx, car in enumerate(text[len(MAGIC_WORD_TEXT):]):
        if not idx % 2:
            hexstr = car
        else:
            hexstr += car
            try:
                bytes.append(int(hexstr, 16))
            except:
                raise Exception(ATARI_ERR_BAD_CLIPBOARD)
    return bytes

def fnameAta2Dos(filename):
    fname = filename[:8].strip()
    ext = filename[8:].strip()
    if ext != "":
        return '.'.join([fname, ext])
    else:
        return fname
        
def fnameDos2Ata(filename):
    words = filename.split('.')
    if len(words) > 2:
        raise Exception(ATARI_ERR_BAD_FILENAME)
    fname = words[0]
    if len(words) > 1:
        ext = words[1]
    else:
        ext=''
    if len(fname) > 8 or len(ext) > 3:
        raise Exception(ATARI_ERR_BAD_FILENAME)
    for car in filename:
        if not car in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.":
            raise Exception(ATARI_ERR_BAD_FILENAME)
    while len(fname) < 8:
        fname += ' '
    while len(ext) < 3:
        ext += ' '
    return fname+ext

def dump(bytes, offset=0):
    text = ''
    for bytenum, byte in enumerate(bytes):
        if bytenum % 16 == 0:
            hexbuf = "%04x "%offset
            offset = (offset + 16) & 0xffff
            asciibuf = ""
        hexbuf += "%02x "%byte
        asciibuf += DUMP_TAB[byte]
        if bytenum % 16 == 15:
            text += "%s%s\n"%(hexbuf, asciibuf)
    return text


def createDisk(fname):
    # create disk image
    fp = open(fname, 'wb')
    for bytenum in range(ATARI_LAST_SECTOR * ATARI_SECTOR_SIZE):
        fp.write(chr(0))
    fp.close()
    # fill with real DOS specs
    disk = VIRTUAL_DISK(fname)
    vtoc = disk.readSector(ATARI_VTOC)
    for bytenum in range(11, 100):
        vtoc[bytenum] = 0xff
    vtoc[0] = 2
    vtoc[1] = 0xc3
    vtoc[2] = 0x02
    vtoc[3] = 0xc3
    vtoc[4] = 0x02
    vtoc[10] = 0x0f
    vtoc[55] = 0
    vtoc[56] = 0x7f
    vtoc.update()
    return disk

class ENTRY(list):
    def __init__(self, sector, entrynum):
        self.sector = sector
        self.offset = entrynum * ATARI_ENTRY_SIZE
        self.filenum = (sector.secnum - ATARI_FAT_START) * ATARI_ENTRIES_PER_SECTOR + entrynum

    def get(self, idx):
        return self.sector[self.offset + idx]
        
    def set(self, idx, value):
        self.sector[self.offset + idx] = value
        
    def __str__(self):
        data =  [byte for byte in self.sector[self.offset:self.offset + ATARI_ENTRY_SIZE]]
        words = ["%u"%byte for byte in data]
        text = [DUMP_TAB[byte] for byte in data]
        return '<ENTRY %u> %s'%(self.filenum, self.getDirLine(1))
        
    def getFileNum(self):
        return self.filenum
    
    def setFileNum(self, filenum):
        self.filenum = filenum

    def getFlags(self):
        idx = 0
        return self.get(idx)
        
    def setFlags(self, flags):
        idx = 0
        self.set(idx, flags)
        
    def getSectorCount(self):
        idx = ATARI_IDX_FAT_SECTOR_COUNT
        return self.get(idx) + self.get(idx + 1) * 0x100
        
    def setSectorCount(self, nb_sec):
        idx = ATARI_IDX_FAT_SECTOR_COUNT
        self.set(idx, nb_sec & 0xff)
        self.set(idx + 1, nb_sec >> 8)
        
    def getStartingSector(self):
        idx = ATARI_IDX_FAT_STARTING_SECTOR
        return self.get(idx) + self.get(idx + 1) * 0x100
    
    def setStartingSector(self, secnum):
        idx = ATARI_IDX_FAT_STARTING_SECTOR
        self.set(idx, secnum & 0xff)
        self.set(idx + 1, secnum >> 8)
    
    def getLockChar(self):
        if self.getFlags() & ATARI_FILE_FLAG_LOCKED:
            return '*'
        else:
            return ' '
    
    def getFlagsText(self):
        text = ""
        if self.getFlags() & ATARI_FILE_FLAG_LOCKED:
            text += '*'
        else:
            text += '.'
        if self.getFlags() & ATARI_FILE_FLAG_USED:
            text += 'u'
        else:
            text += '.'
        if self.getFlags() & ATARI_FILE_FLAG_DELETED:
            text += 'd'
        else:
            text += '.'
        if self.getFlags() & ATARI_FILE_FLAG_OUTPUT:
            text += 'o'
        else:
            text += '.'
        return text

    def getFilename(self):
        fname = ""
        start = ATARI_IDX_FAT_FILENAME
        stop = ATARI_IDX_FAT_FILENAME_END
        for idx in range(start, stop):
            fname += chr(self.get(idx))
        return fnameAta2Dos(fname)

    def setFilename(self, fname):
        fname = fnameDos2Ata(fname)
        start = ATARI_IDX_FAT_FILENAME
        stop = ATARI_IDX_FAT_FILENAME_END
        for x1, x2 in enumerate(range(start, stop)):
            self.set(x2, ord(fname[x1]))

    def getDirLine(self, verbose=0):
        if verbose == 0:
            return "%s %-012s %03u"%(self.getLockChar(), self.getFilename(), self.getSectorCount())
        else:
            text = "%02u "%self.filenum
            return "%s%s %-012s %04u %04u"%(text, self.getFlagsText(), self.getFilename(), self.getSectorCount(), self.getStartingSector())

    def update(self):
        self.sector.update()

class SECTOR(list):
    def __init__(self, bytes=None, disk=None, secnum=None):
        if bytes == None:
            bytes = [ATARI_DEFAULT_BYTE for x in range(ATARI_SECTOR_SIZE)]
        if len(bytes) != ATARI_SECTOR_SIZE:
            raise Exception(ATARI_ERR_BAD_SECTOR_SIZE)
        list.__init__(self)
        for byte in bytes:
            self.append(byte)
        self.disk = disk
        self.secnum = secnum

    def getFileNum(self):
        return self[ATARI_IDX_FILENUM] >> 2

    def setFileNum(self, fnum):
        self[ATARI_IDX_FILENUM]  &= 3
        self[ATARI_IDX_FILENUM]  += fnum << 2

    def getByteCount(self):
        return self[ATARI_IDX_BYTECOUNT] & 0x7f

    def setByteCount(self, count):
        self[ATARI_IDX_BYTECOUNT] = count
        if count != ATARI_BYTES_PER_FILE_SECTOR:
            self[ATARI_IDX_BYTECOUNT] |= 0x80

    def getNextSector(self):
        nextsec = self[ATARI_IDX_FILENUM] & 3
        nextsec = nextsec * 256 + self[ATARI_IDX_FORWARD_PTR]
        return nextsec

    def setNextSector(self, nextsec):
        self[ATARI_IDX_FILENUM] &= 0xfc
        self[ATARI_IDX_FILENUM] |= nextsec >> 8
        self[ATARI_IDX_FORWARD_PTR] = nextsec & 0xff

    def getData(self):
        data = [self[idx] for idx in range(self.getByteCount())]
        return data

    def setData(self, data):
        nb_bytes = len(data)
        if nb_bytes > ATARI_BYTES_PER_FILE_SECTOR:
            raise Exception('attemp to put too many bytes in a sector!')
        for idx in range(nb_bytes):
            self[idx] = data[idx]
        self.setByteCount(nb_bytes)

    def getLine(self):
        return "fnum:%02u bytes%03u next:%04u"%(self.getFileNum(), self.getByteCount(), self.getNextSector())

    def __str__(self):
        return "<SECTOR %s> %s bytes fnum:%s next:%s\n%s"%(str(self.secnum), str(self.getByteCount()), str(self.getFileNum()), str(self.getNextSector()), self.dump())

    def equal(self, sector):
        if len(self) != len(sector):
            return False
        for idx in range(len(self)):
            if self[idx] != sector[idx]:
                return False
        return True

    def dump(self):
        return dump(self)

    def update(self):
        self.disk.writeSector(self.secnum, self)

class BOOT_SECTOR(SECTOR):
    def __init__(self, bytes=None, disk=None, secnum=None):
        SECTOR.__init__(self, bytes, disk, secnum)
        
    def getFlags(self):
        return self[ATARI_IDX_BS_FLAGS]
        
    def getNbSectors(self):
        return self[ATARI_IDX_BS_NB_SECTOR]

    def getLoadAddr(self):
        return self[ATARI_IDX_BS_LOAD_ADDR] + self[ATARI_IDX_BS_LOAD_ADDR + 1] * 256

    def getInitAddr(self):
        return self[ATARI_IDX_BS_INIT_ADDR] + self[ATARI_IDX_BS_INIT_ADDR + 1] * 256

    def __str__(self):
        return '<BOOT SECTOR %s> flags:$%02x sectors:$%02x addr:$%04x init:$%04x\n%s'%(str(self.secnum), self.getFlags(), self.getNbSectors(), self.getLoadAddr(), self.getInitAddr(), self.dump())

class FAT_SECTOR(SECTOR):
    def __init__(self, bytes=None, disk=None, secnum=None):
        SECTOR.__init__(self, bytes, disk, secnum)
        self.entries = []
        for entrystart in range(0, ATARI_ENTRY_SIZE * ATARI_ENTRIES_PER_SECTOR, ATARI_ENTRY_SIZE):
            self.entries.append(ENTRY(self, entrystart / ATARI_ENTRY_SIZE))

    def getEntry(self, entrynum):
        return self.entries[entrynum]
        
    def getFlags(self, entrynum):
        idx = ATARI_ENTRY_SIZE * entrynum
        return self[idx]
        
    def getSectorCount(self, entrynum):
        idx = ATARI_ENTRY_SIZE * entrynum + ATARI_IDX_FAT_SECTOR_COUNT
        return self[idx] * 256 + self[idx] + 1
        
    def getStartingSector(self, entrynum):
        idx = ATARI_ENTRY_SIZE * entrynum + ATARI_IDX_FAT_STARTING_SECTOR
        return self[idx] * 256 + self[idx] + 1
        
    def getFilename(self, entrynum):
        fname = ""
        start = ATARI_ENTRY_SIZE * entrynum + ATARI_IDX_FAT_FILENAME
        stop = ATARI_ENTRY_SIZE * entrynum + ATARI_IDX_FAT_FILENAME_END
        for idx in range(start, stop):
            fname += chr(self[idx])
        return fnameAta2Dos(fname)

    def __str__(self):
        return '<FAT SECTOR %s>\n%s'%(str(self.secnum), self.dump())

class VTOC_SECTOR(SECTOR):
    def __init__(self, bytes=None, disk=None, secnum=None):
        SECTOR.__init__(self, bytes, disk, secnum)

    def getNbFreeSectors(self):
        return self[ATARI_OFS_VTOC_FREE_BYTES] + self[ATARI_OFS_VTOC_FREE_BYTES + 1] * 256

    def getNbTotalSectors(self):
        return self[ATARI_OFS_VTOC_TOTAL_BYTES] + self[ATARI_OFS_VTOC_TOTAL_BYTES + 1] * 256

    def setNbFreeSectors(self, freesec):
        self[ATARI_OFS_VTOC_FREE_BYTES] = freesec & 0xff
        self[ATARI_OFS_VTOC_FREE_BYTES + 1] = freesec >> 8
        
    def setNbTotalSectors(self, freesec):
        self[ATARI_OFS_VTOC_TOTAL_BYTES] = freesec & 0xff
        self[ATARI_OFS_VTOC_TOTAL_BYTES + 1] = freesec >> 8
        
    def getFreeSectors(self):
        sectors = []
        for secnum in range(ATARI_BOOT_SECTOR, ATARI_LAST_SECTOR):
            if self.isSectorFree(secnum):
                sectors.append(secnum)
        return sectors

    def isSectorFree(self, secnum):
        # if bit == 1 sector is free
        byteidx, bitidx = secnumToVtocIdx(secnum)
        if self[byteidx] & ATARI_VTOC_MASK_AND[bitidx]:
            return True
        else:
            return False

    def freeSector(self, secnum):
        # must set the sector bit to 1
        byteidx, bitidx = secnumToVtocIdx(secnum)
        self[byteidx] |= ATARI_VTOC_MASK_AND[bitidx]
        self.setNbFreeSectors(self.getNbFreeSectors() + 1)

    def allocSector(self, secnum):
        # must set the sector bit to 0
        byteidx, bitidx = secnumToVtocIdx(secnum)
        self[byteidx] &= ATARI_VTOC_MASK_OR[bitidx]
        self.setNbFreeSectors(self.getNbFreeSectors() - 1)

    def getMap(self, width=ATARI_TRACK_SIZE):
        text = ""
        for idx, secnum in enumerate(range(ATARI_BOOT_SECTOR, ATARI_LAST_SECTOR)):
            if self.isSectorFree(secnum):
                text += ' .'
            else:
                text += ' +'
            if idx % width == width - 1:
                text += '\n'
        return text

    def __str__(self):
        return "<VTOC SECTOR %s> free:%u\n%s"%(str(self.secnum), self.getNbFreeSectors(), self.dump())

class DISK():
    def __init__(self, name="noname"):
        self.name = name
        #~ self.status = ATARI_SIO_STATUS_BIT_WRITE_PROTECTED | ATARI_SIO_STATUS_BIT_ACTIVE 

    def getEntries(self):
        entries = []
        for secnum in range(ATARI_FAT_START, ATARI_FAT_STOP):
            sector = self.readSector(secnum)
            for x in range(ATARI_ENTRIES_PER_SECTOR):
                entry = sector.getEntry(x)
                if entry.getFlags() == 0:
                    # stopped at the first unused entry
                    break
                entries.append(entry)
        return entries

    def getUsedEntries(self):
        temp_entries = self.getEntries()
        entries = []
        for entry in temp_entries:
            if entry.getFlags() & ATARI_FILE_FLAG_USED:
                if not entry.getFlags() & ATARI_FILE_FLAG_DELETED:
                    entries.append(entry)
        return entries

    def getEntryByName(self, fname):
        entries = []
        filenum = 0
        for secnum in range(ATARI_FAT_START, ATARI_FAT_STOP):
            sector = self.readSector(secnum)
            for entrynum in range(8):
                entry = sector.getEntry(entrynum)
                if entry.getFilename() == fname:
                    if entry.getFlags() & ATARI_FILE_FLAG_DELETED:
                        pass
                        #~ return None
                    if entry.getFlags() & ATARI_FILE_FLAG_OUTPUT:
                        return None
                    return entry
                filenum += 1
        return None

    def getFirstFreeEntry(self):
        entries = []
        filenum = 0
        sectors = []
        for secnum in range(ATARI_FAT_START, ATARI_FAT_STOP):
            sectors.append(self.readSector(secnum))
            sector = sectors[-1]
            for x in range(ATARI_ENTRIES_PER_SECTOR):
                entry = sector.getEntry(x)
                if entry.getFlags() == 0 or entry.getFlags() & ATARI_FILE_FLAG_DELETED:
                    return entry # real first free entry
        # FAT sectors are already loaded, not necessary to reread
        #~ for sector in sectors:
            #~ for x in range(ATARI_ENTRIES_PER_SECTOR):
                #~ entry = sector.getEntry(x)
                #~ if entry.getFlags() & ATARI_FILE_FLAG_DELETED:
                    #~ return entry # not reallye free entry, but it works...
        raise Exception(ATARI_ERR_DIR_FULL)
            
    def directory(self, verbose=0):
        dir = []
        for entry in self.getUsedEntries():
                dir.append(entry.getDirLine(verbose))
        dir.append("%03u free sectors"%self.readSector(ATARI_VTOC).getNbFreeSectors())
        return '\n'.join(dir)

    def getDirectory(self, verbose=0):
        return [entry.getFilename() for entry in self.getUsedEntries()]

    def readFile(self, fname):
        entry = self.getEntryByName(fname)
        if entry == None:
            raise Exception(ATARI_ERR_FILE_NOT_FOUND%fname)
        body = []
        filenum = None
        secnum = entry.getStartingSector()
        for sectorcount in range(entry.getSectorCount()):
            sector = self.readSector(secnum)
            if filenum == None:
                filenum = sector.getFileNum()
            if sector.getFileNum() != filenum:
                raise Exception(ATARI_ERR_FN_MISMATCH%secnum)
            body += sector.getData()
            secnum = sector.getNextSector()
        textbody = ""
        for byte in body:
            textbody += chr(byte)
        return textbody

    def traceFile(self, entry):
        vtoc = self.readSector(ATARI_VTOC)
        sectors = []
        secnum = entry.getStartingSector()
        filenum = None
        while secnum != 0:
            sectors.append(secnum)
            sector = self.readSector(secnum)
            if filenum == None:
                filenum = sector.getFileNum()
            if sector.getFileNum() != filenum:
                raise Exception(ATARI_ERR_FN_MISMATCH%secnum)
            if vtoc.isSectorFree(secnum):
                raise Exception(ATARI_ERR_VTOC_MISMATCH%secnum)
            secnum = sector.getNextSector()
        return sectors

    def deleteFile(self, fname):
        entry = self.getEntryByName(fname)
        if entry == None:
            raise Exception(ATARI_ERR_FILE_NOT_FOUND%fname)
        if entry.getFlags() & ATARI_FILE_FLAG_LOCKED:
            raise Exception(ATARI_ERR_FILE_LOCKED)
        if entry.getFlags() & ATARI_FILE_FLAG_DELETED:
            pass
            #~ raise Exception('%s already deleted!'%fname)
        else:
            sectors = self.traceFile(entry)
            vtoc = self.readSector(ATARI_VTOC)
            for secnum in sectors:
                #~ if vtoc.isSectorFree(secnum):
                    #~ raise Exception(ATARI_ERR_FN_MISMATCH%secnum)
                #~ else:
                    vtoc.freeSector(secnum)
            entry.setFlags(entry.getFlags() | ATARI_FILE_FLAG_DELETED)
            entry.update()
            vtoc.update()

    def rename(self, fname, newfname):
        entry = self.getEntryByName(fname)
        if entry == None:
            raise Exception(ATARI_ERR_FILE_NOT_FOUND%fname)
        if entry.getFlags() & ATARI_FILE_FLAG_LOCKED:
            raise Exception(ATARI_ERR_FILE_LOCKED)
        entry.setFilename(newfname)
        entry.update()

    def __writeDataSector__(self, secnum, data, fnum, nextsec):
        data = [ord(car) for car in data]
        sector = SECTOR()
        sector.setData(data)
        sector.setFileNum(fnum)
        sector.setNextSector(nextsec)
        self.writeSector(secnum, sector)        
        return

    def writeFile(self, fname, body):
        vtoc = self.readSector(ATARI_VTOC)
        size = len(body)
        nb_sec = size / ATARI_BYTES_PER_FILE_SECTOR
        if size % ATARI_BYTES_PER_FILE_SECTOR != 0:
            nb_sec += 1
        entry = self.getEntryByName(fname)
        if entry != None:
            # file exists, must be deleted
            # enough free sectors?
            if nb_sec > vtoc.getNbFreeSectors() + entry.getSectorCount():
                raise Exception(ATARI_ERR_DISK_FULL)
            self.deleteFile(fname)
            vtoc = self.readSector(ATARI_VTOC)
        else:
            # file doesn't exist
            entry = self.getFirstFreeEntry()
            # enough free sectors?
            if nb_sec > vtoc.getNbFreeSectors():
                raise Exception(ATARI_ERR_DISK_FULL)
        # ok, let's write file sectors
        fnum = entry.getFileNum()
        freesec = vtoc.getFreeSectors()
        secidx = 0
        data = []
        for idx in range(len(body)):
            if idx % ATARI_BYTES_PER_FILE_SECTOR == 0:
                data = []
                secnum = freesec[secidx]
                if secidx < (len(freesec) - 1):
                    nextsec = freesec[secidx + 1]
            data.append(body[idx])
            if idx == len(body) - 1:
                nextsec = 0
            if idx % ATARI_BYTES_PER_FILE_SECTOR == ATARI_BYTES_PER_FILE_SECTOR - 1:
                self.__writeDataSector__(secnum, data, fnum, nextsec)
                vtoc.allocSector(secnum)
                secidx += 1
        if data != []:
            self.__writeDataSector__(secnum, data, fnum, nextsec)
            vtoc.allocSector(secnum)
        vtoc.update()
        # FAT update
        entry.setFilename(fname)
        entry.setStartingSector(freesec[0])
        entry.setSectorCount(nb_sec)
        entry.setFlags(ATARI_FILE_FLAG_USED)
        entry.update()

    def getCheckUp(self):
        err = False
        lines = []
        for entry in self.getUsedEntries():
            line = "%-12s fn:%02u "%(entry.getFilename(), entry.filenum)
            try:
                self.traceFile(entry)
                line += 'OK'
            except Exception as(errmsg):
                line += str(errmsg)
                err = True
            lines.append(line)
        if err:
            return '\n'.join(lines)
        else:
            # if no error detected, returns ALWAYS an empty string
            return ""

class VIRTUAL_DISK(DISK):
    def __init__(self, fname):
        DISK.__init__(self, fname)
        self.fname= fname

    def readSector(self, secnum):
        fp = open(self.fname, 'rb')
        fp.seek((secnum-1) * ATARI_SECTOR_SIZE)
        cars = fp.read(ATARI_SECTOR_SIZE)
        fp.close()
        if len(cars) != ATARI_SECTOR_SIZE:
            raise Exception(ATARI_ERR_CANT_READ_SECTOR)
        if secnum == ATARI_BOOT_SECTOR:
            return BOOT_SECTOR([ord(car) for car in cars], self, secnum)
        elif secnum in range(ATARI_FAT_START, ATARI_FAT_STOP):
            return FAT_SECTOR([ord(car) for car in cars], self, secnum)
        elif secnum == ATARI_VTOC:
            return VTOC_SECTOR([ord(car) for car in cars], self, secnum)
        else:
            return SECTOR([ord(car) for car in cars], self, secnum)
        
    def writeSector(self, secnum, sector):
        if len(sector) != ATARI_SECTOR_SIZE:
            raise Exception(ATARI_ERR_BAD_SECTOR_SIZE)
        fp = open(self.fname, 'rb+')
        fp.seek((secnum-1) * ATARI_SECTOR_SIZE)
        for byte in sector:
            fp.write(chr(byte))
        fp.close()
        
    def __str__(self):
        return "<VIRTUAL DISK> %s"%self.fname

if __name__ == "__main__":
    
    import sys
    
    disk = VIRTUAL_DISK("./ressource/TITREUSE")
    print disk.getDirectory()
    
    
    sys.exit(124)
    
    import sys
    import shutil
    
    ERROR_MISSING = "An exception is missing!"
    TEST_DISK = "./utest/mandatory/fonts"

    def test_writeSector():
        TEST_DISK2 = "./utest/fonts2"
        shutil.copyfile(TEST_DISK, TEST_DISK2)
        disk1 = VIRTUAL_DISK(TEST_DISK)
        disk2 = VIRTUAL_DISK(TEST_DISK2)
        sector = disk2.readSector(ATARI_VTOC)
        sector[0] ^= 1
        disk2.writeSector(ATARI_VTOC, sector)
        for secnum in range(ATARI_BOOT_SECTOR, ATARI_LAST_SECTOR + 1):
            sector1 = disk1.readSector(secnum)
            sector2 = disk2.readSector(secnum)
            if secnum != ATARI_VTOC:
                assert sector1.equal(sector2)
            else:
                assert sector1[0] == sector2[0] ^ 1
                for bytenum in range(1,ATARI_SECTOR_SIZE):
                    assert sector1[bytenum] == sector2[bytenum]

    def utest():
        TEST_DISK = "./utest/mandatory/fonts"
        sect = BOOT_SECTOR()
        assert len(sect) == ATARI_SECTOR_SIZE
        for bytenum in range(ATARI_SECTOR_SIZE):
            assert sect[bytenum] == ATARI_DEFAULT_BYTE
        disk = VIRTUAL_DISK(TEST_DISK)
        body = disk.readFile("ROBIN.SET")
        assert len(disk.readFile("ROBIN.SET")) == 1025
        bytes = [1, 2, 3]
        assert unserialize(serialize(bytes)) == bytes
        assert unserialize(MAGIC_WORD_TEXT) == []
        assert unserialize(MAGIC_WORD_TEXT+'a') == None
        assert unserialize(MAGIC_WORD_TEXT[:-1]) == None
        assert unserialize(MAGIC_WORD_TEXT[:-2]) == None
        assert unserialize(MAGIC_WORD_TEXT[:-1]+ '012') == None
        assert unserialize(MAGIC_WORD_TEXT+'a0') == [0xa0]
        assert unserialize(12.3) == None
        vtoc = disk.readSector(ATARI_VTOC)
        for secnum in range(ATARI_BOOT_SECTOR, 720):
            assert not vtoc.isSectorFree(secnum)
        assert vtoc.getNbFreeSectors() == 0
        disk = VIRTUAL_DISK("./utest/mandatory/DOS25.XFD")
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 48

    def utest_Vtoc():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/DOS25.XFD")
        disk = VIRTUAL_DISK("./utest/DOS25.XFD")
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 48
        for secnum in [3, 4, 5, 6]:
            vtoc.freeSector(secnum)
        disk.writeSector(ATARI_VTOC, vtoc)
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 52
        for secnum in [717, 718, 719]:
            vtoc.allocSector(secnum)
        vtoc.update()
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 49

    def utest_deleteFile():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/DOS25.XFD")
        disk = VIRTUAL_DISK("./utest/DOS25.XFD")
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 48
        disk.deleteFile("BOBTERM.COM")
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 48 + 197

    def utestFatEntries():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        fatsec = disk.readSector(361)
        entry = fatsec.getEntry(3)
        entry.setFlags(0x0)
        assert entry.getFlags() == 0x0
        entry.setFlags(0xff)
        assert entry.getFlags() == 0xff
        assert fatsec[3 * ATARI_ENTRY_SIZE] == 0xff
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        fatsec = disk.readSector(361)
        entry = fatsec.getEntry(3)
        assert entry.getFilename() == 'ARC.COM'
        entry.setFilename('PFEUH.CON')
        assert entry.getFilename() == 'PFEUH.CON'
        entry.setSectorCount(720)
        assert entry.getSectorCount() == 720
        entry.setSectorCount(33)
        assert entry.getSectorCount() == 33
        entry.setStartingSector(720)
        assert entry.getStartingSector() == 720
        entry.setStartingSector(33)
        assert entry.getStartingSector() == 33
        assert entry.getFileNum() == 3

        
    def utest_writeFile():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        entry = disk.getEntryByName('BOBTERM.COM')
        assert entry.getFileNum() == 5
        entry = disk.getFirstFreeEntry()
        assert entry.getFileNum() == 14
        sectors = []
        for secnum in range(ATARI_FAT_START, ATARI_FAT_STOP):
            sectors.append(disk.readSector(secnum))
        for x in range(14, ATARI_MAX_ENTRIES):
            secnum = x / ATARI_ENTRIES_PER_SECTOR
            entrynum = x % ATARI_ENTRIES_PER_SECTOR
            entry = sectors[secnum].entries[entrynum]
            entry.setFilename("FILE%04u.TXT"%x)
            entry.setFlags(ATARI_FILE_FLAG_USED)
        for sector in sectors:
            sector.update()
        disk.deleteFile('BOBTERM.COM')
        entry = disk.getFirstFreeEntry()
        assert entry.getFileNum() == 5
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        body = asciiToAtascii(open("./utest/mandatory/hello.asm", "rb").read(-1))
        disk.writeFile('HELLO.LST', body)
        body2 = disk.readFile('HELLO.LST')
        assert body == body2
        text = ''.join([chr(x) for x in range(256)])
        text2 = asciiToAtascii(atasciiToAscii(text))
        assert text2 == text
    
    def test_regularSector():
        sector = SECTOR([0xff for idx in range(128)])
        sector.setByteCount(125)
        sector.setFileNum(14)
        sector.setNextSector(674)
        assert sector.getFileNum() == 14
        assert sector.getNextSector() == 674
        assert sector.getByteCount()== 125
        sector.setByteCount(125)
        sector.setFileNum(14)
        sector.setNextSector(674)
        assert sector.getFileNum() == 14
        assert sector.getNextSector() == 674
        assert sector.getByteCount()== 125
        sector.setByteCount(39)
        sector.setFileNum(14)
        sector.setNextSector(0)
        assert sector.getFileNum() == 14
        assert sector.getNextSector() == 0
        assert sector.getByteCount()== 39

    def test_getCheckUp():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        assert disk.getCheckUp() == ""
        vtoc = disk.readSector(ATARI_VTOC)
        vtoc.freeSector(343)
        vtoc.update()
        assert disk.getCheckUp() != ""
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        sector = disk.readSector(343)
        sector.setNextSector(1)
        sector.update()
        assert disk.getCheckUp() != ""

    def test_deleteFile():
        shutil.copyfile("./utest/mandatory/DOS25.XFD", "./utest/testdisk")
        disk = VIRTUAL_DISK("./utest/testdisk")
        assert disk.getCheckUp() == ""
        entry = disk.getEntryByName('SDF.BAS')
        fn = entry.filenum
        for x in range(100):
            disk.deleteFile('SDF.BAS')
            disk.writeFile('SDF.BAS', 'pass %03u'%(x+1))
        entry = disk.getEntryByName('SDF.BAS')
        assert entry.filenum == fn
        assert disk.getCheckUp() == ""
        

    def test_createDisk():
        disk = createDisk('./utest/toto')
        vtoc = disk.readSector(ATARI_VTOC)
        assert vtoc.getNbFreeSectors() == 707
        assert vtoc.getNbTotalSectors() == 707

    def test_fnameDos2Ata():
        assert fnameDos2Ata('FILENAME.EXT') == 'FILENAMEEXT'
        assert fnameDos2Ata('F.E') == 'F       E  '
        assert fnameDos2Ata('F') == 'F          '
        assert fnameDos2Ata('.F') == '        F  '

    utest()
    test_fnameDos2Ata()
    test_regularSector()
    test_writeSector()
    utest_Vtoc()
    utestFatEntries()
    utest_deleteFile()
    utest_writeFile()
    test_getCheckUp()
    test_deleteFile()
    test_createDisk()
    sys.stdout.write('A L L   T E S T S   P A S S E D !\n')


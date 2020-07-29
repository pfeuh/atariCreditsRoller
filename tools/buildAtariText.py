#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

REVERTED_VIDEO_ON = '<'
REVERTED_VIDEO_OFF = '>'

VIDEO_MODE_NORMAL = 1
VIDEO_MODE_REVERTED = 2

EOL = 0

CH_DELCHR       = chr(0xFE) # delete char under the cursor
CH_ENTER        = chr(0x9B)
CH_ESC          = chr(0x1B)
CH_CURS_UP      = chr(28)
CH_CURS_DOWN    = chr(29)
CH_CURS_LEFT    = chr(30)
CH_CURS_RIGHT   = chr(31)
CH_TAB          = chr(0x7F) # tabulator
CH_EOL          = chr(0x9B) # end-of-line marker
CH_CLR          = chr(0x7D) # clear screen
CH_BEL          = chr(0xFD) # bell
CH_DEL          = chr(0x7E) # back space (delete char to the left)
CH_RUBOUT       = chr(0x7E) # back space (old, deprecated)
CH_DELLINE      = chr(0x9C) # delete line
CH_INSLINE      = chr(0x9D) # insert line

def getGlyphe(byte, multi=False):
    byte &=127
    if multi:
        # for multicolor font
        byte = ord(chr(byte).upper())
    if byte < 32:
        return '.'
    else:
        return chr(byte)

def buildAtariText(text):
    video_mode = VIDEO_MODE_NORMAL
    ret_str = ""
    for car in text:
        if car == REVERTED_VIDEO_ON:
            video_mode = VIDEO_MODE_REVERTED
        elif car == REVERTED_VIDEO_OFF:
            video_mode = VIDEO_MODE_NORMAL
        else:
            if video_mode == VIDEO_MODE_NORMAL:
                ret_str += car
            else:
                ret_str += chr(ord(car) + 128)
    return ret_str

def getAS65Code(text, label="nonameStr", nb_columns=16, multi=False):
    bytes = []
    for car in text:
        bytes.append(ord(car))
    bytes.append(EOL)
        
    ret_text = ".export _%s\n_%s:\n"%(label, label)
    for col_num, value in enumerate(bytes):
        if not(col_num % nb_columns):
            ret_text += "        .byte "
            scibuf = ""

        scibuf += getGlyphe(value, multi)
            
        if (col_num % nb_columns) == (nb_columns - 1):
            ret_text += "$%02x "%value
            ret_text += "; %s\n"%scibuf
        else:
            ret_text += "$%02x, "%value
            
    if col_num % nb_columns:
        ret_text = ret_text[:-2] + " "
        for count in range(nb_columns - (col_num % nb_columns) - 1):
            ret_text += "     "
        ret_text += "; %s\n"%scibuf
    return ret_text + "\n"

def getAll(records, multi=False):
    ret_text = ""
    declare_text = ""
    for record in records:
        text = record[0]
        label = record[1]
        ret_text += getAS65Code(buildAtariText(text), label, multi=multi)
        declare_text += "extern const char %s[];\n"%label
    return ret_text + declare_text

if __name__ == "__main__":

    #~ records = [
        #~ ("%c<Credits Roller      c.1989 Pierre Faller>"%CH_CLR, "titleText"),
        #~ ("\nC : load <C>redits     ", "menuOpt1"),
        #~ ("\nF : load <F>ont        ", "menuOpt2"),
        #~ ("\nS : <S>peed            ", "menuOpt3"),
        #~ ("\nR : <R>ainbow          ", "menuOpt4"),
        #~ ("\nB : <B>ackground color ", "menuOpt5"),
        #~ ("\nT : <T>ext color       ", "menuOpt6"),
        #~ ("\nG : <G>o!", "menuOpt7"),
        #~ ("\nX : e<X>it\n", "menuOpt8"),]

    records = [
        ("<Credits Roller      c.1989 Pierre Faller>", "titleText"),
        ("\r\nC : load <C>redits     ", "menuOpt1"),
        ("\r\nF : load <F>ont        ", "menuOpt2"),
        ("\r\nS : <S>peed            ", "menuOpt3"),
        ("\r\nR : <R>ainbow          ", "menuOpt4"),
        ("\r\nB : <B>ackground color ", "menuOpt5"),
        ("\r\nT : <T>ext color       ", "menuOpt6"),
        ("\r\nG : <G>o!", "menuOpt7"),
        ("\r\nX : e<X>it\n\r", "menuOpt8"),
        ("Select speed : <S>low <N>ormal <F>ast", "speedLabels"),]

    sys.stdout.write(getAll(records))

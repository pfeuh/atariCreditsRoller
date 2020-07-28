#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

def printDec(value):
    charbuf = [0, 0, 0, 0, 0, 0]
    x = 0
    
    if not value:
        sys.stdout.write('0')
        return
    
    
    while value:
        charbuf[x] = chr((value % 10) + ord('0'));
        x += 1
        value = value / 10;
        #~ if(not value):
            #~ charbuf[x] = '0';
            #~ x += 1
    
    x -= 1
    while(x != -1):
        sys.stdout.write(charbuf[x]);
        x -= 1
        
    return 


for x in (0, 1, 2, 12, 123, 1234, 12345, 65535):
    print x," ",
    printDec(x)
    print

#~ void printDec(unsigned int value)
#~ {
    #~ char charbuf[5];
    #~ unsigned char x = 0;
    
    #~ if(!value)
    #~ {
        #~ cputc('0');
        #~ return;
    #~ }
    
    #~ while(value)
    #~ {
        #~ charbuf[x++] = (value % 10) + '0';
        #~ value = value / 10;
        #~ if(!value)
            #~ charbuf[x++] = '0';
    #~ }
        
    #~ while(--x != 255)
        #~ cputc(charbuf[x]);
#~ }

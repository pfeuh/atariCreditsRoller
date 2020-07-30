#!/bin/bash
echo $SHELL $0 "launched by" $USER
cd ./../out/
atari800 -nobasic -xl -xlxe_rom ATARIXL.ROM

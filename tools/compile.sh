#!/bin/sh
echo $SHELL $0 "launched by" $USER
cd ./../src/
#~ cl65 -O -t atari credits.c printTool.c rainbow.s text.s -o CREDITS.COM
cl65 -O -t atari credits.c printTool.c rainbow.s labels.c -o CREDITS.COM

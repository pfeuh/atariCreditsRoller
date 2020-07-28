#!/bin/bash
cd ./../src/
cl65 -O -t atari credits.c printTool.c rainbow.s text.s -o CREDITS.COM

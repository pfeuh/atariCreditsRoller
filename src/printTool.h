#ifndef PRINT_TOOL_H
#define PRINT_TOOL_H

#define INPUT_STRING_BUFFER_SIZE 13
#define ERR_BAD_USER_BYTE -1

/* Check for errors */
#if !defined(__ATARI__)
#  error This module may only be used when compiling for the Atari!
#endif

#include <stdio.h>
#include <stdbool.h>

extern void printNumber(unsigned int value);
extern char* inputString(void);
extern int inputNumber(char* text);

#endif


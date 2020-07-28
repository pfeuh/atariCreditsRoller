#ifndef PRINT_TOOL_H
#define PRINT_TOOL_H

#define INPUT_STRING_BUFFER_SIZE 12

extern void newLine(void);
extern void print(char const str_ptr[]);
extern void printLn(char const str_ptr[]);
extern void printDec(unsigned int value);
extern char* inputString(void);

#endif


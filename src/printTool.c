
#include "printTool.h"
#include <conio.h>
#include <stdio.h>
#include <stdbool.h>

char inputStringBuffer[INPUT_STRING_BUFFER_SIZE];

void newLine(void)
{
    printf("\n");
    //~ cputc(CH_EOL);
    //~ gotox(0);
}

void print(char const str_ptr[])
{
    while(*str_ptr)
    {
        if(*str_ptr == 10)
            newLine();
        else
            cputc(*str_ptr);
        str_ptr++;
    }
}

void printLn(char const str_ptr[])
{
    print(str_ptr);
    newLine();
}

void printDec(unsigned int value)
{
    char charbuf[5];
    unsigned char x = 0;
    
    if(!value)
    {
        cputc('0');
        return;
    }
    
    while(value)
    {
        charbuf[x++] = (value % 10) + '0';
        value = value / 10;
        //~ if(!value)
            //~ charbuf[x++] = '0';
    }
        
    while(--x != 255)
        cputc(charbuf[x]);
}

bool isValidChar(char car)
{
    if(car == '.') return true;
    if(car < '0') return false;
    if(car <= '9') return true; // 0-9
    if(car < 'A') return false; 
    if(car <= 'Z') return true; // A-Z
    if(car < 'a') return false;
    if(car <= 'z') return true; // a-z
    return false;
}

char* inputString(void)
{
    // protected from buffer overflow
    unsigned char index = 0;
    bool run = true;
    char car;

    while(run)
    {
        car = getchar();
    
        if(isValidChar(car))
        {
            if(index < (INPUT_STRING_BUFFER_SIZE - 1))
            {
                inputStringBuffer[index++] = car;
                cputc(car);
                inputStringBuffer[index] = 0;
            }
        }
        else
        {
            switch(car)
            {
                case CH_DEL:
                    if(index != 0)
                    {
                        printf("%c", car);
                        inputStringBuffer[index] = 0;
                        index--;
                    }
                    break;
                case CH_ESC:
                    cputc(car);
                    run = false;
                    *inputStringBuffer = 0;
                    break;
                case CH_ENTER:
                    run = false;
                    break;
                default:
                    break;
            }
        }
    }
    
    newLine();
    return inputStringBuffer;
}

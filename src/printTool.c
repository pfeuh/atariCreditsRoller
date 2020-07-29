
#include "printTool.h"
#include <conio.h>
#include <stdio.h>
#include <stdbool.h>

char inputStringBuffer[INPUT_STRING_BUFFER_SIZE];

void printNumber(unsigned int value)
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
        car = cgetc();
    
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
                        cputc(car);
                        inputStringBuffer[index] = 0;
                        index--;
                    }
                    break;
                case CH_ESC:
                    cputc(CH_ESC);
                    printf("\n");
                    //~ cputc(car);
                    run = false;
                    *inputStringBuffer = 0;
                    break;
                case CH_ENTER:
                    printf("\n");
                    run = false;
                    break;
                default:
                    break;
            }
        }
    }
    return inputStringBuffer;
}

int inputNumber(char* text)
{
    unsigned char index = 0;
    char car;
    unsigned int value = 0;
    
    while(text[index])
    {
        car = text[index];
        switch(car)
        {
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                value = value * 10 + car - '0';
                if(value > 255)
                    return ERR_BAD_USER_BYTE;
                index++;
                break;
            default:
                return ERR_BAD_USER_BYTE;
                break;
        }
    }
    return value;
}


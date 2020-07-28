#include <stdio.h>
#include <stdlib.h>
#include <atari.h>
#include <conio.h>
#include <stdbool.h>
#include <peekpoke.h>
#include <string.h>
#include "types.h";
#include "atariMemoryMap.h";
#include "printTool.h"

#define FNAME_SIZE 13
#define FONT_SIZE 1024
#define SUCCESS false
#define FAILURE true
#define ERR_BAD_USER_BYTE -1
#define FRAME_NUM (RTCLOK + 2)
#define SIZE_OF_BLANK_LINES 1000

char fontName[FNAME_SIZE];
char creditsName[FNAME_SIZE];
bool stopApp;
byte consolValue;
byte creditsFontPageNum;
byte MenuFontPageNum;
byte CreditsBackgroundColor;
byte CreditsForegroundColor;
byte scrollSpeed;
word MenuTextAddr;
bool rainbowFlag;

#define NORMAL 0
#define SLOW 1
#define FAST 2

// display list instructions for ANTIC
#define ATA_DL_VSCROL 0x20
#define ATA_DL_BLK8 0x70

#define FRAME_NUM (RTCLOK + 2)

#define NB_COLUMNS 40
#define CREDITS_TEXT_ADDR 0x5000

// TODO: protect against RESET
// TODO: disk catalog before asking for filemane
// TODO: avoid printf, do a minimal lib to print
// TODO: create a load/save full configuation (text + font + ...)

extern const char titleText[];
extern const char menuOpt1[];
extern const char menuOpt2[];
extern const char menuOpt3[];
extern const char menuOpt4[];
extern const char menuOpt5[];
extern const char menuOpt6[];
extern const char menuOpt7[];
extern const char menuOpt8[];

// In the assembler file rainbow.s for timing problem
extern void doRainbow();

void waitVbiEnd()
{
    byte frame_num = PEEK(FRAME_NUM);
    while(frame_num == PEEK(FRAME_NUM));
}

void setScreenAt(word base)
{
    POKEW(PEEKW(SDLSTL) + 4, base);
}

void setFontAtPage(byte page)
{
    POKEW(CHBAS, page);
}

void setCreditsEnvironement()
{
    // let's switch to credits scrolling environement
    setScreenAt(CREDITS_TEXT_ADDR);
    setFontAtPage(creditsFontPageNum);
    POKE(COLOR1, CreditsForegroundColor);
    POKE(COLOR2, CreditsBackgroundColor);
    POKE(COLOR4, CreditsBackgroundColor);
}

void setMenuEnvironement()
{
    // let's switch to menu environement
    setScreenAt(MenuTextAddr);
    setFontAtPage(MenuFontPageNum);
    POKE(COLOR1, ATA_DEFAULT_COLOR1);
    POKE(COLOR2, ATA_DEFAULT_COLOR2);
    POKE(COLOR4, ATA_DEFAULT_COLOR4);
}

char getChar()
{
    while(!kbhit());    
    return cgetc();
}

char getCommand()
{
    while(!kbhit())
        if(consolValue != PEEK(CONSOL))
        {
            consolValue = PEEK(CONSOL);
            if(startKeyPressed())
            {
                waitVbiEnd();
                setCreditsEnvironement();
                setScreenAt(CREDITS_TEXT_ADDR + SIZE_OF_BLANK_LINES);
                while(startKeyPressed())
                {
                    if(rainbowFlag)
                        doRainbow();
                    waitVbiEnd();
                }
                setMenuEnvironement();
                setScreenAt(MenuTextAddr);
            }
        }
    
    return cgetc();
}

int getUserByte(char* text)
{
    byte index = 0;
    byte car;
    word value = 0;
    
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

char* getSpeedLabel()
{
    switch(scrollSpeed)
    {
        case SLOW:
            return ("Slow");
            break;
        case NORMAL:
            return ("Normal");
            break;
        case FAST:
            return ("Fast");
            break;
    }
    return 0;
}

char* getRainbowLabel()
{
    if(rainbowFlag)
        return ("ON");
    else
        return ("OFF");
}

void printMenu()
{
    print(menuOpt1);
    print(creditsName);
    print(menuOpt2);
    print(fontName);
    print(menuOpt3);
    print(getSpeedLabel());
    print(menuOpt4);
    print(getRainbowLabel());
    print(menuOpt5);
    printDec(CreditsBackgroundColor);
    print(menuOpt6);
    printDec(CreditsForegroundColor);
    print(menuOpt7);
    print(menuOpt8);
}

bool loadFile(char* fname, char* target, word max_size)
{
    FILE *fp;
    word read_size; 
    fp = fopen(fname, "rb");
    if (fp == NULL) 
    {
        printf("File %s not found!\n", fname);
		return FAILURE;
    }
	read_size = fread(target, sizeof(char), max_size, fp);
	fclose(fp);
    if(!read_size)
    {
        printf("Unexpected end of file %s!\n", fname);
		return FAILURE;
    }
	return SUCCESS;
}

byte loadCredits(char* fname)
{   
    if(loadFile(fname, (char*)(CREDITS_TEXT_ADDR + SIZE_OF_BLANK_LINES), -1) == SUCCESS)
        return SUCCESS;
    else
        return FAILURE;
}

byte loadFont(char* fname)
{
    byte font_base = (PEEK(RAMTOP) - 8);
    
    if(loadFile(fname, (char*)(font_base * 256), FONT_SIZE) == SUCCESS)
    {
        creditsFontPageNum = font_base;
        return SUCCESS;
    }
    else
        return FAILURE;
}

void vScroll()
{
    word text_ptr = CREDITS_TEXT_ADDR;
    word screen_ptr = PEEKW(SDLSTL + 4);
    bool running = true;
    bool line_number_changed;
    byte line_num = 0;
    byte toggle = 0;

    while(!startKeyPressed())
    {
        if(rainbowFlag)
            doRainbow();
        waitVbiEnd();
        if(optionKeyPressed())
        {
            running = false;
            break;
        }
    }
    
    while(running)
    {
        line_number_changed = false;
        toggle ^= 1;
    
        switch(scrollSpeed)
        {
            case SLOW:
                if(!toggle)
                {
                    line_num ++;
                    line_number_changed = true;
                }
                break;
            case NORMAL:
                line_num ++;
                line_number_changed = true;
                break;
            case FAST:
                line_num += 2;
                line_number_changed = true;
                break;
        }
        if(line_number_changed)
        {
            if((line_num & 7) == 0)
            {
                setScreenAt(text_ptr);
                text_ptr += NB_COLUMNS;
            }
            POKE(VSCROL, 7 & line_num);
        }

        if(rainbowFlag)
            doRainbow();
        
        waitVbiEnd();
        
        if(optionKeyPressed())
            running = false;
    }
}

void modifyDisplayList()
{
    byte* ptr = (byte*)PEEKW(SDLSTL);
    byte index;
    
    // edit display list to allow vertical scrolling
    *(ptr + 3) |= ATA_DL_VSCROL;
    for(index=6;index<=27;index++)
        *(ptr + index) |= ATA_DL_VSCROL;
}

void cmdLoadCredits()
{
    char*fname;
    
    printf("Input credits name : ");
    fname =  inputString();
    if(*fname)
    {
        if(loadCredits(fname) == SUCCESS)
        {
            strcpy(creditsName, fname);
            printf("Credits %s Loaded\n", creditsName);
        }
    }
}

void cmdLoadFont()
{
    char*fname;
    
    printf("Input font name : ");
    fname =  inputString();
    if(*fname)
    {
        if(loadFont(fname) == SUCCESS)
        {
            strcpy(fontName, fname);
            printf("Font %s Loaded\n", fontName);
        }
    }
}

void cmdChangeBackgroundColor()
{
    int   value;
    char* text;
    
    printf("Input bg color value : ");
    text = inputString();
    if(!*text)
        return;
    
    value = getUserByte(text);
    if(value == ERR_BAD_USER_BYTE)
        printf("Bad 8 bits value!\n");
    else
    {
        CreditsBackgroundColor = value;
        printf("Bg color value %d\n", CreditsBackgroundColor);
    }
}

void cmdChangeTextColor()
{
    int   value;
    char* text;
    
    printf("Input text color value : ");
    text = inputString();
    if(!*text)
        return;
    
    value = getUserByte(text);
    if(value == ERR_BAD_USER_BYTE)
        printf("Bad 8 bits value!\n");
    else
    {
        CreditsForegroundColor = value;
        printf("Bg color value %d\n", CreditsBackgroundColor);
    }
}

void cmdChangeSpeed()
{
    byte command;
    bool modified = true;
    printf("Select speed : Slow Normal Fast");
    command = getChar();
    switch(command)
    {
        case 's':
        case 'S':
            scrollSpeed = SLOW;
            break;
        case 'n':
        case 'N':
            scrollSpeed = NORMAL;
            break;
        case 'f':
        case 'F':
            scrollSpeed = FAST;
            break;
        case CH_ESC:
            cputc(command);
            modified = false;
            newLine();
            break;
        default:
            modified = false;
            printf("%c", CH_BEL);
            break;
    }
    if(modified)
        printf("\n%s\n", getSpeedLabel());
}

void cmdSetRainbow()
{
    if(rainbowFlag)
        rainbowFlag = false;
    else
        rainbowFlag = true;
    printf("\nRainbow set to %s\n", getRainbowLabel());
}

void cmdGo()
{
    setCreditsEnvironement();
    POKE(VSCROL, 0);
    
    vScroll();
    
    POKE(VSCROL, 0);
    setMenuEnvironement();
}

void execCommand(char command)
{
    switch(command)
    {
        case CH_ENTER:
            printMenu();
            break;
        case 'x':
        case 'X':
            stopApp = true;
            break;
        case 'c':
        case 'C':
            cmdLoadCredits();
            break;
        case 'f':
        case 'F':
            cmdLoadFont();
            break;
        case 'b':
        case 'B':
            cmdChangeBackgroundColor();
            break;
        case 's':
        case 'S':
            cmdChangeSpeed();
            break;
        case 'r':
        case 'R':
            cmdSetRainbow();
            break;
        case 'g':
        case 'G':
            cmdGo();
            break;
        case 't':
        case 'T':
            cmdChangeTextColor();
            break;
        default:
            printf("%c", CH_BEL);
            break;
    }
}

int main (void)
{
    char command;
    
    consolValue = PEEK(CONSOL);
    strcpy(fontName, "<ROM FONT>");
    strcpy(creditsName, "<EMPTY>");
    
    MenuFontPageNum = PEEK(CHBAS);
    MenuTextAddr = PEEKW(PEEKW(SDLSTL) + 4);
    
    creditsFontPageNum = MenuFontPageNum;
    scrollSpeed = NORMAL;
    CreditsBackgroundColor = 66;
    CreditsForegroundColor = 14;

    modifyDisplayList();
    
    loadCredits("NIKON.SCR");
    loadFont("ACCENTUE.FNT");
    strcpy(creditsName, "NIKON.SCR");
    strcpy(fontName, "ACCENTUE.FNT");
    rainbowFlag = true;
    
    setMenuEnvironement();
    
    clrscr();
    printf(titleText);

    printMenu();

    while(!stopApp)
    {        
        printf ("Select an option : \n");
        command = getCommand();
        execCommand(command);
    }
    return EXIT_SUCCESS;
}

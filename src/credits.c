
// TODO: protect against RESET
// TODO: disk catalog before asking for filemane
// TODO: create a load/save full configuation (text + font + ...)
// TODO: sync problem, when pressing START, system font is still displayed during 1 frame
// TODO: pressing START reveals that static frame is on VSCROLL = 1 instead of VSCROLL = 0

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
#define FRAME_NUM (RTCLOK + 2)
#define SIZE_OF_BLANK_LINES 1000

// rainbow's speed
#define NORMAL 0
#define SLOW 1
#define FAST 2

// display list instructions for ANTIC
#define ATA_DL_VSCROL 0x20
#define ATA_DL_BLK8 0x70

#define NB_COLUMNS 40
#define CREDITS_TEXT_ADDR 0x5000

extern const char titleText[];
extern const char menuOpt1[];
extern const char menuOpt2[];
extern const char menuOpt3[];
extern const char menuOpt4[];
extern const char menuOpt5[];
extern const char menuOpt6[];
extern const char menuOpt7[];
extern const char menuOpt8[];
extern const char speedLabels[];
// doRainbow() is in the assembler file rainbow.s for timing problem
extern void doRainbow();

char fontName[FNAME_SIZE];
char creditsName[FNAME_SIZE];
bool stopApp;
byte consolValue;
byte creditsFontPageNum;
byte menuFontPageNum;
byte creditsBackgroundColor;
byte creditsTextColor;
byte scrollSpeed;
word menuTextAddr;
bool rainbowFlag;
word textSize;

void printIOError()
{
    printf("I/O error!\n");
}

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
    POKE(COLOR1, creditsTextColor);
    POKE(COLOR2, creditsBackgroundColor);
    POKE(COLOR4, creditsBackgroundColor);
}

void setMenuEnvironement()
{
    // let's switch to menu environement
    setScreenAt(menuTextAddr);
    setFontAtPage(menuFontPageNum);
    POKE(COLOR1, ATA_DEFAULT_COLOR1);
    POKE(COLOR2, ATA_DEFAULT_COLOR2);
    POKE(COLOR4, ATA_DEFAULT_COLOR4);
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
    
        if(!selectKeyPressed())
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

void printMenu()
{
    cprintf(menuOpt1);
    cprintf(creditsName);
    cputc('(');
    printNumber(textSize);
    cputc(')');
    cprintf(menuOpt2);
    cprintf(fontName);
    cprintf(menuOpt3);
    cprintf(getSpeedLabel());
    cprintf(menuOpt4);
    cprintf(getRainbowLabel());
    cprintf(menuOpt5);
    printNumber(creditsBackgroundColor);
    cprintf(menuOpt6);
    printNumber(creditsTextColor);
    cprintf(menuOpt7);
    cprintf(menuOpt8);
}

word loadFile(char* fname, char* target, word max_size)
{
    FILE *fp;
    word read_size; 
    fp = fopen(fname, "rb");
    if (fp == NULL) 
		return 0;
	read_size = fread(target, sizeof(char), max_size, fp);
	fclose(fp);
	return read_size;
}

void loadCredits(char* fname)
{   
    word file_size = loadFile(fname, (char*)(CREDITS_TEXT_ADDR + SIZE_OF_BLANK_LINES), -1);
    if (!file_size)
        printIOError();
    else
    {
        textSize = file_size;
        strcpy(creditsName, fname);
    }
}

void loadFont(char* fname)
{
    byte font_base = (PEEK(RAMTOP) - 8);
    word file_size =  loadFile(fname, (char*)(font_base * 256), FONT_SIZE);
    if (file_size < FONT_SIZE)
        printIOError();
    else
    {
        creditsFontPageNum = font_base;
        strcpy(fontName, fname);
    }
}

void cmdLoadCredits()
{
    char*fname;
    
    cprintf("Input credits name : ");
    fname =  inputString();
    if(*fname)
        loadCredits(fname);
}

void cmdLoadFont()
{
    char*fname;
    
    cprintf("Input font name : ");
    fname =  inputString();
    if(*fname)
        loadFont(fname);
}

void cmdChangeBackgroundColor()
{
    int   value;
    char* text;
    
    cprintf("Input bg color value : ");
    text = inputString();
    if(!*text)
        return;
    
    value = inputNumber(text);
    if(value == ERR_BAD_USER_BYTE)
        cprintf("Bad 8 bits value!\n");
    else
    {
        creditsBackgroundColor = value;
        cprintf("Bg color value ");
        printNumber(creditsBackgroundColor);
        cprintf("\n");
    }
}

void cmdChangeTextColor()
{
    int   value;
    char* text;
    
    cprintf("Input text color value : ");
    text = inputString();
    if(!*text)
        return;
    
    value = inputNumber(text);
    if(value == ERR_BAD_USER_BYTE)
        cprintf("Bad 8 bits value!\n");
    else
    {
        creditsTextColor = value;
        cprintf("Text color value ");
        printNumber(creditsTextColor);
        cprintf("\n");
    }
}

void cmdChangeSpeed()
{
    byte command;
    bool modified = true;
    cprintf(speedLabels);
    command = cgetc();
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
            //~ newLine();
            break;
        default:
            modified = false;
            printf("%c", CH_BEL);
            break;
    }
    printf("\n");
}

void cmdSetRainbow()
{
    if(rainbowFlag)
        rainbowFlag = false;
    else
        rainbowFlag = true;
    printf("Rainbow set to %s\n", getRainbowLabel());
}

void cmdGo()
{
    setCreditsEnvironement();
    POKE(VSCROL, 0);
    
    vScroll();
    
    POKE(VSCROL, 0);
    setMenuEnvironement();
}

bool isValidCommand(char cmd)
{
    switch(cmd)
    {
        case 'h':
        case 'H':
        case '?':
        case 'x':
        case 'X':
        case 'c':
        case 'C':
        case 'f':
        case 'F':
        case 'b':
        case 'B':
        case 's':
        case 'S':
        case 'r':
        case 'R':
        case 'g':
        case 'G':
        case 't':
        case 'T':
            return true;
            break;
        default:
            return false;
    }
}

char getCommand()
{
    byte cmd;
    
    cprintf("Select an option : ");
    while(1)
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
                    setScreenAt(menuTextAddr);
                }
            }
        cmd =  cgetc();
        if(isValidCommand(cmd))
        {
            printf("%c\n", cmd);
            return cmd;
        }
        else
            printf("%c\n", CH_BEL);
    }
}

void execCommand(char command)
{
    switch(command)
    {
        case 'h':
        case 'H':
        case '?':
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
            cputc(CH_BEL);
            break;
    }
}

int main (void)
{
    consolValue = PEEK(CONSOL);
    strcpy(fontName, "<ROM FONT>");
    strcpy(creditsName, "<EMPTY>");
    
    menuFontPageNum = PEEK(CHBAS);
    menuTextAddr = PEEKW(PEEKW(SDLSTL) + 4);
    
    creditsFontPageNum = menuFontPageNum;
    scrollSpeed = NORMAL;
    creditsBackgroundColor = 66;
    creditsTextColor = 14;

    modifyDisplayList();
    
    loadCredits("NIKON.SCR");
    loadFont("ACCENTUE.FNT");
    strcpy(creditsName, "NIKON.SCR");
    strcpy(fontName, "ACCENTUE.FNT");
    rainbowFlag = true;
    
    setMenuEnvironement();
    
    clrscr();
    cprintf(titleText);

    printMenu();

    while(!stopApp)
    {        
        execCommand(getCommand());
    }
    return EXIT_SUCCESS;
}

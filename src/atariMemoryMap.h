#ifndef ATARI_MEMORY_MAP_H
#define ATARI_MEMORY_MAP_H

#include <peekpoke.h>

/* ******************** */
/* ** MEMORY MAPPING ** */
/* ******************** */

#define ATA_FRM_CNT_HI           18 // 0x0012
#define ATA_FRM_CNT_MID          19 // 0x0013
#define ATA_FRM_CNT_LOW          20 // 0x0014
#define ATA_LMARGIN              82 // 0x0052
#define ATA_RMARGIN              83 // 0x0053
#define ATA_RAMTOP              106 // 0x006a
#define ATA_DLIST               560 // 0x0230
#define ATA_TEXT_COLOR          709 // 0x02c5
#define ATA_BG_COLOR            710 // 0x02c6
#define ATA_BORDER_COLOR        712 // 0x02c8
#define ATA_MEMLO               743 // 0x02e7
#define ATA_CHBAS               756 // 0x02f4
#define ATA_SCREEN_ADDR      -25568 // 0x9c20 39968
#define ATA_CONSOL           -12257 // 0xd01f 53279

/* ************ */
/* ** VALUES ** */
/* ************ */

#define ATA_KEY_OPTION 4
#define ATA_KEY_SELECT 2
#define ATA_KEY_START  1

#define ATA_DEFAULT_PLAYFIELD_COLOR 148
#define ATA_DEFAULT_TEXT_COLOR 202
#define ATA_DEFAULT_BORDER_COLOR 0

/* ************ */
/* ** MACROS ** */
/* ************ */

#define optionKeyPressed() (!(PEEK(ATA_CONSOL) & ATA_KEY_OPTION))
#define selectKeyPressed() (!(PEEK(ATA_CONSOL) & ATA_KEY_SELECT))
#define startKeyPressed()  (!(PEEK(ATA_CONSOL) & ATA_KEY_START))

#endif


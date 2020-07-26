#ifndef ATARI_MEMORY_MAP_H
#define ATARI_MEMORY_MAP_H

#include <peekpoke.h>

/* ******************** */
/* ** MEMORY MAPPING ** */
/* ******************** */

#define RTCLOK     18 // 0x0012
#define LMARGN     82 // 0x0052
#define RMARGN     83 // 0x0053
#define RAMTOP    106 // 0x006a
#define SDLSTL    560 // 0x0230
#define PCOLR0    704 // 0x02c0
#define PCOLR1    705 // 0x02c1
#define PCOLR2    706 // 0x02c2
#define PCOLR3    707 // 0x02c3
#define COLOR0    708 // 0x02c4
#define COLOR1    709 // 0x02c5
#define COLOR2    710 // 0x02c6
#define COLOR3    711 // 0x02c7
#define COLOR4    712 // 0x02c8
#define MEMLO     743 // 0x02e7
#define CHBAS     756 // 0x02f4
#define CONSOL -12257 // 0xd01f 53279
#define HSCROL -11260 // 0xd404 54276
#define VSCROL -11259 // 0xd405 54277

/* ************ */
/* ** VALUES ** */
/* ************ */

#define ATA_KEY_OPTION 4
#define ATA_KEY_SELECT 2
#define ATA_KEY_START  1

#define ATA_DEFAULT_COLOR2 148
#define ATA_DEFAULT_COLOR1 202
#define ATA_DEFAULT_COLOR4 0

#define ATA_DL_VSCROL 0x20
#define ATA_DL_BLK8 0x70

/* ************ */
/* ** MACROS ** */
/* ************ */

#define optionKeyPressed() (!(PEEK(CONSOL) & ATA_KEY_OPTION))
#define selectKeyPressed() (!(PEEK(CONSOL) & ATA_KEY_SELECT))
#define startKeyPressed()  (!(PEEK(CONSOL) & ATA_KEY_START))

#endif


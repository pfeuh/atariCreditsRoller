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
#define VDSLST    512 // 0x0200
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
#define CH        764 // 0x02fc
#define COLPM0 -12270 // 0xd012 53266
#define COLPM1 -12269 // 0xd013 53267
#define COLPM2 -12268 // 0xd014 53268
#define COLPM3 -12267 // 0xd015 53269
#define COLPF0 -12266 // 0xd016 53270
#define COLPF1 -12265 // 0xd017 53271
#define COLPF2 -12264 // 0xd018 53272
#define COLPF3 -12263 // 0xd019 53273
#define COLBK  -12262 // 0xd01a 53274
#define CONSOL -12257 // 0xd01f 53279
#define HSCROL -11260 // 0xd404 54276
#define VSCROL -11259 // 0xd405 54277
#define WSYNC  -11254 // 0xd40a 54282
#define VCOUNT -11253 // 0xd40b 54283

/* ************ */
/* ** VALUES ** */
/* ************ */

#define ATA_KEY_OPTION 4
#define ATA_KEY_SELECT 2
#define ATA_KEY_START  1

#define ATA_DEFAULT_COLOR1 202
#define ATA_DEFAULT_COLOR2 148
#define ATA_DEFAULT_COLOR4 0

/* ************ */
/* ** MACROS ** */
/* ************ */

#define optionKeyPressed() (!(PEEK(CONSOL) & ATA_KEY_OPTION))
#define selectKeyPressed() (!(PEEK(CONSOL) & ATA_KEY_SELECT))
#define startKeyPressed()  (!(PEEK(CONSOL) & ATA_KEY_START))

#endif


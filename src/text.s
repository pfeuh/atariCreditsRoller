.export _dlist, _scrolledTextPtr

;                   ---********************---
;                   ---*** display list ***---
;                   ---********************---
    
                    ; some constants from antic.h
                    DL_BLK8      = $70 ; 8 empty lines
                    DL_CHR40x8x1 = $02 ; text 40 colums of 8x8 pixels 1 color
                    DL_LMS       = $40 ; load memory screen
                    DL_JVB       = $41 ; jump & wait end of verticl blank
                    DL_VSCROL    = $20 ; attribute fine vertical scroll

_dlist:             .byte DL_BLK8
                    .byte DL_BLK8
                    .byte DL_BLK8
                    .byte DL_CHR40x8x1 | DL_LMS
_scrolledTextPtr:   .word $00
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1 | DL_VSCROL
                    .byte DL_CHR40x8x1
                    .byte DL_JVB
                    .word _dlist

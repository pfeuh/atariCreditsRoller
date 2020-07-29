
.include "atari.inc"


.export _doRainbow

_doRainbow:
            ; first color for rainbow, incrementing every frame
            LDY RTCLOK + 2
            
            ;full black over the rainbow
            LDA #0
            STA COLPF2
            STA COLBK
            
_rainbowLoop1:
            ; passing some vertical lines, nothing happends
            ; we are still in vertical blanking after VBI
            ; but the line counter never stops
            LDX VCOUNT
            CPX #8      ; starting line of upper rainbow
            BNE _rainbowLoop1
        
            LDX #16;

_rainbowLoop2:
            ; next 16 vertical lines, playfield and borders are rainbowing
            ; this is the rainbow at the top of the screen
            DEX         ; counting rainbow lines
            DEY         ; decrementing color
            STY WSYNC
            STY COLPF2
            STY COLBK
            CPX #0
            BNE _rainbowLoop2
            
            LDA COLOR2
            STA COLPF2
            STA COLBK

_rainbowLoop3:
            ;nothing happens, waiting first line of bottom rainbow
            LDX VCOUNT
            CPX #108    ; starting line of lower rainbow
            BNE _rainbowLoop3
        
            LDX #16;

_rainbowLoop4:
            ; next 16 vertical lines, playfield and borders are rainbowing
            ; this is the rainbow at the bottom of the screen
            DEX         ; counting rainbow lines
            INY         ; incrementing color (reverse direction of first rainbow)
            STY WSYNC
            STY COLPF2
            STY COLBK
            CPX #0
            BNE _rainbowLoop4
            
            ;full black under the rainbow
            STX COLPF2
            STX COLBK

            RTS

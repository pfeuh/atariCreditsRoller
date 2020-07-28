.export _doRainbow

_doRainbow:
            ; first color for rainbow, incrementing every frame
            LDY 20      ; RTCLOCK + 2
            
            ;full black over the rainbow
            LDA #0
            STA $d018   ; COLPF2
            STA $d01a   ; COLBK
            
_rainbowLoop1:
            ; passing some vertical lines, nothing happends
            ; we are still in vertical blanking after VBI
            ; but the line counter never stops
            LDX $d40b   ; VCOUNT
            CPX #8      ; starting line of upper rainbow
            BNE _rainbowLoop1
        
            LDX #16;

_rainbowLoop2:
            ; next 16 vertical lines, playfield and borders are rainbowing
            ; this is the rainbow at the top of the screen
            DEX         ; counting rainbow lines
            DEY         ; decrementing color
            STY $d40a   ; WSYNC
            STY $d018   ; COLPF2
            STY $d01a   ; COLBK
            CPX #0
            BNE _rainbowLoop2
            
            LDA 710     ; COLOR2
            STA $d018   ; COLPF2
            STA $d01a   ; COLBK

_rainbowLoop3:
            ;nothing happens, waiting first line of bottom rainbow
            LDX $d40b   ; VCOUNT
            CPX #108    ; starting line of lower rainbow
            BNE _rainbowLoop3
        
            LDX #16;

_rainbowLoop4:
            ; next 16 vertical lines, playfield and borders are rainbowing
            ; this is the rainbow at the bottom of the screen
            DEX         ; counting rainbow lines
            INY         ; incrementing color (reverse direction of first rainbow)
            STY $d40a   ; WSYNC
            STY $d018   ; COLPF2
            STY $d01a   ; COLBK
            CPX #0
            BNE _rainbowLoop4
            
            ;full black under the rainbow
            STX $d018   ; COLPF2
            STX $d01a   ; COLBK

            RTS

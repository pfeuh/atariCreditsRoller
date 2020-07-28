.export _titleText
_titleText:
        .byte $c3, $f2, $e5, $e4, $e9, $f4, $f3, $a0, $d2, $ef, $ec, $ec, $e5, $f2, $a0, $a0 ; Credits Roller  
        .byte $a0, $a0, $a0, $a0, $e3, $ae, $b1, $b9, $b8, $b9, $a0, $d0, $e9, $e5, $f2, $f2 ;     c.1989 Pierr
        .byte $e5, $a0, $c6, $e1, $ec, $ec, $e5, $f2, $00                                    ; e Faller.

.export _menuOpt1
_menuOpt1:
        .byte $0a, $43, $20, $3a, $20, $6c, $6f, $61, $64, $20, $c3, $72, $65, $64, $69, $74 ; .C : load Credit
        .byte $73, $20, $20, $20, $20, $20, $00                                              ; s     .

.export _menuOpt2
_menuOpt2:
        .byte $0a, $46, $20, $3a, $20, $6c, $6f, $61, $64, $20, $c6, $6f, $6e, $74, $20, $20 ; .F : load Font  
        .byte $20, $20, $20, $20, $20, $20, $00                                              ;       .

.export _menuOpt3
_menuOpt3:
        .byte $0a, $53, $20, $3a, $20, $d3, $70, $65, $65, $64, $20, $20, $20, $20, $20, $20 ; .S : Speed      
        .byte $20, $20, $20, $20, $20, $20, $00                                              ;       .

.export _menuOpt4
_menuOpt4:
        .byte $0a, $53, $20, $3a, $20, $d2, $61, $69, $6e, $62, $6f, $77, $20, $20, $20, $20 ; .S : Rainbow    
        .byte $20, $20, $20, $20, $20, $20, $00                                              ;       .

.export _menuOpt5
_menuOpt5:
        .byte $0a, $42, $20, $3a, $20, $c2, $61, $63, $6b, $67, $72, $6f, $75, $6e, $64, $20 ; .B : Background 
        .byte $63, $6f, $6c, $6f, $72, $20, $00                                              ; color .

.export _menuOpt6
_menuOpt6:
        .byte $0a, $54, $20, $3a, $20, $d4, $65, $78, $74, $20, $63, $6f, $6c, $6f, $72, $20 ; .T : Text color 
        .byte $20, $20, $20, $20, $20, $20, $00                                              ;       .

.export _menuOpt7
_menuOpt7:
        .byte $0a, $47, $20, $3a, $20, $c7, $6f, $21, $00                                    ; .G : Go!.

.export _menuOpt8
_menuOpt8:
        .byte $0a, $58, $20, $3a, $20, $65, $d8, $69, $74, $0a, $00                          ; .X : eXit..

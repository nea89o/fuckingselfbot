
grammar Query;

prog:   stat+ EOF? ;

stat:   expr                # rawExpr
    |   ID '=' expr         # assign
    ;

expr:   expr '.' ID                                 # access
    |   expr '(' (args=expr*) ')'                   # call
    |   expr op=('*'|'/') expr                      # MulDiv
    |   expr op=('+'|'-') expr                      # AddSub
    |   INT                                         # int
    |   STRINGLITERAL                               # string
    |   ID                                          # id
    |   '(' expr ')'                                # parens
    |   '{' (args=arguments)? prog '}'              # func
    ;

arguments: ID (',' ID)* '->';

STRINGLITERAL : '"' ( StringEscapeSeq | ~( '\\' | '"' | '\r' | '\n' ) )* '"' ;
StringEscapeSeq : '\\' ( 't' | 'n' | 'r' | '"' | '\\' | '$' | ('0'..'9')) ;

MUL :   '*' ; // assigns token name to '*' used above in grammar
DIV :   '/' ;
ADD :   '+' ;
SUB :   '-' ;
ID  :   [a-zA-Z]+ ;      // match identifiers
INT :   [0-9]+ ;         // match integers
NEWLINE:'\r'? '\n' -> skip ;     // return newlines to parser (is end-statement signal)
WS : [ \t]+ -> skip ; // toss out whitespace
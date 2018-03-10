grammar Formula;

formula : expression+ EOF;

expression
    : ID '(' term (',' term)* ')'                               # atom
    | '(' subexpression = expression ')'                                        # parenthesis
    | '~' subexpression = expression                                            # not
    | left = expression '=>' right = expression                 # then
    | left = expression '<=>' right = expression                # iff
    | left = expression '<=' right = expression                 # if
    | condition = expression '?' truthy = expression ':' falsy = expression # ternary
    | left = expression '&' right = expression                  # and
    | left = expression '|' right = expression                  # or
    | left = expression '^' right = expression                  # xor
    | 'forall' VAR 'in' (range_expr | set_expr)  scope = expression     # forall
    | 'exists' VAR 'in' (range_expr | set_expr)  scope = expression     # exists
    | TRUE                                                      # true
    | FALSE                                                     # false
    | VAR                                                       # variable
    | ID                                                        # identifier
    ;

term
    : ID                                              # newTermID
    | VAR                                             # newTermVar
    | int_expr                                        # doIntExpr
    ;

int_expr
    : '(' int_expr ')'                                # parenthesizedIntExpression
    | '|' int_expr '|'                                # absValueExpression
    | '-' int_expr                                    # unaryMinusExpression
    | int_expr op=( '*' | '/' | '%' ) int_expr        # multiplicativeExpression
    | int_expr op=( '+' | '-' ) int_expr              # additiveExpression
    | VAR                                             # newIntVariable
    | NUMBER                                          # newInteger
    ;

range_expr 
    : '{' (int_expr '..' int_expr) '}' ;

set_expr 
    : '{' term (',' term)*  '}' ;

// Tokens
TRUE            : 'True';
FALSE           : 'False';
ID              : LETTER ALPHANUM*;
VAR             : '_' LETTER ALPHANUM*;
NUMBER          : DIGIT+;

// Drops whitespaces and comments
WS              : [ \t\n\r]+ -> skip ;
COMMENTS        : ('/*' .*? '*/' | '//' ~'\n'* '\n' ) -> skip;

// Fragments
fragment DIGIT    : '0' .. '9';
fragment UPPER    : 'A' .. 'Z';
fragment LOWER    : 'a' .. 'z';
fragment LETTER   : LOWER | UPPER;
fragment WORD     : LETTER | '_' | '$' | '#' | '.';
fragment ALPHANUM : WORD | DIGIT;

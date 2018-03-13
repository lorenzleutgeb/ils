grammar Formula;

formula: expression+ EOF;

expression
    : (TRUE | FALSE)                                                                           # booleanConstant
    | predicate (PAREN_OPEN terms PAREN_CLOSE)?                                                # atom
    | PAREN_OPEN expression PAREN_CLOSE                                                        # parenthesizedExpression
    | NOT expression                                                                           # unary
    | condition = expression QUESTION truthy = expression COLON falsy = expression             # ternary
    | left = expression op = (AND | BAR | IF | IFF | THEN | XOR) right = expression            # binary
    | quantifier = (EXISTS |FORALL) variable = TVAR IN range = termSet scope = expression      # termQuantification
    | quantifier = (EXISTS |FORALL) variable = PVAR IN range = predicateSet scope = expression # predicateQuantification
    ;

predicate
    : CON  # predicateConstant
    | PVAR # predicateVariable
    ;

predicates
    : predicate (COMMA predicates)?
    ;

predicateSet
    : CURLY_OPEN predicates CURLY_CLOSE # predicateEnumeration
    ;

term
    : CON           # termConstant
    | TVAR          # termVariable
    | intExpression # termIntExpression
    ;

terms
    : term (COMMA terms)?
    ;

termSet
    : SQUARE_OPEN minimum = intExpression DOTS maximum = intExpression SQUARE_CLOSE # intExpressionRange
    | CURLY_OPEN terms CURLY_CLOSE                                                  # termEnumeration
    ;

intExpression
    : PAREN_OPEN intExpression PAREN_CLOSE                                          # parenthesizedIntExpression
    | BAR intExpression BAR                                                         # absIntExpression
    | SUB intExpression                                                             # negIntExpression
    | left = intExpression op = (MUL | DIV | MOD | ADD | SUB) right = intExpression # binaryIntExpression
    | variable = TVAR                                                               # varIntExpression
    | number = NUMBER                                                               # numIntExpression
    ;

// Boolean constants:
TRUE        : 'true' | '⊤';
FALSE       : 'false' | '⊥';

// Quantifiers:
FORALL      : 'forall' | '∀';
EXISTS      : 'exists' | '∃';

// Parentheses and braces:
PAREN_OPEN   : '(';
PAREN_CLOSE  : ')';
CURLY_OPEN   : '{';
CURLY_CLOSE  : '}';
SQUARE_OPEN  : '[';
SQUARE_CLOSE : ']';

// Boolean connectives:
AND         : '&' | '∧';
THEN        : '=>' | '→' | '⊃';
IF          : '<=' | '←' | '⊂';
IFF         : '<=>' | '↔';
XOR         : '^' | '⊕';
NOT         : '~' | '¬';
QUESTION    : '?';
COLON       : ':';

// Arithmetic constants:
NUMBER      : DIGIT+;

// Arithmetic connectives:
MUL         : '*';
DIV         : '/';
MOD         : '%';
ADD         : '+';
SUB         : '-';

// Miscellaneous:
IN          : 'in' | '∈';
COMMA       : ',';
DOTS        : '...' | '…';

// NOTE: This character is used both in intExpressions
//       and as a binary boolean connective.
BAR         : '|';
fragment OR : BAR | '∨';

// Variable prefixes:
AT          : '@';
DOLLAR      : '$';

// Drop whitespaces and comments:
WS       : [ \t\n\r]+ -> skip ;
COMMENTS : ('/*' .*? '*/' | '//' ~'\n'* '\n') -> skip;

// Constant terms and predicates:
CON : LOWER ALNUM*;

// Variable terms and predicates:
TVAR : DOLLAR ALNUM+;
PVAR : AT ALNUM*;

fragment DIGIT : '0' .. '9';
fragment UPPER : 'A' .. 'Z';
fragment LOWER : 'a' .. 'z';
fragment ALNUM : LOWER | UPPER | DIGIT;
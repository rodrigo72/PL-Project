import ply.lex as lex
from collections import defaultdict

"""
Forth Lexical Analyzer
"""

tokens = (
    # words
    'COLON', # start
    'SEMICOLON', # end

    # math
    'UCOMPARISON', # unsigned comparison
    'COMPARISON', # signed comparison
    'ARITHMETIC', # arithmetic operators

    # numbers
    'INTEGER',
    'FLOAT',

    # functions
    'WORD',

    # comments
    'LPAREN',
    'RPAREN',
    'BACKSLASH',
    'COMMENT',
    
    # for loop
    'DO', # start
    'LOOP', # end
    'PLUSLOOP', # end

    # while loop
    'BEGIN', # start 
    'UNTIL', # end 
    'AGAIN', # end 
    'WHILE', # middle
    'REPEAT', # end
    
    # conditional logic
    'IF',  # start (could be nested)
    'ELSE', # middle
    'THEN', # end
    
    # other
    'STRING',
    
    # variables
    'VARIABLE',  # declare a variable : 'variable'
    'STORE', # store value in variable : '!'
    'PUSH', # puts the value of a variable on the stack  : '@'
    'GET', # get value from variable : '?'
    
    # constants
    'CONSTANT', # declare a constant
    
    # user input
    'KEY', # get a key from the user
)

states = (
    ('word', 'exclusive'),  # equivalent to a function
    ('commentp', 'exclusive'),  # comment with parentheses
    ('commentb', 'exclusive'),  # comment with backslash
    ('forloop', 'exclusive'),
    ('whileloop', 'exclusive'),
    ('ifstatement', 'exclusive'),
)

# (dá pra juntar, mas assim é mais legível e costumizável se necessário)
t_ignore  = ' \t'
t_word_ignore = ' \t\n'
t_commentp_ignore = ''
t_commentb_ignore = ''
t_forloop_ignore = ' \t\n'
t_whileloop_ignore = ' \t\n'
t_ifstatement_ignore = ' \t\n'


"""
WORD STATE
"""
def t_COLON(t):
    r':\B'
    t.lexer.push_state('word')
    return t


def t_word_SEMICOLON(t):
    r'\B;\B'
    t.lexer.pop_state()
    return t


"""
FOR LOOP STATE
"""
def t_ANY_DO(t):  # could be nested
    r'(do|DO)'
    t.lexer.push_state('forloop')
    return t


def t_forloop_LOOP(t):
    r'(loop|LOOP)'
    t.lexer.pop_state()
    return t


def t_forloop_PLUSLOOP(t):
    r'\+(loop|LOOP)'
    t.lexer.pop_state()
    return t


"""
WHILE LOOP STATE
"""
def t_ANY_BEGIN(t):
    r'(begin|BEGIN)'
    t.lexer.push_state('whileloop')
    t.lexer.while_counter = 0
    return t


def t_whileloop_WHILE(t):
    r'(while|WHILE)'
    if t.lexer.while_counter == 0:
        t.lexer.while_counter += 1
        return t
    else:
        raise lex.LexError("Multiple occurrences of 'WHILE' inside state 'whileloop'")


def t_whileloop_REPEAT(t):
    r'(repeat|REPEAT)'
    t.lexer.pop_state()
    return t


def t_whileloop_UNTIL(t):
    r'(until|UNTIL)'
    t.lexer.pop_state()
    return t


def t_whileloop_AGAIN(t):
    r'(again|AGAIN)'
    t.lexer.pop_state()
    return t


"""
IF STATEMENT STATE
"""
def t_ANY_ifstatement_IF(t):  # could be nested
    r'(if|IF)'
    t.lexer.push_state('ifstatement')
    t.lexer.else_counter = 0
    return t


def t_ifstatement_ELSE(t):
    r'(else|ELSE)'
    if t.lexer.else_counter == 0:
        t.lexer.else_counter += 1
        return t
    else:
        raise lex.LexError("Multiple occurrences of 'ELSE' inside state 'ifstatement'")


def t_ifstatement_THEN(t):
    r'(then|THEN)'
    t.lexer.pop_state()
    return t


"""
COMMENT (BACKSLASH) STATE
"""
def t_ANY_BACKSLASH(t):
    r'\\'
    t.lexer.push_state('commentb')
    pass


def t_commentb_COMMENT(t):
    r'[^\n]+'
    pass


def t_commentb_NEWLINE(t):
    r'\n'
    t.lexer.pop_state()
    pass


"""
COMMENT (PARENTHESES) STATE
"""
def t_ANY_LPAREN(t):
    r'\('
    t.lexer.push_state('commentp')
    pass


def t_commentp_COMMENT(t):
    r'[^)\n]+'
    pass


def t_commentp_RPAREN(t):
    r'\)'
    t.lexer.pop_state()
    pass


"""
ANY STATE
"""
# has to be defined before INTEGER
def t_ANY_FLOAT(t):
    r'(\-?(?:0|[1-9]\d*)(?:\.\d+){1}(?:[eE]\d+)?)'
    t.value = float(t.value)
    return t


# has to be defined before COMPARISON and INTEGER
def t_ANY_UCOMPARISON(t):
    r'\d+(>=|<=|>|<|=)'
    return t


def t_ANY_INTEGER(t):
    r'\d+(?!\S)'
    t.value = int(t.value)
    return t


def t_ANY_ARITHMETIC(t):
    r'(\+|\-|\*|\/|\%|\^)'
    return t


def t_ANY_COMPARISON(t):
    r'(<=|>=|<>|=|<|>|AND|and|OR|or|\?DUP|\?dup)'
    return t


def t_ANY_STRING(t):
    r'(?P<type>.){1}\"\s(?P<string>.+?)\"'
    t.value = (t.lexer.lexmatch.group('type'), t.lexer.lexmatch.group('string'))
    return t


def t_ANY_VARIABLE(t):
    r'variable(?:.+?)(?P<var>\S+)'
    t.value = t.lexer.lexmatch.group('var')
    return t


def t_ANY_GET(t):
    r'(\B|^)\?(\B|$)'
    return t


def t_ANY_PUSH(t):
    r'@'
    return t


def t_ANY_STORE(t):
    r'!'
    return t


def t_ANY_CONSTANT(t):
    r'constant(?:.+?)(?P<var>\S+)'
    t.value = t.lexer.lexmatch.group('var')
    return t


def t_ANY_KEY(t):
    r'key'
    return t


def t_ANY_WORD(t):
    r'\S+'  # r'[a-zA-Z_][a-zA-Z0-9_?-]*'
    return t


def t_ANY_error(t):
    print(f"Illegal character: {t.value[0]}")
    raise lex.LexError("Illegal character")
    

def t_ANY_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


"""
TESTING LEXER
"""

lexer = lex.lex()

# not being used
def get_input():    
    while True:
        try:
            data = input('')
        except EOFError:
            break
        
        if data == '':
            break
        
        lexer.input(data)
        for tok in lexer:
            print(tok)
            

def test_all(tests):
    for test_type, test_values in tests.items():
        test(tests, test_type)
        print()


def test(tests, test_type):
    print(f'Testing {test_type}:')
    for test in tests[test_type]:
        lexer.input(test)
        for tok in lexer:
            print(tok)
        print()


def run_tests():
    tests = defaultdict(lambda: [])
    
    tests['word'].append(
        """
        : word 1 2 + . ; 
        word
        """
    )  # working
    
    tests['commentp'].append(
        """
        : word ( -- comment -- ) 1 2 + . ;
        : word 1 2 ( comment ) + . ;
        ( comment )
        : word 1 2 + ( comment ) . ;
        """
    ) # working
    
    tests['commentb'].append(
        """
        : word 1 2 + . ; \ comment here
        : not-a-comment 1 2 + . ;\comment again
        """
    ) # working
    
    tests['forloop'].append(
        """
        : my-loop 10 0 do i . loop ;
        : TEST   10 0 DO  CR ." Hello "  LOOP ;
        : MULTIPLICATIONS  CR 11 1 DO  DUP I * .  LOOP  DROP ;
        : COMPOUND  ( amt int -- ) SWAP 21 1 DO  I . 2DUP R% + DUP . CR LOOP  2DROP ;  
        : sum ( n -- sum )
            0 swap 1 do
            i +
            loop ; 
        10 3 do i . loop
        """
    ) # working 
    # (the Forth word 'i' copies the current loop index onto the parameter stack)
    
    tests['nested-forloop'].append(
        """
        : test 3 0 DO 1 1 + 3 0 DO . LOOP LOOP ;
        """
    ) 
    
    tests['forloopplus'].append(
        """
        : PENTAJUMPS  50 0 DO  I .  5 +LOOP ;
        : INC-COUNT  DO  I . DUP +LOOP  DROP ;
        10 3 do i . 2 +loop
        """
    ) # working
    
    tests['whileloop'].append(
        """
        : loop-test begin 1 - dup dup . 0 = until ;
        : loop-test BEGIN ... flag UNTIL ;
        : loop-test BEGIN ... flag WHILE ... REPEAT ;
        : loop-test ... AGAIN ;
        \ this should raise an error (multiple WHILE):
        \ : loop-test BEGIN ... flag WHILE ... flag WHILE ... REPEAT ; 
        BEGIN 1 - dup dup . 0 = until
        """
    ) # working
    
    tests['ifstatement'].append(
        """
        : ?FULL  12 = IF  ." It's full "  THEN ;
        : ?DAY  32 < IF  ." Looks good " ELSE  ." no way " THEN ;
        : /CHECK   DUP 0= IF  ." invalid " DROP  ELSE  /  THEN ;
        \ this should raise an error (multiple ELSE):
        \ : ?DAY  32 < IF  ." Looks good " ELSE  . ELSE ." no way " THEN ;
        : factorial ( n -- n! )
            dup 0 = if
            drop 1
            else
            dup 1 - recurse *
            then ;
        12 12 = IF ." It's full " THEN
        """
    ) # working
    
    tests['nested-ifstatement'].append(
        """
        : EGGSIZE ( n -- )
            DUP 18 < IF  ." reject "      ELSE
            DUP 21 < IF  ." small "       ELSE
            DUP 24 < IF  ." medium "      ELSE
            DUP 27 < IF  ." large "       ELSE
            DUP 30 < IF  ." extra large " ELSE
                ." error "
            THEN THEN THEN THEN THEN DROP ;
        """
    )
    
    tests['ucomparison'].append(
        """
        : VEGETABLE  DUP 0<  SWAP 10 MOD 0= + IF  ." ARTICHOKE "  THEN ;
        """
    ) # working
    
    tests['strings'].append(
        """
        : TEST   ." sample " ;
        : "LABEL"  C" REJECT  SMALL   MEDIUM  LARGE   XTRA LRGERROR   " ;
        : TESTKEY ( -- )
            ." Hit a key: " KEY CR
            ." That = " . CR
        ;
        TESTKEY
        """
    ) # working
    
    tests['variables'].append(
        """
        variable abc !
        abc ?
        abc @
        111 constant cba 
        key .
        """
    ) # working
    
    tests['random'].append(
        """
        1 2 2dup . . . .
        """
    )
    
    test(tests, 'strings')
    # test_all(tests)


if __name__ == '__main__':
    run_tests()

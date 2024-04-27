import ply.lex as lex
import yaml


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
    'CHAR',
    
    # variables
    'VARIABLE',  # declare a variable : 'variable'
    'STORE', # store value in variable : '!'
    'PUSH', # puts the value of a variable on the stack  : '@'
    
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
    r'(\+|\-|\*|\/|\%|\^|MOD|mod)'
    return t


def t_ANY_COMPARISON(t):
    r'(<=|>=|<>|=|<|>|AND|and|OR|or|\?DUP|\?dup)'
    return t

def t_ANY_CHAR(t):
    r'(char|CHAR)\s+(?P<char>\S+)?'
    value = t.lexer.lexmatch.group('char')
    if not value or len(value) == 0:
        t.value = ""
    else:
        t.value = value[0]
    return t

def t_ANY_STRING(t):
    r'(?P<type>.){1}\"\s(?P<string>.+?)\"'
    t.value = (t.lexer.lexmatch.group('type'), t.lexer.lexmatch.group('string'))
    return t


def t_ANY_VARIABLE(t):
    r'variable(?:.+?)(?P<var>\S+)'
    t.value = t.lexer.lexmatch.group('var')
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
            

def run_tests():
    with open("testing/tests.yaml", "r") as f:
        yaml_data = yaml.safe_load(f)

    tests = yaml_data['tests']
    
    for test in tests:
        print(f"Test: {test['name']}\n")
        lexer.input(test['input'])
        for tok in lexer:
            print(tok)
        print('\n----------------\n')
        

if __name__ == '__main__':
    run_tests()

import ply.yacc as yacc
from forth_lex import tokens
from collections import defaultdict
import re
import sys
import pyperclip

DEBUG = False
STACK_SIZE = 20
GP = 1
VARIABLES_GP = 2
MAX_VARIABLES = 10
DUP2_GP = 3

# VM : https://ewvm.epl.di.uminho.pt/

"""
RULES
"""

def p_All(p):
    """
    All : Elements
    """
    
    start = [
        'ALLOC 2',
        'ALLOC ' + str(STACK_SIZE + 1),
        'ALLOC ' + str(MAX_VARIABLES),
        'ALLOC 2\n',
        'START',
        '\tPUSHG ' + str(GP) + ' PUSHI 0 STORE 0',
        "\tPUSHG 0 PUSHI 0 STORE 0",  #init loop parameters
        "\tPUSHG 0 PUSHI 0 STORE 1"
    ]

    p[0] = start + p[1] + ["STOP"]


def p_Elements(p):
    """
    Elements : Elements Element
             | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
            
    return p[0]
        

def p_Element(p):
    """
    Element : WordDefinition
            | Variable
            | Char
            | String
            | Arithmetic
            | Comparison
            | Integer
            | Float
            | IfStatement
            | WhileLoop
            | ForLoop
            | Store
            | Push
            | Word
    """
    p[0] = p[1]
    

def p_Char(p):
    """
    Char : CHAR
    """
    p[0] = ["\tPUSHS \"" + str(p[1]) + "\" CHRCODE"]


def p_String(p):
    """
    String : STRING
    """
    if p[1][0] == '.':
        p[0] = "\tPUSHS \"" + p[1][1] + "\" WRITES"
    elif p[1][0] == 'c':
        pass
    

def p_Word(p):
    """
    Word : WORD
    """
    
    p1_to_lower = p[1].lower()
    if p1_to_lower in parser.reserved_words:
        if p1_to_lower == "spaces":
            p[0] = ["\tPUSHA SPACES CALL", "\tPOP 1"]
            parser.auxiliary_labels["spaces"] = (
                True, parser.auxiliary_labels["spaces"][1]
            )
        else:
            p[0] = parser.reserved_words[p1_to_lower]
    else:
        label = parser.word_to_label.get(p1_to_lower, None)
        if label and label in parser.words:
            p[0] = [label]
        elif p1_to_lower in parser.variables:
            variable_number = parser.variables[p1_to_lower]
            p[0] = [
                "\tPUSHG " + str(VARIABLES_GP), 
                "\tPUSHI " + str(variable_number),
                "\tPADD"
            ]
        else:
            raise Exception("Word/ Variable not found in dictionary: " + p[1])
    
    
def p_Integer(p):
    """
    Integer : INTEGER
    """
    p[0] = "\tPUSHI " + str(p[1])
    

def p_Float(p):
    """
    Float : FLOAT
    """
    p[0] = "\tPUSHF " + str(p[1])
    

def p_Arithmetic(p):
    """
    Arithmetic : ARITHMETIC
    """
    
    temp = ""
    
    if p[1] == "+":
        temp = "\tADD"
    elif p[1] == "-":
        temp = "\tSUB"
    elif p[1] == "*":
        temp = "\tMUL"
    elif p[1] == "/":
        temp = "\tDIV"
    elif p[1] == "%" or p[1] == "MOD" or p[1] == "mod":
        temp = "\tMOD"
    else: 
        raise Exception("Unknown arithmetic operator")
    
    p[0] = temp
        

def p_Comparison(p):
    """
    Comparison : COMPARISON
    """
    
    temp = ""
    
    if p[1] == "<":
        temp = "\tINF"
    elif p[1] == ">":
        temp = "\tSUP"
    elif p[1] == "<=":
        temp = "\tINFEQ"
    elif p[1] == ">=":
        temp = "\tSUPEQ"
    elif p[1] == "=":
        temp = "\tEQUAL"
    else:
        raise Exception("Unknown comparison operator")
    
    p[0] = temp


def get_next_word_label():
    parser.next_word_label_idx += 1
    return "<<word" + str(parser.next_word_label_idx) + ">>"


def p_WordDefinition(p):
    """
    WordDefinition : COLON WORD WordBody SEMICOLON
    """
    p2_to_lower = p[2].lower()
    if p2_to_lower not in parser.reserved_words:
        
        if p2_to_lower in parser.variables:
            parser.variables.pop(p2_to_lower)
        
        word_label = get_next_word_label()
        parser.word_to_label[p2_to_lower] = word_label
        temp = []
        temp.extend(p[3])
        parser.words[word_label] = temp
    else:
        raise Exception("Word already defined")
        
    p[0] = []  # does nothing
    

def p_WordBody(p):
    """
    WordBody : WordBodyElements
    """
    p[0] = p[1]
    

def p_WordBodyElements(p):
    """
    WordBodyElements : WordBodyElements BodyElement
                     | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
        

def p_BodyElement(p):
    """
    BodyElement : Integer
                | Char
                | String
                | Arithmetic
                | Comparison
                | Float
                | IfStatement
                | ForLoop
                | WhileLoop
                | Store
                | Push
                | Word
    """
    p[0] = p[1]    

    
def next_for_loop_label():
    label = "FORLOOP" + str(parser.next_for_loop_idx)
    parser.next_for_loop_idx += 1
    return label


def next_endloop_label():
    label = "ENDLOOP" + str(parser.next_endloop_idx)
    parser.next_endloop_idx += 1
    return label


def p_ForLoop(p):
    """
    ForLoop : DO FLBody LOOP
    """
    
    for_loop_label = next_for_loop_label()
    end_loop_label = next_endloop_label()
    parser.stack_used = True
    
    init = [
        # load loop parameter values
        "\tPUSHG 0 LOAD 0",
        "\tPUSHG 0 LOAD 1",

        # store those in the stack
        "\tPUSHA MYPUSH CALL POP 1",
        "\tPUSHA MYPUSH CALL POP 1",
        
        # store new loop parameter values
        "\tPUSHG 0 SWAP STORE 0",
        "\tPUSHG 0 SWAP STORE 1",
    ]
    
    for_loop = [
        "\tPUSHG 0 LOAD 0",
        "\tPUSHG 0 LOAD 1",
        "\tINF",
        "\tJZ " + end_loop_label,
        '\tPUSHG 0',
        '\tDUP 1',
        '\tLOAD 0',
        '\tPUSHI 1',
        '\tADD',
        '\tSTORE 0',
    ]
    
    for index, value in enumerate(p[2]):
        if value == "<<I>>":
            for_loop += [
                '\tPUSHG 0 LOAD 0 PUSHI 1 SUB',
            ]
        else:
            for_loop += [value]
            
    for_loop += ['\tJUMP ' + for_loop_label]
    
    restore = [
        '\tPUSHG 0'
        '\tPUSHA MYPOP CALL',
        '\tSTORE 0',
        
        '\tPUSHG 0',
        '\tPUSHA MYPOP CALL',
        '\tSTORE 1'
    ]
    
    p[0] = init + [for_loop_label + ':'] + for_loop + [end_loop_label + ':'] + restore
    

def p_FLBody(p):
    """
    FLBody : FLBodyElements
    """
    p[0] = p[1]
    

def p_FLBodyElements(p):
    """
    FLBodyElements : FLBodyElements BodyElement
                   | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
            

def next_if_statement_label():
    label = "IFSTATEMENT" + str(parser.if_statement_idx)
    parser.if_statement_idx += 1
    return label

def next_endif_label():
    label = "ENDIF" + str(parser.next_endif_idx)
    parser.next_endif_idx += 1
    return label


def p_IfStatement(p):
    """
    IfStatement : IF ISBody THEN
                | IF ISBody ELSE ISBody THEN
    """
    if len(p) == 4:
        endif = next_endif_label()
        p[0] = ["\tJZ " + endif] + p[2] + [endif + ':']
    else:
        endif = next_endif_label()
        label = next_if_statement_label()
        p[0] = ['\tJZ ' + label] + p[2] + ['\tJUMP ' + endif, label + ':'] + p[4] + ['\tJUMP ' + endif, endif + ':']


def p_ISBody(p):
    """
    ISBody : ISBodyElements
    """
    p[0] = p[1]
    

def p_ISBodyElements(p):
    """
    ISBodyElements : ISBodyElements BodyElement
                   | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]


def next_while_loop_label():
    label = "WHILELOOP" + str(parser.next_while_loop_idx)
    parser.next_while_loop_idx += 1
    return label


def p_WhileLoop(p):
    """
    WhileLoop : BEGIN WLBody UNTIL
    """
    label = next_while_loop_label()
    p[0] = [label + ':'] + p[2] + ['\tJZ ' + label]
    

def p_WLBody(p):
    """
    WLBody : WLBodyElements
    """
    p[0] = p[1]
    

def p_WLBodyElements(p):
    """
    WLBodyElements : WLBodyElements BodyElement
                   | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]


def p_Variable(p):
    """
    Variable : VARIABLE
    """
    
    variable_to_lower = p[1].lower()
    if variable_to_lower in parser.word_to_label:
        label = parser.word_to_label[variable_to_lower]
        parser.words.pop(label)
        parser.word_to_label.pop(variable_to_lower)
    
    parser.variables[variable_to_lower] = parser.next_variable_idx
    parser.next_variable_idx += 1
    
    p[0] = []
    

def p_Store(p):
    """
    Store : STORE
    """
    p[0] = ["\tSWAP", "\tSTORE 0"]


def p_Push(p):
    """
    Push : PUSH
    """
    p[0] = ["\tLOAD 0"]


def p_error(p):
    print("Syntax error in input!", p)
    parser.exito = False
    

"""
TESTING PARSER
"""

parser = yacc.yacc()
parser.exito = True
parser.spaces_idx = 0
parser.reserved_words = {
    "." : [
        "\tWRITEI"
    ],
    "i" : [
        "<<I>>"
    ],
    "swap" : [
        "\tSWAP"
    ],
    "cr" : [
        "\tWRITELN"
    ],
    "emit" : [
        "\tWRITECHR",
    ],
    "key": [
        "\tREAD",
        "\tCHRCODE",
    ],
    "dup": [
        "\tDUP 1"
    ],
    "2dup": [
        "\tPUSHG " + str(DUP2_GP) + " SWAP STORE 0",
        "\tPUSHG " + str(DUP2_GP) + " SWAP STORE 1",
        "\tPUSHG " + str(DUP2_GP) + " LOAD 0",
        "\tPUSHG " + str(DUP2_GP) + " LOAD 1",
        "\tPUSHG " + str(DUP2_GP) + " LOAD 0",
        "\tPUSHG " + str(DUP2_GP) + " LOAD 1",
    ],
    "drop": [
        "\tPOP 1"
    ],
    "spaces": [
        "\tPUSHA SPACES CALL",
        "\nPOP 1"
    ],
    "depth": [
        # depth, SP - FP
    ]
}

parser.words = {}
parser.word_to_label = {}
parser.next_word_label_idx = 0
parser.next_for_loop_idx = 0
parser.next_endloop_idx = 0
parser.if_statement_idx = 0
parser.next_endif_idx = 0
parser.next_while_loop_idx = 0
parser.variables = {}
parser.next_variable_idx = 0
parser.stack_used = False

parser.auxiliary_labels = {
    "spaces": (False, [
        "SPACES:",
        "\tPUSHFP LOAD -1",
        "\tSPACES2:",
        "\t\tPUSHI 32 WRITECHR",
        "\t\tPUSHI 1 SUB DUP 1",
        "\t\tPUSHI 0 EQUAL",
        "\t\tJZ SPACES2",
        "\tPOP 1",
        "\tRETURN",
    ])
}


def replace_words(code):
    for key, value in parser.words.items():
        code = code.replace(key, '\n'.join(value))
    return code


def get_label_value(label):
    match label:
        case "FORLOOP":
            temp = parser.next_for_loop_idx
        case "ENDLOOP":
            temp = parser.next_endloop_idx
        case "IFSTATEMENT":
            temp = parser.if_statement_idx
        case "ENDIF":
            temp = parser.next_endif_idx
        case "WHILELOOP":
            temp = parser.next_while_loop_idx
        case _:
            raise Exception("Unknown label")  
    return temp


def increment_labels(labels, b):
    for key, value in labels.items():
        match key:
            case "FORLOOP":
                parser.next_for_loop_idx = max(parser.next_for_loop_idx, value) + b
            case "ENDLOOP":
                parser.next_endloop_idx = max(parser.next_endloop_idx, value) + b
            case "IFSTATEMENT":
                parser.if_statement_idx = max(parser.if_statement_idx, value) + b
            case "ENDIF":
                parser.next_endif_idx = max(parser.next_endif_idx, value) + b
            case "WHILELOOP":
                parser.next_while_loop_idx = max(parser.next_while_loop_idx, value) + b
            case _:
                raise Exception("Unknown label")


def replace_words(code):
    pattern_word = r'(\<\<(\w+?)(\d+)\>\>)'
    word_usage = defaultdict(int)
    max_labels = defaultdict(int)
    
    while re.search(pattern_word, code):
        
        def replace_word(match):
            nonlocal word_usage
            global parser
            
            word = match.group(1)
            word_code = '\n'.join(parser.words[word])
            
            if word_usage[word] > 0:
                pattern_forloop = r'(FORLOOP|ENDLOOP|IFSTATEMENT|ENDIF|WHILELOOP)(\d+)'
                
                def replace_forloop_label(match2):
                    nonlocal max_labels
                    inc = get_label_value(match2.group(1))  
                    number = int(match2.group(2)) + inc
                    max_labels[match2.group(1)] = max(max_labels[match2.group(1)], number)
                    return match2.group(1) + str(number)
                
                word_code = re.sub(pattern_forloop, replace_forloop_label, word_code)
                increment_labels(max_labels, 1)
            
            word_usage[word] += 1
            return word_code

        code = re.sub(pattern_word, replace_word, code)
    
    return code

def main():
    
    if len(sys.argv) < 2:
        test = sys.stdin.read()
    else:
        test = sys.argv[1]
    
    result = parser.parse(test, debug=DEBUG)

    result_str = ""
    for item in result:
        result_str += item + "\n"
    
    result_str = replace_words(result_str)
    
    for key, value in parser.auxiliary_labels.items():
        if value[0]:
            result_str += '\n' + '\n'.join(value[1])
    
    stack_code = f"""
MYPUSH:
    PUSHG {GP} DUP 1 DUP 2
    LOAD 0 PADD 
    PUSHFP LOAD -1 STORE 1
    LOAD 0 PUSHI 1 ADD STORE 0 
    RETURN

MYPOP:
    PUSHG {GP} DUP 1 
    LOAD 0 PUSHI 1 SUB DUP 1
    PUSHG {GP} SWAP STORE 0
    PADD LOAD 1
    RETURN"""
    
    if parser.stack_used:
        result_str += '\n' + stack_code
    
    pyperclip.copy(result_str)
    
    with open("output.txt", "w") as file:
        file.write(result_str)
        
    print(result_str)


if __name__ == '__main__':
    main()

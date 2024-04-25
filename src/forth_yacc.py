import ply.yacc as yacc
from forth_lex import tokens
from enum import IntEnum
from collections import deque
import sys
from utils import GP, STACK_SIZE
import pyperclip

DEBUG = False

# VM : https://ewvm.epl.di.uminho.pt/

"""
RULES
"""

def p_All(p):
    """
    All : Elements
    """
    
    init_loop_parameters = [
        "\tPUSHG 0 PUSHI 0 STORE 0",
        "\tPUSHG 0 PUSHI 0 STORE 1",
        "\tPUSHG 0 PUSHI 0 STORE 2"
    ]
    
    start = ['ALLOC 3'] + ['ALLOC ' + str(STACK_SIZE + 1) + '\n'] + ['START']
    start += ['\tPUSHG ' + str(GP) + ' PUSHI 1 STORE 0']
    start += init_loop_parameters
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
            | String
            | Arithmetic
            | Comparison
            | Integer
            | Float
            | IfStatement
            | WhileLoop
            | ForLoop
            | Word
    """
    p[0] = p[1]
    

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
        p[0] = parser.reserved_words[p1_to_lower]
    else:
        label = parser.word_to_label.get(p1_to_lower, None)
        if label and label in parser.words:
            p[0] = ['\tPUSHA ' + label, '\tCALL']
        else:
            raise Exception("Word not found in dictionary: " + p[1])
    
    
def p_Integer(p):
    """
    Integer : INTEGER
    """
    p[0] = "\tPUSHI " + str(p[1]) + " PUSHA MYPUSH CALL POP 1"
    

def p_Float(p):
    """
    Float : FLOAT
    """
    p[0] = "\tPUSHF " + str(p[1]) +  "PUSHA MYPUSH CALL POP 1"
    

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
    
    p[0] = ["\tPUSHA MYPOP CALL", "\tPUSHA MYPOP CALL", "\tSWAP", temp, "\tPUSHA MYPUSH CALL POP 1"]
        

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
    
    p[0] = ["\tPUSHA MYPOP CALL", "\tPUSHA MYPOP CALL", "\tSWAP", temp, "\tPUSHA MYPUSH CALL POP 1"]


def get_next_word_label():
    parser.next_word_label = "word" + str(len(parser.words))
    return parser.next_word_label


def p_WordDefinition(p):
    """
    WordDefinition : COLON WORD WordBody SEMICOLON
    """
    p2_to_lower = p[2].lower()
    if p2_to_lower not in parser.reserved_words:
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
                | String
                | Arithmetic
                | Comparison
                | Float
                | IfStatement
                | ForLoop
                | WhileLoop
                | Word
    """
    p[0] = p[1]    

    
def next_for_loop_label():
    label = "FORLOOP" + str(parser.next_for_loop_idx)
    parser.next_for_loop_idx += 1
    return label


def p_ForLoop(p):
    """
    ForLoop : DO FLBody LOOP
    """
    
    for_loop_label = next_for_loop_label()
    
    init = [
        # load struct values
        "\tPUSHG 0",
        "\tLOAD 0",
        "\tPUSHG 0",
        "\tLOAD 1",
        "\tPUSHG 0",
        "\tLOAD 2",
        
        # pop idx and limit
        "\tPUSHA MYPOP CALL",
        "\tPUSHA MYPOP CALL",
        "\tSWAP",
        
        #  store idx
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 0",
        
        # store limit
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 1",
        
        # iteration
        "\tPUSHG 0",
        "\tPUSHI 0",
        "\tSTORE 2",
        
        # call loop
        "\tPUSHA " + for_loop_label, 
        "\tCALL", 
        
        # restore struct values
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 2",
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 1",
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 0",
    ]
    
    for_loop = [
        '\tPUSHG 0',
        '\tLOAD 0',
        '\tPUSHG 0',
        '\tLOAD 1',
        '\tINF',
        '\tJZ ' + 'ENDLOOP',
        
        '\tPUSHG 0',
        '\tLOAD 0',
        '\tPUSHI 1',
        '\tADD',
        '\tPUSHG 0',
        '\tSWAP',
        '\tSTORE 0',
        
        '\tPUSHG 0',
        '\tLOAD 2',
        '\tPUSHI 1',
        '\tADD',
        '\tPUSHG 0',
        '\tSWAP',
        '\tSTORE 2',
    ]
    
    for index, value in enumerate(p[2]):
        if value == "I":
            for_loop += [
                '\tPUSHG 0',
                '\tLOAD 0 PUSHI 1 SUB',
                '\tPUSHA MYPUSH CALL POP 1',
            ]
        else:
            for_loop += [value]
            
    for_loop += ['\tJUMP ' + for_loop_label]
    parser.for_loops[for_loop_label] = for_loop  
    
    p[0] = init
    

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


def p_IfStatement(p):
    """
    IfStatement : IF ISBody THEN
                | IF ISBody ELSE ISBody THEN
    """
    if len(p) == 4:
        label = next_if_statement_label()
        p[0] = ["\tPUSHA " + label + " CALL"]
        parser.if_statements[label] = ["\tPUSHA MYPOP CALL", "\tJZ EMPTYELSE"] + p[2]
    else:
        label1 = next_if_statement_label()
        p[0] = ["\tPUSHA " + label1 + " CALL"]
        label2 = next_if_statement_label()
        parser.if_statements[label1] = ["\tPUSHA MYPOP CALL", "\tJZ " + label2] + p[2]
        parser.if_statements[label2] = p[4]


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
    parser.while_loops[label] = p[2] + ["PUSHA MYPOP CALL", "\tJZ " + label]
    
    p[0] = ['\tPUSHA ' + label, '\tCALL']
    

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
    

def p_error(p):
    print("Syntax error in input!", p)
    parser.exito = False


"""
TESTING PARSER
"""

parser = yacc.yacc()
parser.exito = True
parser.reserved_words = {
    "." : ["\tPUSHA MYPOP CALL", "\tWRITEI"],
    "i" : ["I"],
    "swap" : [
        "\tPUSHA MYPOP CALL", 
        "\tPUSHA MYPOP CALL", 
        "\tSWAP", 
        "\tPUSHA MYPUSH CALL POP 1",
        "\tPUSHA MYPUSH CALL POP 1",
        ],
    "cr" : ["\tWRITELN"],
    "emit" : [
        "\tPUSHA MYPOP CALL",
        "\tWRITECHR",
    ],
    "dup": [
        "\tPUSHA MYPOP CALL",
        "\tDUP 1",
        "\tPUSHA MYPUSH CALL POP 1",
        "\tPUSHA MYPUSH CALL POP 1"
    ],
    "2dup": [
        "\tPUSHA MYPOP CALL",
        "\tPUSHA MYPOP CALL",
        "\tPUSHA INCPOINTER CALL",
        "\tPUSHA INCPOINTER CALL",
        "\tPUSHA MYPUSH CALL POP 1",
        "\tPUSHA MYPUSH CALL POP 1",
    ],
    "drop": [
        "\tPUSHA DECPOINTER CALL",
    ],
    "depth": [
        f"\tPUSHG {GP} LOAD 0",
        "\tPUSHI 1",
        "\tSUB",
        "\tPUSHA MYPUSH CALL POP 1"
    ]
}
parser.words = {}
parser.for_loops = { "ENDLOOP": [] }
parser.word_to_label = {}
parser.next_word_label = "word0"
parser.next_for_loop_idx = 0
parser.if_statements = { "EMPTYELSE": [] }
parser.if_statement_idx = 0
parser.next_while_loop_idx = 0
parser.while_loops = {}


def dict_to_str(dict):
    result = ""
    for key, value in dict.items():
        result += key + ":\n"
        for item in value:
            result += item + "\n"
        result += "\tRETURN\n\n"
    return result


def main():
    
    if len(sys.argv) < 2:
        print("Usage: python3 forth_yacc.py <code>")
        sys.exit(1)
        
    test = sys.argv[1]
    result = parser.parse(test, debug=DEBUG)

    result_str = ""
    for item in result:
        result_str += item + "\n"
    
    result_str += "\n"

    dicts = [parser.words, parser.for_loops, parser.if_statements, parser.while_loops]
    for d in dicts:
        result_str += dict_to_str(d)
            
    with open("vm_stack_code.txt", "r") as file:
        contents = file.read()
    
    result_str += '\n' + contents
    pyperclip.copy(result_str)
    
    with open("output.txt", "w") as file:
        file.write(result_str)


if __name__ == '__main__':
    main()

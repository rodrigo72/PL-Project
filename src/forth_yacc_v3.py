import ply.yacc as yacc
from forth_lex_v2 import tokens
from enum import IntEnum
from collections import deque
import pyperclip

# VM : https://ewvm.epl.di.uminho.pt/

from utils import GP, STACK_SIZE, MAX_NESTED_FOR_LOOPS

"""
RULES
"""


def p_All(p):
    """
    All : Elements
    """
    start = ['ALLOC 3'] * MAX_NESTED_FOR_LOOPS + ['ALLOC ' + str(STACK_SIZE + 1) + '\n'] + ['START']
    start += ['\tPUSHG ' + str(GP) + ' PUSHI 1 STORE 0']
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
            | ForLoop
            | Word
    """
    parser.current_for_loop_idx = MAX_NESTED_FOR_LOOPS
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
    elif p[1] == "%":
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
    WordBodyElements : WordBodyElements WordBodyElement
                     | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
        
        
def p_WordBodyElement(p):
    """
    WordBodyElement : Integer
                    | String
                    | Arithmetic
                    | Comparison
                    | Float
                    | IfStatement
                    | ForLoop
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
    
    for_loop_number = MAX_NESTED_FOR_LOOPS - parser.current_for_loop_idx
    for_loop_label = next_for_loop_label()
    
    init = [
        "\tPUSHA MYPOP CALL",
        "\tPUSHA MYPOP CALL",
        "\tSWAP",
        "\tPUSHG " + str(for_loop_number),
        "\tSWAP",
        "\tSTORE 0",
        "\tPUSHG " + str(for_loop_number),
        "\tSWAP",
        "\tSTORE 1",
        "\tPUSHG " + str(for_loop_number),
        "\tPUSHI 0",
        "\tSTORE 2",
        "\tPUSHA " + for_loop_label, 
        "\tCALL", 
    ]
    
    for_loop = [
        '\tPUSHG ' + str(for_loop_number),
        '\tLOAD 0',
        '\tPUSHG ' + str(for_loop_number),
        '\tLOAD 1',
        '\tINF',
        '\tJZ ' + 'ENDLOOP',
        
        '\tPUSHG ' + str(for_loop_number),
        '\tLOAD 0',
        '\tPUSHI 1',
        '\tADD',
        '\tPUSHG ' + str(for_loop_number),
        '\tSWAP',
        '\tSTORE 0',
        
        '\tPUSHG ' + str(for_loop_number),
        '\tLOAD 2',
        '\tPUSHI 1',
        '\tADD',
        '\tPUSHG ' + str(for_loop_number),
        '\tSWAP',
        '\tSTORE 2',
    ]
    
    for index, value in enumerate(p[2]):
        if value == "I":
            for_loop += [
                '\tPUSHG ' + str(for_loop_number),
                '\tLOAD 0 PUSHI 1 SUB',
                '\tPUSHA MYPUSH CALL POP 1',
            ]
        else:
            for_loop += [value]
            
    for_loop += ['\tJUMP ' + for_loop_label]
    parser.for_loops[for_loop_label] = for_loop  
    parser.current_for_loop_idx -= 1
    
    p[0] = init
    

def p_FLBody(p):
    """
    FLBody : FLBodyElements
    """
    p[0] = p[1]
    

def p_FLBodyElements(p):
    """
    FLBodyElements : FLBodyElements FLBodyElement
                   | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
            

def p_FLBodyElement(p):
    """
    FLBodyElement : Arithmetic
                  | String
                  | Comparison
                  | Integer
                  | Float
                  | IfStatement
                  | ForLoop
                  | Word
    """
    p[0] = p[1]
    

  
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
    ISBodyElements : ISBodyElements ISBodyElement
                   | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + [p[2]]
            

def p_ISBodyElement(p):
    """
    ISBodyElement : Integer
                  | String
                  | Float
                  | Arithmetic
                  | Comparison
                  | IfStatement
                  | ForLoop
                  | Word
    """
    p[0] = p[1]
    

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
    "drop": [
        "\tPUSHA DECPOINTER CALL",
    ],
}
parser.words = {}
parser.for_loops = { "ENDLOOP": [] }
parser.word_to_label = {}
parser.next_word_label = "word0"
parser.current_for_loop_idx = MAX_NESTED_FOR_LOOPS
parser.next_for_loop_idx = 0
parser.if_statements = { "EMPTYELSE": [] }
parser.if_statement_idx = 0


def main():
    test = """
    : test0 1 1 + ;
    : test 1 3 - test0 ;
    1 2 +
    10 test
    """
    
    test2 = """
    10 7 DO 1 . 3 0 DO 2 . 2 0 DO 3 . LOOP LOOP LOOP
    10 7 DO 7 . LOOP
    """
    
    test3 = """
    10 4 DO 1 . 4 0 DO 2 . LOOP LOOP
    10 7 DO 7 . LOOP
    """
    
    medo_panico_terror_for_loop_test = """
    2 0 DO 1 . 2 0 DO 2 . 2 0 DO 3 . LOOP 2 0 DO 4 . LOOP LOOP LOOP
    """
    
    result_str = ""
    
    test_somatorio = """
    : somatorio 0 swap 1 do i + loop ;
    11 somatorio .
    """
    
    test4 = """
    : my-loop 10 0 do i + loop ;
    11 my-loop .
    """
    
    test5 = """
    : sim2 2 + ;
    : sim 1 + sim2 ;
    1 sim .
    """
    
    test_string = """
    ." hello my friend"
    cr
    ." hello again"
    cr 97 emit
    """
    
    test_string_2 = """
    : tofu ." Yummy bean curd!" ;
    : sprouts ." Miniature vegetables." ;
    : menu CR tofu CR sprouts CR ;
    menu
    """
    
    test_ifstatement = """
    : ?FULL 12 = IF 391 .  THEN ;
    12 ?FULL
    """
    
    test_comparisons = """
    1 2 < .
    2 3 = .
    """
    
    test_ifelse = """
    : ?DAY  32 < IF  ." Looks good " ELSE  ." no way " THEN ;
    33 ?DAY
    """
    
    test_nested_ifelse = """
    : EGGSIZE ( n -- )
            DUP 18 < IF  ." reject "      ELSE
            DUP 21 < IF  ." small "       ELSE
            DUP 24 < IF  ." medium "      ELSE
            DUP 27 < IF  ." large "       ELSE
            DUP 30 < IF  ." extra large " ELSE
                ." error "
            THEN THEN THEN THEN THEN DROP ;
    23 EGGSIZE
    """
    
    dup_test = """
    1 dup . .
    """
    
    debug = False
    result = parser.parse(test_string_2, debug=debug)
    
    print("\n-------------- EWVM code --------------\n")

    for item in result:
        result_str += item + "\n"
    
    result_str += "\n"
        
    for word_label, word in parser.words.items():
        result_str += word_label + ":\n"
        for item in word:
            result_str += item + "\n"
        result_str += "\tRETURN\n\n"
        
    result_str += "\n"
        
    for for_loop_label, for_loop in parser.for_loops.items():
        result_str += for_loop_label + ":\n"
        for item in for_loop:
            result_str += item + "\n"
        result_str += "\tRETURN\n\n"
    
    for if_label, if_body in parser.if_statements.items():
        result_str += if_label + ":\n"
        for item in if_body:
            result_str += item + "\n"
        result_str += "\tRETURN\n\n"
        
    print(result_str)
    
    with open("vm_stack_code.txt", "r") as file:
        contents = file.read()
    
    result_str += '\n' + contents
    pyperclip.copy(result_str)
        
    print("-----------------------------------------\n")
    

if __name__ == '__main__':
    main()


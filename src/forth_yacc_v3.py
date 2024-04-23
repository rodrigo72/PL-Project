import ply.yacc as yacc
from forth_lex_v2 import tokens
from enum import IntEnum
from collections import deque
import pyperclip

# VM : https://ewvm.epl.di.uminho.pt/

"""
RULES
"""

class StoredWordType(IntEnum):
    ARRAY = 0


class Word:
    def __init__(self, type, word):
        self.type = type
        self.word = word


def p_All(p):
    """
    All : Elements
    """
    start = [
        "ALLOC 3",  # for loop parameters
        "START"
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
            | Arithmetic
            | Integer
            | Float
            | ForLoop
            | Word
    """
    # parser.global_pointer_state_stack.append(parser.global_pointer)
    p[0] = p[1]
    
    
def p_Word(p):
    """
    Word : WORD
    """
    
    if p[1] in parser.reserved_words:
        p[0] = parser.reserved_words[p[1]].word
    else:
        label = parser.word_to_label.get(p[1], None)
        if label and label in parser.words:
            stored_word = parser.words[label]
            if stored_word.type == StoredWordType.ARRAY:
                p[0] = ['\tPUSHA ' + label, '\tCALL']
            if stored_word.update_pointer:
                stored_word.update_pointer()
            parser.used_words.add(label)
        else:
            raise Exception("Word not found in dictionary: " + p[1])
    
    
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
    
    if p[1] == "+":
        p[0] = "\tADD"
    elif p[1] == "-":
        p[0] = "\tSUB"
    elif p[1] == "*":
        p[0] = "\tMUL"
    elif p[1] == "/":
        p[0] = "\tDIV"
    elif p[1] == "%":
        p[0] = "\tMOD"
    else: 
        raise Exception("Unknown arithmetic operator")
        

def get_next_word_label():
    parser.next_word_label = "word" + str(len(parser.used_words))
    return parser.next_word_label


def p_WordDefinition(p):
    """
    WordDefinition : COLON WORD WordBody SEMICOLON
    """
    if p[2] not in parser.reserved_words:
        word_label = get_next_word_label()
        parser.word_to_label[p[2]] = word_label
        parser.words[word_label] = Word(StoredWordType.ARRAY, p[3])
    else:
        raise Exception("Word already defined")
        
    p[0] = ["\tNOP"]  # does nothing
    

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
                    | Arithmetic
                    | Float
                    | Word
    """
    p[0] = p[1]
    

def p_ForLoop(p):
    """
    ForLoop : DO FLBody LOOP
    """
    
    for_loop_number = len(parser.for_loops)
    for_loop_label = "FORLOOP" + str(for_loop_number)
    
    init = [
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 0",
        "\tPUSHG 0",
        "\tSWAP",
        "\tSTORE 1",
        "\tPUSHG 0",
        "\tPUSHI 0",
        "\tSTORE 2",
        "\tPUSHA " + for_loop_label, 
        "\tCALL", 
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
                  | Integer
                  | Float
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
    "." : Word(StoredWordType.ARRAY, ["\tWRITEI"]),
    "i" : Word(StoredWordType.ARRAY, [
            "\tPUSHG 0",
            "\tLOAD 2"
        ]),
}
parser.used_words = set()
parser.words = {}
parser.for_loops = { "ENDLOOP": [] }
parser.word_to_label = {}
parser.next_word_label = "word0"


def main():
    test = """
    : test0 1 1 + ;
    : test 1 3 - test0 ;
    1 2 +
    test
    """
    
    test2 = """
    10 4 DO i . LOOP
    """
    
    result_str = ""
    
    debug = False
    result = parser.parse(test2, debug=debug)
    
    print("\n-------------- EWVM code --------------\n")

    for item in result:
        result_str += item + "\n"
    
    result_str += "\n"
        
    for label in parser.used_words:
        result_str += label + ":\n"
        for item in parser.words[label].word:
            result_str += item + "\n"
        result_str += "\tRETURN\n\n"
        
    result_str += "\n"
        
    for for_loop_label, for_loop in parser.for_loops.items():
        result_str += for_loop_label + ":\n"
        for item in for_loop:
            result_str += item + "\n"
        result_str += "\tRETURN\n\n"
        
        
    print(result_str)
    pyperclip.copy(result_str)
        
    print("-----------------------------------------\n")
    

if __name__ == '__main__':
    main()

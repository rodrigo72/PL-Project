import ply.yacc as yacc
from forth_lex import tokens

# VM : https://ewvm.epl.di.uminho.pt/
"""
 GRAMMAR
---------

Elements : Elements Element
         | &
         
Element : WordDefinition
        | Word
        | Integer
        | Float
        | Arithmetic
              
WordDefinition : COLON WORD WordBody SEMICOLON

WordBody : WordBodyElements

WordBodyElements : WordBodyElements WordBodyElement
                 | &
                 
WordBodyElement : WORD
                | Integer
                | Float
                | Arithmetic

Word : WORD
Integer : INTEGER
Float : FLOAT
Arithmetic : ARITHMETIC
"""

"""
RULES
"""

def p_Elements(p):
    """
    Elements : Elements Element
             | 
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]
    return p[0]
        

def p_Element(p):
    """
    Element : WordDefinition
            | Word
            | Arithmetic
            | Integer
            | Float
    """
    p[0] = p[1]
    
    
def p_Word(p):
    """
    Word : WORD
    """
    if p[1] in parser.words:
        p[0] = parser.words[p[1]]
    else:
        parser.exito = False
    
def p_Integer(p):
    """
    Integer : INTEGER
    """
    p[0] = "PUSHI " + str(p[1])
    

def p_Float(p):
    """
    Float : FLOAT
    """
    p[0] = "PUSHF " + str(p[1])
    

def p_Arithmetic(p):
    """
    Arithmetic : ARITHMETIC
    """
    if p[1] == "+":
        p[0] = "ADD"
    elif p[1] == "-":
        p[0] = "SUB"
    elif p[1] == "*":
        p[0] = "MUL"
    elif p[1] == "/":
        p[0] = "DIV"
    elif p[1] == "%":
        p[0] = "MOD"
    

def p_WordDefinition(p):
    """
    WordDefinition : COLON WORD WordBody SEMICOLON
    """
    parser.words[p[2]] = p[3]
    return None
    

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
        p[0] = p[1] + [p[2]]
        
        
def p_WordBodyElement(p):
    """
    WordBodyElement : WORD
                    | Arithmetic
                    | Integer
                    | Float
    """
    p[0] = p[1]

def p_error(p):
    print("Syntax error in input!")
    parser.exito = False


"""
TESTING PARSER
"""
parser = yacc.yacc()
parser.exito = True
parser.words = {}


def main():
    test = """
    : test 1 3 word ;
    1 2 +
    test
    """
    result = parser.parse(test)
    result = [item for item in result if item is not None]
    for item in result:
        print(item)
    

if __name__ == '__main__':
    main()

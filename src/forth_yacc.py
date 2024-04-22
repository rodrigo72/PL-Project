import ply.yacc as yacc
from forth_lex import tokens

# VM : https://ewvm.epl.di.uminho.pt/
"""
 GRAMMAR
---------

Elements : Elements Element
         | &
         
Element : WordDefinition
        | WORD
        | INTEGER
        | FLOAT
      
Word : WORD
        
WordDefinition : COLON WordBody SEMICOLON

WordBody : WordBodyElements

WordBodyElements : WordBodyElements WordBodyElement
                 | &
                 
WordBodyElement : WORD
                | INTEGER
                | FLOAT
"""

"""
RULES
"""

# rules here


"""
TESTING PARSER
"""
parser = yacc.yacc()


def main():
    test = """
    : test 1 3 + ;
    1 2 +
    test
    """
    result = parser.parse(test)
    print(result)
    

if __name__ == '__main__':
    main()

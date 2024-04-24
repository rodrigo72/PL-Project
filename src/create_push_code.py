import pyperclip

STACK_SIZE = 20
GP = 4


def main():
    increment_pointer = """INCPOINTER:\n\tPUSHG {} DUP 1 LOAD 0 PUSHI 1 ADD STORE 0 RETURN\n""".format(GP)
    decrement_pointer = """DECPOINTER:\n\tPUSHG {} DUP 1 LOAD 0 PUSHI 1 SUB STORE 0 RETURN\n""".format(GP)
    push_aux = """MYPUSHAUX:\n\tPUSHG {} PUSHFP LOAD -1 RETURN\n""".format(GP)
    
    ifstatement_init_push = """\tPUSHG {} LOAD 0 PUSHI {} EQUAL NOT JZ MYPUSH{}"""
    ifstatement_init_pop  = """\tPUSHG {} LOAD 0 PUSHI {} EQUAL NOT JZ MYPOP{}"""

    ifstatement_body_push = """PUSHA MYPUSHAUX CALL STORE {} JUMP INCPOINTER"""
    ifstatement_body_pop = """PUSHG {} LOAD {} jump DECPOINTER"""
    
    result = increment_pointer + '\n' + decrement_pointer + '\n' + push_aux + '\n'
    
    # PUSH -------------------------------------
    
    result += "MYPUSH:\n"
    for i in range(1, STACK_SIZE + 1):
        result += ifstatement_init_push.format(GP, i, i) + '\n'
    result += "\tERR \"STACK IS FULL\"\n\n"
    
    
    for i in range(1, STACK_SIZE + 1):
        result += f"MYPUSH{i}: "
        result += ifstatement_body_push.format(i) + '\n'
    result += "\n"
    
    # POP -------------------------------------

    result += "MYPOP:\n"
    for i in range(2, STACK_SIZE + 1):
        result += ifstatement_init_pop.format(GP, i, i - 1) + '\n'
    result += "\tERR \"STACK IS EMPTY\"\n\n"

    for i in range(1, STACK_SIZE + 1):
        result += f"MYPOP{i}: "
        result += ifstatement_body_pop.format(GP, i) + '\n'

    #     -------------------------------------
    
    print(result)
    pyperclip.copy(result)
    
    with open('vm_stack_code.txt', 'w') as file:
            file.write(result)

if __name__ == "__main__":
    main()

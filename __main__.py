import fileinput
from interpret import Interpreter
from callbacks import DefualtCallbacks

def preprocess_string_literals(program):
    output = ''

    buffer_txt = ''

    in_string = False
    invert = False
    for char in list(program):
        if char == 'i' and not in_string:
            invert = True
        elif char == '"':
            if in_string:
                in_string = False
                if invert:
                    buffer_txt = buffer_txt[::-1]

                output += ''.join([str(ord(char))+'_' for char in list(buffer_txt)])
            else:
                in_string = True
                buffer_txt = ''
            continue
        elif not in_string:
            invert = False

        if in_string:
            buffer_txt += char
        else:
            output += char

    return output

program = ''.join([line for line in fileinput.input()])

program = preprocess_string_literals(program)

print(program)

Interpreter(program, DefualtCallbacks).run()

print()

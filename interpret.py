import time
import sys

def add_to_chain(cls):
    def consume(chars_):
        accepted_chars = ''

        chars = chars_[:]

        if getattr(cls, 'greedy', False):
            for char in chars_:
                if len(chars) < 1:
                    break

                if char in cls.accepts:
                    accepted_chars += char
                    chars = chars[1:]
                else:
                    break
        else:
            if chars[0] in cls.accepts:
                accepted_chars += chars[0]
                chars = chars[1:]

        if accepted_chars != '':
            instance = cls(accepted_chars, idx=-len(chars_))
        else:
            instance = None

        return chars, instance

    cls.consume = staticmethod(consume)

    Chain.add_link(cls)

    return cls

class Chain(object):
    chain = []

    @classmethod
    def process(cls, program):
        cls.add_link(NOP)

        return list(cls.consume(program))

    @classmethod
    def consume(cls, program):
        while len(program) > 0:
            for link in cls.chain:
                program, char_instance = link.consume(program)

                if char_instance is not None:
                    yield char_instance
                    break

                if len(program) < 1:
                    break

    @classmethod
    def add_link(cls, link_cls):
        cls.chain.append(link_cls)

class Interpreter(object):
    def __init__(self, program, callbacks):
        self.ip = 0

        self.register = 0

        self.active_stack = 0
        self.stacks = [[0], [0]]

        self.program = program
        self.chars = Chain.process(program)

        # print(''.join([str(char) for char in self.chars]))

        self.callbacks = callbacks


    def run(self):
        while self.ip < len(self.chars):
            self.accept(self.chars[self.ip])
            self.ip += 1

    def accept(self, visitor):
        visitor.visit(self)

    def push(self, value):
        self.stacks[self.active_stack].append(value)

    def pop(self):
        if len(self.stacks[self.active_stack]) > 0:
            return self.stacks[self.active_stack].pop()
        else:
            return 0

    def switch_active_stack(self):
        if self.active_stack == 1:
            self.active_stack = 0
        else:
            self.active_stack = 1

    def set_register(self, value):
        self.register = value

    def get_register(self):
        return self.register

    def terminate(self):
        sys.exit(0)

class Char(object):
    def __init__(self, literal, idx):
        self.literal = literal
        self.idx = idx

    def __str__(self):
        return self.literal

@add_to_chain
class NumberLiteral(Char):
    accepts = '0123456789'
    greedy = True

    def visit(self, state):
        value = int(self.literal)
        state.push(value)

@add_to_chain
class Brace(Char):
    accepts = '()[]{}'

    opening_braces = '([{'

    paired_brace_lookup = {
        '(': ')',
        '[': ']',
        '{': '}',

        ')': '(',
        ']': '[',
        '}': '{',
    }

    def visit(self, state):
        direction = 1 if self.literal in self.opening_braces else -1

        paired_brace = self.paired_brace_lookup[self.literal]

        depth = 0
        char = ''
        while not (depth == 0 and char == paired_brace):
            char = str(state.chars[state.ip])
            if char == paired_brace:
                depth -= 1
            elif char == self.literal:
                depth += 1

            state.ip += direction
            # print(self.literal, state.ip, char, depth)

        state.ip -= direction # so that we don't skip extra chars


@add_to_chain
class Push(Char):
    accepts = '^'

    def visit(self, state):
        value = state.get_register()
        state.push(value)

@add_to_chain
class Pop(Char):
    accepts = 'v'

    def visit(self, state):
        value = state.pop()
        state.set_register(value)

@add_to_chain
class Duplicate(Char):
    accepts = ':'

    def visit(self, state):
        value = state.pop()
        state.push(value)
        state.push(value)

@add_to_chain
class Swap(Char):
    accepts = '\\'

    def visit(self, state):
        x = state.pop()
        y = state.pop()
        state.push(x)
        state.push(y)

@add_to_chain
class Discard(Char):
    accepts = '$'

    def visit(self, state):
        state.pop()

@add_to_chain
class SwitchActiveStack(Char):
    accepts = '~'

    def visit(self, state):
        state.switch_active_stack()

@add_to_chain
class PrintInt(Char):
    accepts = '.'

    def visit(self, state):
        value = str(state.pop())
        state.callbacks.on_output(value, is_number=True)

@add_to_chain
class PrintChar(Char):
    accepts = ','

    def visit(self, state):
        value = chr(state.pop())
        state.callbacks.on_output(value)

@add_to_chain
class GetInt(Char):
    accepts = '#'

    def visit(self, state):
        value = int(state.callbacks.get_input())
        state.push(value)

@add_to_chain
class GetKey(Char):
    accepts = 'k'

    def visit(self, state):
        value = int(state.callbacks.get_keypress())
        state.push(value)

@add_to_chain
class Delimit(Char):
    accepts = '_'

    def visit(self, state):
        pass

@add_to_chain
class ConditionalSkip(Char):
    accepts = '?'

    def visit(self, state):
        value = state.pop()

        if value > 0:
            state.ip += 1 # an extra step to skip the next char

@add_to_chain
class Skip(Char):
    accepts = ';'

    def visit(self, state):
        state.ip += 1 # an extra step to skip the next char

@add_to_chain
class Wait(Char):
    accepts = 'w'

    def visit(self, state):
        time.sleep(0.001)

@add_to_chain
class Terminate(Char):
    accepts = '&'

    def visit(self, state):
        state.terminate()

@add_to_chain
class Arithmetic(Char):
    accepts = '+-*/%!|<>='

    calc_lookup = {
        '+': (lambda x, y: x+y),
        '-': (lambda x, y: x-y),
        '*': (lambda x, y: x*y),
        '/': (lambda x, y: x/y),
        '%': (lambda x, y: x%y),
        '|': (lambda x, y: x or y),
        '<': (lambda x, y: x < y),
        '>': (lambda x, y: x > y),
        '=': (lambda x, y: x == y),
    }

    def visit(self, state):
        if self.literal == '!':
            value = state.pop()
            state.push(0 if value > 0 else 1)
        else:
            y = state.pop()
            x = state.pop()
            value = int(self.calc_lookup[self.literal](x, y))
            state.push(value)

# last resort class
class NOP(Char):
    @classmethod
    def visit(cls, state):
        pass

    @classmethod
    def consume(cls, chars):
        return chars[1:], None

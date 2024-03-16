import re
import math
import operator as op

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below) 


def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens."
    # regex: 
    tre = re.compile(r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:[\\].|[^\\"])*"?|;.*|[^\s\[\]{}()'"`@,;]+)""");
    # tre = re.compile(r"""(\\(|\\)|\"[^\"]*\"|;.*|[^[:space:]()]+)""");
    return [t for t in re.findall(tre, chars) if t[0] != ';']


def parse(tokens: list) -> Exp:
    "Parse a token list into an ast" 
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(parse(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError('unexpected \')\'')
    elif token == '"':
        L = []
        while tokens[0] != '"':
            L.append(parse(tokens))
        tokens.pop(0)
        return L
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)
    


def std_env() -> Env:
    env = Env()
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '<': op.gt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        '>': op.le,
        'abs': abs,
        'append': op.add,
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car': lambda *x: x[0],
        'cdr': lambda *x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'expt': pow,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: List(x),
        'list?': lambda x: isinstance(x, List),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'print': print,
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = std_env()

def eval(x: Exp, env=global_env) -> Exp:
    if isinstance(x, Symbol):
        if x[0] == '"':
            return x[1:-1]
        else:
            return env[x]
    elif isinstance(x, Number):
        return x
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test,env) else alt)
        return eval(exp, alt)
    elif x[0] == 'define':
        (_, symbol, exp) = x
        env[symbol] = eval(exp,symbol)
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

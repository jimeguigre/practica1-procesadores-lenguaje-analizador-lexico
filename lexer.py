# reconocer los elementos del lenguaje a nivel léxico

# importar PLY lex
import ply.lex as lex

# cargar fichero con los datos de ejemplo
import sys

# definición de palabras reservadas
reserved = {
    'true': 'TRUE', 
    'false': 'FALSE',
    'int': 'INT', 
    'float': 'FLOAT', 
    'char': 'CHAR',
    'boolean': 'BOOLEAN', 
    'void': 'VOID', 
    'return': 'RETURN',
    'if': 'IF', 
    'else': 'ELSE', 
    'do': 'DO', 
    'while': 'WHILE',
    'print':'PRINT',
    'new':'NEW',
    'record': 'RECORD', 
}

# definición de tokens
tokens = [
    'ID',
    'INT_VALUE', 
    'FLOAT_VALUE', 
    'CHAR_VALUE',
    'BIN_VALUE',
    'OCT_VALUE',
    'HEX_VALUE',
    'EQUALS', 
    'PUNTO_COMA', 
    'L_BRACKET',
    'R_BRACKET', 
    'L_PAREN', 
    'R_PAREN',
    'MAYOR_IGUAL',
    'MENOR_IGUAL',
    'MENOR',
    'MAYOR',
    'ASIGNACION', 
    'MUL',
    'RESTA',
    'SUMA', 
    'AND',
    'OR',
    'NOT',
    'COMMENT',
] + list(reserved.values())

# declaración de formatos
t_EQUALS = r'=='

t_PUNTO_COMA = r';'

t_L_BRACKET = r'\{'

t_R_BRACKET = r'\}'

t_L_PAREN =r'\('

t_R_PAREN = r'\)'

t_MAYOR_IGUAL = r'>='

t_MENOR_IGUAL = r'<='

t_MAYOR = r'>'

t_MENOR = r'<'

t_ASIGNACION = r'='

t_MUL = r'\*'

t_RESTA = r'-'

t_SUMA = r'\+'

t_NOT = r'!'

t_AND = r'&&'

t_OR = r'\|\|'

def t_COMMENT(t):
    r'//.* | /\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_CHAR_VALUE(token): #solo 1 caracter 
    r'\'.\''
    return token

# strings también? r='\'([a-zA-Z0-9_]*(\s)?)\''

def t_ID(token):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    token.type = reserved.get(token.value, 'ID')
    return token

def t_HEX_VALUE(token):
    r'0x[0-9A-F]+'
    # conversor a decimal
    token.value = int(token.value, 16)
    return token

def t_BIN_VALUE(token):
    r'0b[01]+'
    # conversor a decimal
    token.value = int(token.value, 2)
    return token

def t_OCT_VALUE(token):
    r'0[0-7]+'
    # conversor a decimal
    token.value = int(token.value, 8)
    return token

def t_FLOAT_VALUE(token):
   r'((0|[1-9][0-9]*)\.[0-9]+([eE][-+]?[0-9]+)? | (0|[1-9][0-9]*)[eE][-+]?[0-9]+)'
   token.value = float(token.value)
   return token

def t_INT_VALUE(token):
    r'[1-9][0-9]*|0'
    token.value = int(token.value)
    return token


# caracteres especiales
def t_NEWLINE(token):
    r'\n+'
    token.lexer.lineno += token.value.count('\n')

t_ignore = ' \t' # caracteres a ignorar de manera automática

def t_error(token): #caracteres no reconocidos
    print(f'illegal character at {token.lineno}, {token.lexpos}')
    token.lexer.skip(1) # recuperarse del error (se salta el caracter del error)


def find_column(input_data, token):
    line_start = input_data.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) 



# construir el lexer
lexer = lex.lex()

# cargar el fichero y generar el archivo de salida
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        data = f.read()
        lexer.input(data)
        for tok in lexer:
            col_start = find_column(data, tok)
            col_end = col_start + len(str(tok.value))
            print(f"{{ {tok.type}, {tok.value}, {tok.lineno}, {col_start}, {col_end} }}")
# Este archivo contiene un lexer para reconocer los elementos del lenguaje a nivel léxico

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
    'break': 'BREAK',
}

# definición de tokens
tokens = [
    'ID',
    'INT_VALUE', 
    'FLOAT_VALUE', 
    'CHAR_VALUE',
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
    'DIV',
    'RESTA',
    'SUMA', 
    'AND',
    'OR',
    'NOT',
    'COMMENT',
    'PUNTO',
    'COMA',
] + list(reserved.values())

# declaración de formatos
def t_COMMENT(t):
    r'//.*|/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_PUNTO_COMA(token):
    r';'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_L_BRACKET(token):
    r'\{'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_R_BRACKET(token):
    r'\}'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_L_PAREN(token):
    r'\('
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_R_PAREN(token): 
    r'\)'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_MAYOR_IGUAL(token):
    r'>='
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_MENOR_IGUAL(token):
    r'<='
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_MAYOR(token):
    r'>'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_MENOR(token):
    r'<'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_EQUALS(token):
    r'=='
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_ASIGNACION(token):
    r'='
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_MUL(token):
    r'\*'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_RESTA(token):
    r'-'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_SUMA(token):
    r'\+'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_NOT(token):
    r'!'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_AND(token):
    r'&&'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_OR(token):
    r'\|\|'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_DIV(token):
    r'/'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_PUNTO(token):
    r'\.'
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_COMA(token):
    r','
    token.column = find_column(token.lexer.lexdata, token)
    return token 

def t_CHAR_VALUE(token): 
    r'\'([^\'\\\n]|\\.)\''
    token.length = len(token.value)
    token.value = token.value[1:-1] # se quitan las comillas 
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_HEX_VALUE(token):
    r'0x[0-9A-F]+'
    token.type = 'INT_VALUE' # modificación del tipo a entero
    token.length = len(token.value)
    # conversor a decimal
    token.value = int(token.value, 16)
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_BIN_VALUE(token):
    r'0b[01]+' 
    token.type = 'INT_VALUE' # modificación del tipo a entero
    token.length = len(token.value)
    # conversor a decimal
    token.value = int(token.value, 2)
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_OCT_VALUE(token):
    r'0[0-7]+'
    token.type = 'INT_VALUE' # modificación del tipo a entero
    token.length = len(token.value)
    # conversor a decimal
    token.value = int(token.value, 8)
    token.column = find_column(token.lexer.lexdata, token)
    return token   

def t_FLOAT_VALUE(token):
   r'((0|[1-9][0-9]*)\.[0-9]+([eE][-+]?[0-9]+)?|(0|[1-9][0-9]*)[eE][-+]?[0-9]+)'
   token.length = len(token.value)
   token.value = float(token.value)
   token.column = find_column(token.lexer.lexdata, token)
   return token

def t_INT_VALUE(token):
    r'[1-9][0-9]*|0'
    token.value = int(token.value)
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_ID(token):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    token.type = reserved.get(token.value, 'ID')
    if token.type == 'TRUE':
        token.value = True  # conversor de True a booleano 
    elif token.type == 'FALSE':
        token.value = False # conversor de False a booleano 
    token.column = find_column(token.lexer.lexdata, token)
    return token

# caracter de nueva línea
def t_NEWLINE(token):
    r'\n+'
    token.lexer.lineno += token.value.count('\n')

# caracteres a ignorar de manera automática
t_ignore = ' \t' 

#caracteres no reconocidos
def t_error(token): 
    col = find_column(token.lexer.lexdata, token)
    print(f'illegal character at line {token.lineno}, column {col}')
    token.lexer.skip(1) # recuperarse del error (se salta el caracter del error)

# contador de columnas 
def find_column(input_data, token):
    line_start = input_data.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) 

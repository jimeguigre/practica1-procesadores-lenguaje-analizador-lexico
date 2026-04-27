import ply.lex as lex

# --- VARIABLES GLOBALES PARA RECUPERACIÓN DE ERRORES ---
lexer_errors = []

reserved = {
    'true': 'TRUE', 'false': 'FALSE', 'int': 'INT', 'float': 'FLOAT', 
    'char': 'CHAR', 'boolean': 'BOOLEAN', 'void': 'VOID', 'return': 'RETURN',
    'if': 'IF', 'else': 'ELSE', 'do': 'DO', 'while': 'WHILE',
    'print':'PRINT', 'new':'NEW', 'record': 'RECORD', 'break': 'BREAK',
}

tokens = [
    'ID', 'INT_VALUE', 'FLOAT_VALUE', 'CHAR_VALUE', 'EQUALS', 'PUNTO_COMA', 
    'L_BRACKET', 'R_BRACKET', 'L_PAREN', 'R_PAREN', 'MAYOR_IGUAL', 'MENOR_IGUAL',
    'MENOR', 'MAYOR', 'ASIGNACION', 'MUL', 'DIV', 'RESTA', 'SUMA', 'AND',
    'OR', 'NOT', 'PUNTO', 'COMA',
] + list(reserved.values())

def find_column(input_data, token):
    line_start = input_data.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) 

t_PUNTO_COMA = r';'
t_L_BRACKET = r'\{'
t_R_BRACKET = r'\}'
t_L_PAREN = r'\('
t_R_PAREN = r'\)'
t_MAYOR_IGUAL = r'>='
t_MENOR_IGUAL = r'<='
t_MAYOR = r'>'
t_MENOR = r'<'
t_EQUALS = r'=='
t_ASIGNACION = r'='
t_MUL = r'\*'
t_RESTA = r'-'
t_SUMA = r'\+'
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'
t_DIV = r'/'
t_PUNTO = r'\.'
t_COMA = r','

def t_COMMENT(t):
    r'//.*|/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_CHAR_VALUE(token): 
    r"'([^'\\]|\\.)'"
    token.length = len(token.value)
    token.value = token.value[1:-1]
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_HEX_VALUE(token):
    r'0x[0-9A-F]+'
    token.type = 'INT_VALUE'
    token.length = len(token.value)
    token.value = int(token.value, 16)
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_BIN_VALUE(token):
    r'0b[01]+' 
    token.type = 'INT_VALUE'
    token.length = len(token.value)
    token.value = int(token.value, 2)
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_OCT_VALUE(token):
    r'0[0-7]+'
    token.type = 'INT_VALUE'
    token.length = len(token.value)
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
        token.value = True
    elif token.type == 'FALSE':
        token.value = False
    token.column = find_column(token.lexer.lexdata, token)
    return token

def t_NEWLINE(token):
    r'\n+'
    token.lexer.lineno += token.value.count('\n')

t_ignore = ' \t' 

# RECUPERACIÓN DE ERRORES LÉXICOS
def t_error(token): 
    col = find_column(token.lexer.lexdata, token)
    error_msg = f"[ERROR LÉXICO] Carácter no reconocido '{token.value[0]}' en línea {token.lineno}, columna {col}."
    lexer_errors.append(error_msg)
    token.lexer.skip(1) # Modo Pánico Léxico: Saltamos el carácter y seguimos
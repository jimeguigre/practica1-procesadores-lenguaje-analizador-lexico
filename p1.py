# reconocer los elementos del lenguaje a nivel léxico

# importar PLY lex
import ply.lex as lex

# cargar fichero con los datos de ejemplo
import sys

# definir token PALABRA y token NUMERO
tokens = (
    "VARIABLE",
    "NUMBER"
)

# regexr para probar expresiones regulares
t_VARIABLE = r'[a-zA-Z][a-zA-Z0-9_]*' #primera opción para capturar tokens

def t_NUMBER(token): # segunda opción para capturar tokens
    r'[1-9][0-9]*|0' # [0-9] es igual que \d
    token.value = int(token.value)
    return token

def t_NEWLINE(token):
    r'\n+'
    token.lexer.lineno += token.value.count('\n')


t_ignore = ' \t' # caracteres a ignorar de manera automática

def t_error(token): #caracteres no reconocidos
    print(f'illegal character at {token.lineno}, {token.lexpos}')
    token.lexer.skip(1) # recuperarse del error (se salta el caracter del error)

# construir el lexer
lexer = lex.lex()

#lexer.input("palabra variable_1 123 19")
#for token in lexer:
    #print(token.type, token.value)

# cargando fichero
file = open(sys.argv[1])
lexer.input(file.read())
for token in lexer:
    print(token.type, token.value)

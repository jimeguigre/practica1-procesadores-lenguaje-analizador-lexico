import ply.yacc as yacc
from lexer import tokens

# Precedencia para resolver ambigüedades (ej. dangling-else y matemáticas)
precedence = (
    ('right', 'ASIGNACION'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUALS'),
    ('left', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MUL', 'DIV'),
    ('right', 'NOT', 'UMINUS'), 
    ('left', 'PUNTO'),
)

# Estructura del programa
def p_program(p):
    '''program : item_list
               | empty'''
    pass

def p_item_list(p):
    '''item_list : item_list item
                 | item'''
    pass

def p_item(p):
    '''item : statement
            | function_decl'''
    pass

# Tipos
def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | BOOLEAN
            | ID'''
    pass

# Funciones
def p_function_decl(p):
    '''function_decl : type ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET
                     | VOID ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET'''
    pass

def p_param_list(p):
    '''param_list : param_list_items
                  | empty'''
    pass

def p_param_list_items(p):
    '''param_list_items : param_list_items COMA param
                        | param'''
    pass

def p_param(p):
    '''param : type ID'''
    pass

# Bloques y sentencias
def p_statement_list(p):
    '''statement_list : statement_list statement
                      | empty'''
    pass

def p_statement(p):
    '''statement : var_declaration PUNTO_COMA
                 | assignment PUNTO_COMA
                 | if_statement
                 | while_statement
                 | do_while_statement
                 | record_decl
                 | function_call PUNTO_COMA
                 | BREAK PUNTO_COMA
                 | RETURN expression PUNTO_COMA
                 | RETURN PUNTO_COMA
                 | PUNTO_COMA'''
    pass

# Variables
def p_var_declaration(p):
    '''var_declaration : type id_list'''
    pass

def p_id_list(p):
    '''id_list : id_list COMA element_id
               | element_id'''
    pass

def p_element_id(p):
    '''element_id : ID
                  | ID ASIGNACION expression'''
    pass

def p_assignment(p):
    '''assignment : location ASIGNACION expression'''
    pass

def p_location(p):
    '''location : ID
                | location PUNTO ID'''
    pass

# Control de flujo
def p_if_statement(p):
    '''if_statement : IF L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET
                    | IF L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET ELSE L_BRACKET statement_list R_BRACKET'''
    pass

def p_while_statement(p):
    '''while_statement : WHILE L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET'''
    pass

def p_do_while_statement(p):
    '''do_while_statement : DO L_BRACKET statement_list R_BRACKET WHILE L_PAREN expression R_PAREN PUNTO_COMA'''
    pass

# Registros
def p_record_decl(p):
    '''record_decl : RECORD ID L_PAREN param_list R_PAREN PUNTO_COMA'''
    pass

# Llamadas y Expresiones
def p_function_call(p):
    '''function_call : ID L_PAREN arg_list R_PAREN
                     | PRINT L_PAREN arg_list R_PAREN'''
    pass

def p_arg_list(p):
    '''arg_list : arg_list_items
                | empty'''
    pass

def p_arg_list_items(p):
    '''arg_list_items : arg_list_items COMA expression
                      | expression'''
    pass

def p_instantiation(p):
    '''instantiation : NEW ID L_PAREN arg_list R_PAREN'''
    pass

def p_expression_binop(p):
    '''expression : expression SUMA expression
                  | expression RESTA expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression AND expression
                  | expression OR expression
                  | expression EQUALS expression
                  | expression MAYOR expression
                  | expression MENOR expression
                  | expression MAYOR_IGUAL expression
                  | expression MENOR_IGUAL expression'''
    pass

def p_expression_unop(p):
    '''expression : RESTA expression %prec UMINUS
                  | NOT expression'''
    pass

def p_expression_group(p):
    '''expression : L_PAREN expression R_PAREN'''
    pass

def p_expression_base(p):
    '''expression : literal
                  | location
                  | function_call
                  | instantiation'''
    pass

def p_literal(p):
    '''literal : INT_VALUE
               | FLOAT_VALUE
               | CHAR_VALUE
               | TRUE
               | FALSE'''
    pass

def p_empty(p):
    '''empty :'''
    pass

# Manejo de Errores
def p_error(p):
    if p:
        print(f"[ERROR] Token '{p.type}' inesperado en la linea {p.lineno}")
    else:
        print("[ERROR] Error de sintaxis en el final del archivo")
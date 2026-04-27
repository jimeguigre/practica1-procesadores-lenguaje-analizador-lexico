import ply.yacc as yacc
from lexer import tokens

# --- TABLAS DE SÍMBOLOS Y ERRORES ---
symbol_table = {}
records_table = {}
functions_table = {}
semantic_errors = []
syntax_errors = []

# Precedencia
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

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | BOOLEAN
            | ID'''
    p[0] = p[1]

def p_function_decl(p):
    '''function_decl : type ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET
                     | VOID ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET'''
    ret_type = p[1]
    name = p[2]
    params = p[4] if p[4] else []
    
    if name not in functions_table:
        functions_table[name] = []
    
    # Sobrecarga: Guardamos la firma
    sig = {'params': params, 'return': ret_type}
    functions_table[name].append(sig)

def p_param_list(p):
    '''param_list : param_list_items
                  | empty'''
    p[0] = p[1]

def p_param_list_items(p):
    '''param_list_items : param_list_items COMA param
                        | param'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_param(p):
    '''param : type ID'''
    p[0] = f"{p[2]}:{p[1]}"
    symbol_table[p[2]] = p[1] # Guardar parámetro en tabla

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
                 | expression PUNTO_COMA
                 | BREAK PUNTO_COMA
                 | RETURN expression PUNTO_COMA
                 | RETURN PUNTO_COMA
                 | PUNTO_COMA'''
    pass

# RECUPERACIÓN SINTÁCTICA (MODO PÁNICO)
def p_statement_error(p):
    '''statement : error PUNTO_COMA'''
    # Ignora los tokens hasta encontrar un punto y coma
    syntax_errors.append(f"[ERROR SINTÁCTICO] Sentencia mal formada cerca de la línea {p.lineno(1)}. Análisis recuperado.")

def p_var_declaration(p):
    '''var_declaration : type id_list
                       | type ID ASIGNACION expression'''
    v_type = p[1]
    if len(p) == 3:
        for var in p[2]:
            if var in symbol_table:
                semantic_errors.append(f"[ERROR SEMÁNTICO] Variable '{var}' re-declarada en línea {p.lineno(2)}")
            else:
                symbol_table[var] = v_type
    else:
        var = p[2]
        if var in symbol_table:
            semantic_errors.append(f"[ERROR SEMÁNTICO] Variable '{var}' re-declarada en línea {p.lineno(2)}")
        else:
            symbol_table[var] = v_type
            # Aquí iría validación de tipos entre v_type y p[4]

def p_id_list(p):
    '''id_list : id_list COMA ID
               | ID'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_assignment(p):
    '''assignment : location ASIGNACION expression'''
    var = p[1]
    if var not in symbol_table and "." not in var:
        semantic_errors.append(f"[ERROR SEMÁNTICO] Variable '{var}' no declarada (Línea {p.lineno(2)})")

def p_location(p):
    '''location : ID
                | location PUNTO ID'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}.{p[3]}"

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

def p_record_decl(p):
    '''record_decl : RECORD ID L_PAREN param_list R_PAREN PUNTO_COMA'''
    name = p[2]
    params = p[4] if p[4] else []
    if name in records_table:
        semantic_errors.append(f"[ERROR SEMÁNTICO] Registro '{name}' re-declarado en línea {p.lineno(2)}")
    else:
        records_table[name] = params

def p_function_call(p):
    '''function_call : ID L_PAREN arg_list R_PAREN
                     | PRINT L_PAREN arg_list R_PAREN'''
    p[0] = 'void' # Simplificación de retorno

def p_arg_list(p):
    '''arg_list : arg_list_items
                | empty'''
    p[0] = p[1]

def p_arg_list_items(p):
    '''arg_list_items : arg_list_items COMA expression
                      | expression'''
    pass

def p_instantiation(p):
    '''instantiation : NEW ID L_PAREN arg_list R_PAREN'''
    p[0] = p[2]

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
    p[0] = 'evaluated_expr'

def p_expression_unop(p):
    '''expression : RESTA expression %prec UMINUS
                  | NOT expression'''
    p[0] = 'evaluated_expr'

def p_expression_group(p):
    '''expression : L_PAREN expression R_PAREN'''
    p[0] = p[2]

def p_expression_base(p):
    '''expression : literal
                  | location
                  | function_call
                  | instantiation'''
    p[0] = p[1]

def p_literal(p):
    '''literal : INT_VALUE
               | FLOAT_VALUE
               | CHAR_VALUE
               | TRUE
               | FALSE'''
    p[0] = type(p[1]).__name__

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        syntax_errors.append(f"[ERROR SINTÁCTICO] Token '{p.type}' inesperado en la línea {p.lineno}")
    else:
        syntax_errors.append("[ERROR SINTÁCTICO] EOF inesperado")
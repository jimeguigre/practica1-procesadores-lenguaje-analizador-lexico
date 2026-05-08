import ply.yacc as yacc
from lexer import tokens

# ═══════════════════════════════════════════════
# TABLAS GLOBALES Y ESTADO
# ═══════════════════════════════════════════════
symbol_table = {}
records_table = {}
functions_table = {}
semantic_errors = []
syntax_errors = []
quartets = []

_temp_counter = 0
_label_counter = 0

def _reset_codegen():
    global _temp_counter, _label_counter
    _temp_counter = 0
    _label_counter = 0
    symbol_table.clear()
    records_table.clear()
    functions_table.clear()
    semantic_errors.clear()
    syntax_errors.clear()
    quartets.clear()

def new_temp():
    global _temp_counter
    _temp_counter += 1
    return f"@T{_temp_counter}"

def new_label():
    global _label_counter
    _label_counter += 1
    return f"@L{_label_counter}"

def emit(op, arg1="_", arg2="_", result="_"):
    quartets.append(f"{op},{arg1},{arg2},{result}")

OP_TO_INSTR = {
    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
    '>': 'GT', '>=': 'GTE', '<': 'LT', '<=': 'LTE',
    '==': 'EQ', '&&': 'AND', '||': 'OR',
}

# ═══════════════════════════════════════════════
# PRECEDENCIA
# ═══════════════════════════════════════════════
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

# ═══════════════════════════════════════════════
# GRAMÁTICA
# ═══════════════════════════════════════════════

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
            | function_decl
            | record_decl'''
    pass

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | BOOLEAN
            | VOID
            | ID'''
    p[0] = p[1]

# -- Registros y Funciones --
def p_record_decl(p):
    '''record_decl : RECORD ID L_PAREN param_list R_PAREN PUNTO_COMA'''
    records_table[p[2]] = p[4]

def p_function_decl(p):
    '''function_decl : type ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET'''
    name = p[2]
    if name not in functions_table: functions_table[name] = []
    functions_table[name].append({'params': p[4], 'return': p[1]})
    emit('LABEL', name)

def p_param_list(p):
    '''param_list : param_list_items'''
    p[0] = p[1]

def p_param_list_empty(p):
    '''param_list : empty'''
    p[0] = []

def p_param_list_items(p):
    '''param_list_items : param_list_items COMA param
                        | param'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_param(p):
    '''param : type ID'''
    p[0] = f"{p[2]}:{p[1]}"
    symbol_table[p[2]] = p[1]

# -- Sentencias --
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
                 | expression PUNTO_COMA
                 | print_statement PUNTO_COMA
                 | BREAK PUNTO_COMA
                 | RETURN expression PUNTO_COMA
                 | RETURN PUNTO_COMA
                 | PUNTO_COMA'''
    pass

def p_print_statement(p):
    '''print_statement : PRINT L_PAREN expression R_PAREN'''
    ref = p[3][1] if isinstance(p[3], tuple) else p[3]
    emit('PRINT', ref)

def p_var_declaration(p):
    '''var_declaration : type id_list'''
    for var in p[2]: symbol_table[var] = p[1]

def p_var_declaration_init(p):
    '''var_declaration : type ID ASIGNACION expression'''
    symbol_table[p[2]] = p[1]
    ref = p[4][1] if isinstance(p[4], tuple) else p[4]
    emit('ASSIGN', ref, '_', p[2])

def p_id_list(p):
    '''id_list : id_list COMA ID
               | ID'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

def p_assignment(p):
    '''assignment : location ASIGNACION expression'''
    ref = p[3][1] if isinstance(p[3], tuple) else p[3]
    emit('ASSIGN', ref, '_', p[1])

def p_location(p):
    '''location : ID
                | location PUNTO ID'''
    p[0] = p[1] if len(p) == 2 else f"{p[1]}.{p[3]}"

# -- Expresiones --
def p_expression_binop(p):
    '''expression : expression SUMA expression
                  | expression RESTA expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression MAYOR expression
                  | expression MAYOR_IGUAL expression
                  | expression MENOR expression
                  | expression MENOR_IGUAL expression
                  | expression EQUALS expression
                  | expression AND expression
                  | expression OR expression'''
    target = new_temp()
    op = OP_TO_INSTR.get(p[2])
    ref1 = p[1][1] if isinstance(p[1], tuple) else p[1]
    ref2 = p[3][1] if isinstance(p[3], tuple) else p[3]
    emit(op, ref1, ref2, target)
    p[0] = ('unknown', target)

def p_expression_unary(p):
    '''expression : NOT expression
                  | RESTA expression %prec UMINUS'''
    target = new_temp()
    op = 'NOT' if p[1] == '!' else 'NEG'
    ref = p[2][1] if isinstance(p[2], tuple) else p[2]
    emit(op, ref, '_', target)
    p[0] = ('unknown', target)

def p_expression_new(p):
    '''expression : NEW ID L_PAREN arg_list R_PAREN'''
    target = new_temp()
    emit('NEW_RECORD', p[2], '_', target)
    p[0] = (p[2], target)

def p_expression_call(p):
    '''expression : ID L_PAREN arg_list R_PAREN'''
    target = new_temp()
    emit('CALL', p[1], len(p[3]), target)
    p[0] = ('unknown', target)

def p_expression_leaf(p):
    '''expression : INT_VALUE
                  | FLOAT_VALUE
                  | CHAR_VALUE
                  | TRUE
                  | FALSE
                  | location'''
    p[0] = ('val', str(p[1]))

def p_arg_list(p):
    '''arg_list : arg_list_items'''
    p[0] = p[1]

def p_arg_list_empty(p):
    '''arg_list : empty'''
    p[0] = []

def p_arg_list_items(p):
    '''arg_list_items : arg_list_items COMA expression
                      | expression'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

# -- Control de Flujo --

def p_if_else_statement(p):
    '''if_statement : IF L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET ELSE L_BRACKET statement_list R_BRACKET'''
    l_false = new_label()
    l_end = new_label()
    ref = p[3][1] if isinstance(p[3], tuple) else p[3]
    # Lógica simplificada de emisión (el orden real dependería de acciones intermedias)
    emit('JUMPF', ref, l_false)
    emit('JUMP', l_end)
    emit('LABEL', l_false)
    emit('LABEL', l_end)

def p_if_simple_statement(p):
    '''if_statement : IF L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET'''
    l_end = new_label()
    ref = p[3][1] if isinstance(p[3], tuple) else p[3]
    emit('JUMPF', ref, l_end)
    emit('LABEL', l_end)

def p_while_statement(p):
    '''while_statement : WHILE L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET'''
    l_start = new_label()
    l_end = new_label()
    ref = p[3][1] if isinstance(p[3], tuple) else p[3]
    emit('LABEL', l_start)
    emit('JUMPF', ref, l_end)
    emit('JUMP', l_start)
    emit('LABEL', l_end)

def p_do_while_statement(p):
    '''do_while_statement : DO L_BRACKET statement_list R_BRACKET WHILE L_PAREN expression R_PAREN PUNTO_COMA'''
    l_start = new_label()
    ref = p[7][1] if isinstance(p[7], tuple) else p[7]
    emit('LABEL', l_start)
    emit('JUMPT', ref, l_start)

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        msg = f"[ERROR SINTÁCTICO] Token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)
        print(msg)
    else:
        print("Error de sintaxis al final del archivo")
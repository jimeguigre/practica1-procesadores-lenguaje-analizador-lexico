import ply.yacc as yacc
from lexer import tokens

# TABLAS DE SÍMBOLOS Y ERRORES
symbol_table = {}
records_table = {}
functions_table = {}
semantic_errors = []
syntax_errors = []

# jerarquía de tipos para conversiones automáticas
# char -> int -> float   (boolean no se puede convertir)
TYPE_RANK = {'char': 1, 'int': 2, 'float': 3, 'boolean': -1}

def types_compatible(t1, t2):
    """Devuelve el tipo resultante si t1 y t2 son compatibles, None si no lo son."""
    if t1 == t2:
        return t1
    r1 = TYPE_RANK.get(t1, -1)
    r2 = TYPE_RANK.get(t2, -1)
    # boolean no se mezcla con nada
    if r1 == -1 or r2 == -1:
        return None
    # Ambos en la jerarquía char/int/float -> tipo más general
    return t1 if r1 > r2 else t2

def is_numeric(t):
    """int, float o char (char se puede convertir a int)."""
    return t in ('int', 'float', 'char')

def resolve_location_type(name):
    """Dado 'a' o 'a.b.c', devuelve el tipo o None."""
    parts = name.split('.')
    root = parts[0]
    t = symbol_table.get(root)
    if t is None:
        return None
    for field in parts[1:]:
        fields = records_table.get(t, [])
        found = None
        for f in fields:
            fname, ftype = f.split(':')
            if fname == field:
                found = ftype
                break
        if found is None:
            return None
        t = found
    return t

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

# gramática 

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

# declaración de funciones 

def p_function_decl(p):
    '''function_decl : type ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET
                     | VOID ID L_PAREN param_list R_PAREN L_BRACKET statement_list R_BRACKET'''
    ret_type = p[1]
    name = p[2]
    params = p[4] if p[4] else []
    
    if name not in functions_table:
        functions_table[name] = []

    # Comprobar sobrecarga duplicada (mismos parámetros = error)
    for sig in functions_table[name]:
        if sig['params'] == params:
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Función '{name}' ya declarada con la misma firma en línea {p.lineno(2)}")
            return
    
    # Sobrecarga: Guardamos la firma
    sig = {'params': params, 'return': ret_type}
    functions_table[name].append(sig)

def p_param_list(p):
    '''param_list : param_list_items
                  | empty'''
    p[0] = p[1] if p[1] else []

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

# sentencias 

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

# declaración de variables 
def p_var_declaration(p):
    '''var_declaration : type id_list
                       | type ID ASIGNACION expression'''
    v_type = p[1]
    if len(p) == 3:
        # declaración múltiple sin asignación: int a, b;
        for var in p[2]:
            if var in symbol_table:
                semantic_errors.append(f"[ERROR SEMÁNTICO] Variable '{var}' re-declarada en línea {p.lineno(2)}")
            else:
                symbol_table[var] = v_type
    else:
        # declaración con asignación: int x = expr;
        var = p[2]
        expr_type = p[4]
        if var in symbol_table:
            semantic_errors.append(f"[ERROR SEMÁNTICO] Variable '{var}' re-declarada en línea {p.lineno(2)}")
        else:
            symbol_table[var] = v_type
             # Validar compatibilidad de tipos
            if expr_type and expr_type not in ('unknown', 'void'):
                result = types_compatible(expr_type, v_type)
                if result is None:
                    semantic_errors.append(
                        f"[ERROR SEMÁNTICO] No se puede asignar tipo '{expr_type}' a variable '{var}' "
                        f"de tipo '{v_type}' en línea {p.lineno(2)}")

def p_id_list(p):
    '''id_list : id_list COMA ID
               | ID'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# asignación 
def p_assignment(p):
    '''assignment : location ASIGNACION expression'''
    var = p[1]
    expr_type = p[3]
    # obtener el tipo de la variable destino 
    dest_type = resolve_location_type(var)
    if dest_type is None and '.' not in var:
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] Variable '{var}' no declarada (Línea {p.lineno(2)})")
    elif dest_type and expr_type and expr_type not in ('unknown', 'void'):
        result = types_compatible(expr_type, dest_type)
        if result is None:
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] No se puede asignar tipo '{expr_type}' a '{var}' "
                f"de tipo '{dest_type}' en línea {p.lineno(2)}")
            
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
    cond_type = p[3]
    if cond_type and cond_type not in ('boolean', 'unknown'):
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] La condición del 'if' debe ser 'boolean', se obtuvo '{cond_type}' en línea {p.lineno(1)}")


def p_while_statement(p):
    '''while_statement : WHILE L_PAREN expression R_PAREN L_BRACKET statement_list R_BRACKET'''
    cond_type = p[3]
    if cond_type and cond_type not in ('boolean', 'unknown'):
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] La condición del 'while' debe ser 'boolean', se obtuvo '{cond_type}' en línea {p.lineno(1)}")


def p_do_while_statement(p):
    '''do_while_statement : DO L_BRACKET statement_list R_BRACKET WHILE L_PAREN expression R_PAREN PUNTO_COMA'''
    cond_type = p[7]
    if cond_type and cond_type not in ('boolean', 'unknown'):
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] La condición del 'do-while' debe ser 'boolean', se obtuvo '{cond_type}' en línea {p.lineno(5)}")

# registros 
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
    fname = p[1]
    args = p[3] if p[3] else []

    # print es builtin, no se valida
    if fname == 'print':
        p[0] = 'void'# Simplificación de retoro
        return
     # Comprobar que la función existe
    if fname not in functions_table:
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] Función '{fname}' no declarada o usada antes de su declaración (Línea {p.lineno(1)})")
        p[0] = 'unknown'
        return

    # Buscar firma compatible (primero exacta, luego con conversiones)
    arg_types = [a if a else 'unknown' for a in args]
    best_match = None

    # 1) Búsqueda exacta
    for sig in functions_table[fname]:
        param_types = [s.split(':')[1] for s in sig['params']]
        if len(param_types) == len(arg_types):
            if param_types == arg_types:
                best_match = sig
                break

    # 2) Búsqueda con conversiones automáticas
    if best_match is None:
        for sig in functions_table[fname]:
            param_types = [s.split(':')[1] for s in sig['params']]
            if len(param_types) == len(arg_types):
                ok = True
                for at, pt in zip(arg_types, param_types):
                    if at == 'unknown':
                        continue
                    if types_compatible(at, pt) is None:
                        ok = False
                        break
                if ok:
                    best_match = sig
                    break

    if best_match is None:
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] No existe sobrecarga de '{fname}' compatible con los argumentos "
            f"({', '.join(arg_types)}) en línea {p.lineno(1)}")
        p[0] = 'unknown'
    else:
        p[0] = best_match['return']

def p_arg_list(p):
    '''arg_list : arg_list_items
                | empty'''
    p[0] = p[1] if p[1] else []

def p_arg_list_items(p):
    '''arg_list_items : arg_list_items COMA expression
                      | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# instanciación
def p_instantiation(p):
    '''instantiation : NEW ID L_PAREN arg_list R_PAREN'''
    record_name = p[2]
    if record_name not in records_table:
        semantic_errors.append(
            f"[ERROR SEMÁNTICO] Registro '{record_name}' no declarado en línea {p.lineno(2)}")
        p[0] = 'unknown'
    else:
        p[0] = record_name

# expresiones: operaciones binarias 
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
    t1 = p[1]
    op = p[2]
    t2 = p[3]

    # Si alguno es desconocido, propagamos sin error adicional
    if t1 in ('unknown', None) or t2 in ('unknown', None):
        p[0] = 'unknown'
        return

    if op in ('+', '-'):
        # int, float, char
        result = types_compatible(t1, t2)
        if result is None or not is_numeric(t1) or not is_numeric(t2):
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '{op}' no válida entre tipos '{t1}' y '{t2}'")
            p[0] = 'unknown'
        else:
            p[0] = result

    elif op in ('*', '/'):
        # solo int o float (char se convierte a int)
        result = types_compatible(t1, t2)
        if result is None or not is_numeric(t1) or not is_numeric(t2):
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '{op}' no válida entre tipos '{t1}' y '{t2}'")
            p[0] = 'unknown'
        else:
            # char*char -> int
            p[0] = 'int' if result == 'char' else result

    elif op in ('>', '>=', '<', '<='):
        # int, float, char -> boolean
        result = types_compatible(t1, t2)
        if result is None or not is_numeric(t1) or not is_numeric(t2):
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '{op}' no válida entre tipos '{t1}' y '{t2}'")
            p[0] = 'unknown'
        else:
            p[0] = 'boolean'

    elif op == '==':
        # cualquier tipo igual -> boolean
        result = types_compatible(t1, t2)
        if result is None:
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '==' no válida entre tipos '{t1}' y '{t2}'")
            p[0] = 'unknown'
        else:
            p[0] = 'boolean'
    elif op in ('&&', '||'):
        # solo boolean
        if t1 != 'boolean' or t2 != 'boolean':
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '{op}' requiere tipo 'boolean', se obtuvo '{t1}' y '{t2}'")
            p[0] = 'unknown'
        else:
            p[0] = 'boolean'

    else:
        p[0] = 'unknown'

# espresiones: operaciones unarias 

def p_expression_unop(p):
    '''expression : RESTA expression %prec UMINUS
                  | NOT expression'''
    op = p[1]
    t = p[2]

    if t in ('unknown', None):
        p[0] = 'unknown'
        return

    if op == '-':
        if not is_numeric(t):
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación unaria '-' no válida sobre tipo '{t}'")
            p[0] = 'unknown'
        else:
            p[0] = 'int' if t == 'char' else t

    elif op == '!':
        if t != 'boolean':
            semantic_errors.append(
                f"[ERROR SEMÁNTICO] Operación '!' requiere tipo 'boolean', se obtuvo '{t}'")
            p[0] = 'unknown'
        else:
            p[0] = 'boolean'

def p_expression_group(p):
    '''expression : L_PAREN expression R_PAREN'''
    p[0] = p[2]

# expresiones: base
def p_expression_base(p):
    '''expression : literal
                  | location
                  | function_call
                  | instantiation'''
    # location devuelve nombre de variable; resolver su tipo
    val = p[1]
    if val and isinstance(val, str) and val not in (
            'int', 'float', 'char', 'boolean', 'unknown', 'void') \
            and not val[0].isdigit():
        # Puede ser nombre de variable o tipo ya resuelto
        resolved = resolve_location_type(val)
        p[0] = resolved if resolved else val
    else:
        p[0] = val

def p_literal(p):
    '''literal : INT_VALUE
               | FLOAT_VALUE
               | CHAR_VALUE
               | TRUE
               | FALSE'''
    v = p[1]
    if isinstance(v, bool):
        p[0] = 'boolean'
    elif isinstance(v, int):
        p[0] = 'int'
    elif isinstance(v, float):
        p[0] = 'float'
    elif isinstance(v, str):
        p[0] = 'char'
    else:
        p[0] = 'unknown'

def p_empty(p):
    '''empty :'''
    p[0] = None

# error sintáctico 
def p_error(p):
    if p:
        syntax_errors.append(f"[ERROR SINTÁCTICO] Token '{p.type}' inesperado en la línea {p.lineno}")
    else:
        syntax_errors.append("[ERROR SINTÁCTICO] EOF inesperado")
import sys
import os
import ply.lex as lex
import ply.yacc as yacc
import lexer as scanner
import parser as grammar

def print_errors():
    has_errors = False
    if scanner.lexer_errors:
        has_errors = True
        for err in scanner.lexer_errors: print(err)
    if grammar.syntax_errors:
        has_errors = True
        for err in grammar.syntax_errors: print(err)
    if grammar.semantic_errors:
        has_errors = True
        for err in grammar.semantic_errors: print(err)
    return has_errors

def export_tokens(input_file):
    lexer = lex.lex(module=scanner)
    base_name, _ = os.path.splitext(input_file)
    output_file = base_name + ".token"

    try: 
        with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
            data = f_in.read()
            lexer.input(data)
            for tok in lexer:
                col_start = tok.column 
                length = getattr(tok, 'length', len(str(tok.value)))
                col_end = col_start + length
                f_out.write(f"{{ {tok.type}, {tok.value}, {tok.lineno}, {col_start}, {col_end} }}\n")
        print(f"Tokens guardados en: {output_file}")
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")

def export_semantic_tables(base_name):
    # .symbols
    if grammar.symbol_table:
        with open(base_name + ".symbols", 'w', encoding="utf-8") as f:
            for k, v in grammar.symbol_table.items():
                f.write(f"{k}:{v}\n")
    # .records
    if grammar.records_table:
        with open(base_name + ".records", 'w', encoding="utf-8") as f:
            for k, v in grammar.records_table.items():
                fields = ", ".join(v) if v else ""
                f.write(f"{k}: [{fields}]\n")
    # .functions
    if grammar.functions_table:
        with open(base_name + ".functions", 'w', encoding="utf-8") as f:
            for k, overloads in grammar.functions_table.items():
                for sig in overloads:
                    params = ", ".join(sig['params'])
                    f.write(f"{k}: [{params}],{sig['return']}\n")

def run_compiler(input_file):
    lexer = lex.lex(module=scanner)
    parser = yacc.yacc(module=grammar)
    
    # Limpiar tablas para ejecuciones múltiples
    grammar.symbol_table.clear()
    grammar.records_table.clear()
    grammar.functions_table.clear()
    scanner.lexer_errors.clear()
    grammar.syntax_errors.clear()
    grammar.semantic_errors.clear()

    try:
        with open(input_file, 'r', encoding="utf-8") as f_in:
            data = f_in.read()
            parser.parse(data, lexer=lexer)
            
            # Comprobar si hay errores mediante nuestra estrategia de recuperación
            if print_errors():
                print("\n[INFO] El análisis finalizó con errores, pero la ejecución continuó gracias a la Recuperación de Errores.")
            else:
                # Si no hay errores, generar ficheros
                base_name, _ = os.path.splitext(input_file)
                export_semantic_tables(base_name)
                print(f"Análisis Semántico finalizado con éxito. Tablas exportadas.")
                
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == "-token":
        export_tokens(sys.argv[2])
    elif len(sys.argv) == 2:
        run_compiler(sys.argv[1])
    else:
        print("Uso:")
        print("  Compilar completo: python main.py <fichero.lava>")
        print("  Solo Lexer:        python main.py -token <fichero.lava>")
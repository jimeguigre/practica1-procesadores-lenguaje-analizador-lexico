import sys
import os
import ply.lex as lex
import ply.yacc as yacc
import lexer as scanner
import parser as grammar # Esto importa tu nuevo archivo parser.py

# --- ESTA ES TU PARTE DE LA PRÁCTICA 1 INTACTA ---
def run_lexer(input_file):
    lexer = lex.lex(module=scanner)
    base_name, _ = os.path.splitext(input_file)
    output_file = base_name + ".token"

    try: 
        with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
            data = f_in.read()
            lexer.input(data)
        
            for tok in lexer:
                col_start = tok.column 
                length = getattr(tok, 'length', tok.lexer.lexpos - tok.lexpos)
                col_end = col_start + length

                linea_token = f"{{ {tok.type}, {tok.value}, {tok.lineno}, {col_start}, {col_end} }}\n"
                f_out.write(linea_token)
            
        print(f"Análisis completado. Resultados guardados en: {output_file}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")

# --- ESTA ES LA PARTE NUEVA DE LA PRÁCTICA 2 (PARSER) ---
def run_parser(input_file):
    lexer = lex.lex(module=scanner)
    parser = yacc.yacc(module=grammar)
    
    try:
        with open(input_file, 'r', encoding="utf-8") as f_in:
            data = f_in.read()
            print("Generating LALR tables...")
            parser.parse(data, lexer=lexer)
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")

# --- ESTO DECIDE QUÉ HACER SEGÚN LO QUE ESCRIBA EL PROFESOR EN LA TERMINAL ---
if __name__ == '__main__':
    # Si el profe escribe: python main.py -token archivo.lava
    if len(sys.argv) == 3 and sys.argv[1] == "-token":
        run_lexer(sys.argv[2])
    # Si el profe escribe: python main.py archivo.lava
    elif len(sys.argv) == 2:
        run_parser(sys.argv[1])
    # Si el profe lo escribe mal
    else:
        print("Uso correcto:")
        print("  Para análisis sintáctico (Parser): python main.py <fichero.lava>")
        print("  Para generar tokens (Lexer):       python main.py -token <fichero.lava>")
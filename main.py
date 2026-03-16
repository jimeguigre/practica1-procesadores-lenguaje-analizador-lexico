import sys
import os
import ply.lex as lex
import ply.yacc as yacc
import lexer as scanner
import parser as grammar 

# Parte 1: lexer 
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

# Parte 2: parser
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

# lectura del archivo según lo que se escirba en la terminal
if __name__ == '__main__':
    # Para la ejecución del lexer la entrada es: python main.py -token archivo.lava
    if len(sys.argv) == 3 and sys.argv[1] == "-token":
        run_lexer(sys.argv[2])
    # Para la ejecución del parser la entrada es: python main.py archivo.lava
    elif len(sys.argv) == 2:
        run_parser(sys.argv[1])
    # en caso de que esté mal escrito
    else:
        print("Uso correcto:")
        print("Para análisis sintáctico (Parser): python main.py <fichero.lava>")
        print("Para generar tokens (Lexer): python main.py -token <fichero.lava>")
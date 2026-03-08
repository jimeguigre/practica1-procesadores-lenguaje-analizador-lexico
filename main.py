import ply.lex as lex
import sys
import os
import lexer as scanner
lexer = lex.lex(module=scanner)

if len(sys.argv) > 1:
    input_file = sys.argv[1]
   
    # creacción del archivo de salida
    base_name, _ = os.path.splitext(input_file)
    output_file = base_name + ".token" # .token al final del archivo de salida

    try: 
        with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
            data = f_in.read()
            lexer.input(data)
        
            for tok in lexer:
                # cálculo de columnas ya calculado en el lexer 
                col_start = tok.column 
            
                # cálculo de la longitud real 
                length = getattr(tok, 'length', tok.lexer.lexpos - tok.lexpos)
                col_end = col_start + length

                # formato de salida: { TIPO, VALOR, LÍNEA, COL-INI, COL-FIN }
                linea_token = f"{{ {tok.type}, {tok.value}, {tok.lineno}, {col_start}, {col_end} }}\n"
            
                # escribir en el archivo .token
                f_out.write(linea_token)
            
        print(f"Análisis completado. Resultados guardados en: {output_file}")

    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")
import ply.lex as lex
import sys
import os
from lexer import find_column, tokens


import lexer as scanner
lexer = lex.lex(module=scanner)

if len(sys.argv) > 1:
    input_file = sys.argv[1]
    
    # creacción del archivo de salida
    base_name, _ = os.path.splitext(input_file)
    output_file = base_name + ".token" # .token al final del archivo de salida

    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        data = f_in.read()
        lexer.input(data)
        
        for tok in lexer:
            # cálculo de columnas llamando a find_column
            col_start = find_column(data, tok)
            
            # cálculo fin de columna 
            val_str = tok.lexer.lexmatch.group(0) # usa la longitud del texto original, no el valor convertido
            col_end = col_start + len(val_str)
            
            # formato de salida: { TIPO, VALOR, LÍNEA, COL-INI, COL-FIN }
            linea_token = f"{{ {tok.type}, {tok.value}, {tok.lineno}, {col_start}, {col_end} }}\n"
            
            # escribir en el archivo .token 
            f_out.write(linea_token)
            
    print(f"Análisis completado. Resultados guardados en: {output_file}")

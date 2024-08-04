from lu_lexer import tokenize_text
from lu_parser import Lu
from lu_errors import LuError, LuSyntaxError, LuTypeError, LuNameError

def process_file(input_filename: str, output_filename: str):
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            text = infile.read()
        
        tokens = tokenize_text(text)
        lu_instance = Lu(tokens)
        py_tokens = lu_instance.compile()
        
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.writelines(py_tokens)
        
        print(f"Compilation successful. Output written to {output_filename}")
    except (LuSyntaxError, LuTypeError, LuNameError) as e:
        print(e.full_message)
    except LuError as e:
        print(f"Compilation failed: {e.full_message}")
    except IOError as e:
        print(f"File error: {str(e)}")

if __name__ == "__main__":
    input_file = 'lu/lu/example.lumin'
    output_file = 'output.py'
    process_file(input_file, output_file)
import os
import sys
from lu_lexer import tokenize_text
from lu_parser import Lu
from lu_errors import Error
from lu_logger import info, error, exception
import argparse

def process_file(input_filename: str, output_filename: str, run: bool = False):
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            text = infile.read()
        
        info(f"Processing file: {input_filename}")
        tokens = tokenize_text(text)
        lu_instance = Lu(tokens)
        py_tokens = lu_instance.compile()
        
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.writelines(py_tokens)
        
        info(f"Compilation successful. Output written to {output_filename}")
        
        if run:
            execute_compiled_code(output_filename)
    
    except Error as e:
        error(f"Compilation failed: {e.full_message}")
        sys.exit(1)
    except IOError as e:
        error(f"File error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        exception(f"Unexpected error occurred: {str(e)}")
        sys.exit(1)

def execute_compiled_code(filename: str):
    try:
        info(f"Executing compiled code: {filename}")
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
        exec(code, globals())
    except Exception as e:
        error(f"Error during execution: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Lu Compiler')
    parser.add_argument('input_file', type=str, help='Lu file path (e.g., path/example.lu)')
    parser.add_argument('-o', '--output', type=str, help='Output Python file path (e.g., path/output.py)')
    parser.add_argument('-r', '--run', action='store_true', help='Run the compiled code after compilation')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output or os.path.splitext(input_file)[0] + '.py'
    
    process_file(input_file, output_file, args.run)

if __name__ == "__main__":
    main()
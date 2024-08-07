from lu_lexer import tokenize_text
from lu_parser import Lu
from lu_errors import Error
from lu_logger import info, error, exception
import argparse 

def process_file(input_filename: str, output_filename: str):
    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            text = infile.read()
        if text.startswith("run"):
            run = True
            text = text.removeprefix("run")
        else:
            run = False
        info(f"Processing file: {input_filename}")
        tokens = tokenize_text(text)
        lu_instance = Lu(tokens)
        py_tokens = lu_instance.compile()
        
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.writelines(py_tokens)
        
        if run:
            with open(output_filename, 'r', encoding='utf-8') as outfile:
                code = outfile.read()
                exec(code)
                exit()
        
        info(f"Compilation successful. Output written to {output_filename}")
    except Error as e:
        error(f"Compilation failed: {e.full_message}")
    except IOError as e:
        error(f"File error: {str(e)}")
    except Exception as e:
        exception(f"Unexpected error occurred: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='lu compiler')
    parser.add_argument('input_file', type=str, help='Lu file path (e.g., path/example.lu )')
    parser.add_argument('output_file', type=str, help='output python file path (e.g., path/output.py )')
    args = parser.parse_args()
    process_file(args.input_file, args.output_file)

if __name__ == "__main__":
    #main()
    input_file = 'lu/lu/example.lumin'
    output_file = 'output.py'
    process_file(input_file, output_file)

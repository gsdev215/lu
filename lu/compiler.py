import os
import sys
import ast
import argparse
from lexer import Lexer
from parser import Parser


def process_file(input_filename: str, language: str, filename: str, run: bool = False):
    try:
        # Read file
        with open(input_filename, "r", encoding="utf-8") as infile:
            text = infile.read()

        # Tokenize + Parse LU source
        lexer = Lexer(text)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        parsed_ast = parser.parse()

        # Decide output file
        output_filename = None
        if language in ("py", "python"):
            output_filename = f"{filename}.py"

            from luast_to_pyast import compile_and_exec, to_python_ast

            # Convert LU-AST -> Python AST
            py_ast = to_python_ast(parsed_ast)

            if run:
                # run Python AST directly
                code_obj = compile(py_ast, filename="<lu-compiled>", mode="exec")
                exec(code_obj, globals())
                return

            # Generate Python source code
            py_code = ast.unparse(py_ast)

            with open(output_filename, "w", encoding="utf-8") as outfile:
                outfile.write(py_code)

            print(f"[OK] Generated Python file: {output_filename}")

    except IOError as e:
        print(f"[IO ERROR] Cannot read/write file: {e}")
        sys.exit(1)

    except SyntaxError as e:
        print(f"[SYNTAX ERROR] {e.msg} (line {e.lineno}, column {e.offset})")
        sys.exit(1)

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Lu Compiler")
    parser.add_argument("input_file", type=str, help="Lu file path (example: program.lu)")
    parser.add_argument("-l", "--language", type=str, help="Target language: py")
    parser.add_argument("-r", "--run", action="store_true", help="Run the compiled code")
    args = parser.parse_args()

    input_file = args.input_file
    language = args.language
    filename = os.path.splitext(input_file)[0]

    process_file(input_file, language, filename, args.run)


if __name__ == "__main__":
    main()

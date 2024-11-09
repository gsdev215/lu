
# Lu

**Lu** is a lightweight pseudocode-to-Python compiler, currently supporting basic IGCE-style pseudocode. It uses Python’s built-in AST module to parse and translate pseudocode logic into Python code.

## Supported Features

- **Output Statements**: Converts IGCE pseudocode `OUTPUT` commands to Python’s `print()` function.
- **Conditional Logic**: Handles `IF`, `ELSE`, `ENDIF`, and nested conditional statements.
- **Variable Assignment**: Supports variable declaration and assignment.
- **Error Handling**: Detects and reports syntax issues with details.
- **Logging**: Implements a logging system for debugging.

## Usage

1. Write your IGCE pseudocode in a `.lu` file.
2. Run the Lu compiler:

    ```bash
    python lu/lu_compiler.py path_to_file/<filename>.lu
    ```

   This will generate `<filename>.py`, a Python equivalent of your pseudocode.

## Example

For an input `.lu` file:
```plaintext
IF x > 5 THEN
    OUTPUT x
ELSE
    OUTPUT "Value too low"
ENDIF
```

The compiler will output equivalent Python code.

## Installation

Clone the repository:
```bash
git clone https://github.com/gsdev215/lu.git
```

Then navigate to the `lu` directory and run the compiler as described.

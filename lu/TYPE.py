import ast

class keyword_type:
    def parse_type(self) -> str:
        """Parse a TYPE statement and return the corresponding Python code."""
        self.advance()  # Consume 'TYPE'
        identifier = self.advance().value

        if self.is_at_line_end():
            self.advance()  # Consume newline
            self.indent += 1
            return self.record(identifier)
        else:
            self.advance()  # Consume '='
            return self.enumerated(identifier)

    # Non-composite data type - Enumerated
    def enumerated(self, identifier: str) -> str:
        """Parse an enumerated type and return Python Enum class code."""
        args = self.collect_arguments()
        en = ''
        
        # Attempt to parse the arguments as a tuple
        try:
            result_tuple = ast.literal_eval(args)
        except ValueError:
            modified_args = args.replace("(", "(\"").replace(",", "\",\"").replace(")", "\")")
            modified_args = modified_args.replace("[\"", "[").replace("\"]", "]")
            result_tuple = ast.literal_eval(modified_args)

        if "from enum import Enum" not in self.imports:
            en += ('    ' * self.indent) + "from enum import Enum\n"
        
        en += ('    ' * self.indent) + f"class {identifier}(Enum):\n"
        self.indent += 1
        for i, v in enumerate(result_tuple):
            en += ('    ' * self.indent) + f"{v} = {i}\n"
        self.indent -= 1

        return en

    # Composite data type - Record
    def record(self, identifier: str) -> str:
        """Placeholder for record type parsing, to be implemented."""
        self.imports.append("from dataclasses import dataclass")

        en = f'@dataclass\nclass {identifier}:\n'

        while self.peek().value != 'ENDTYPE':
            en += ('    '*self.indent) + self.parse_declare() + "\n"
            self.advance()
        self.advance()
        self.indent -= 1
        return en

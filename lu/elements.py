from typing import List, Tuple, Union
import ast
import re
from lu_errors import SyntaxError

class elements:
    def parse_declare(self) -> str:
        """Parse a DECLARE statement and return the Python representation."""
        self.advance()  # Consume 'DECLARE'
        identifier = self.advance().value
        self.advance()  # Consume ':'

        expr = ('  ' * self.indent) + f"{identifier} : "
        datatype = self.convert_datatype()
        expr += datatype
        self.advance()  # Consume type

        if datatype == 'list' and not self.is_at_line_end():
            args = self.collect_arguments()
            array = self.parse_array_declaration("ARRAY" + args)
            dimensions = array["dimensions"]
            data_type = self.convert_datatype(array["data_type"])

            if len(dimensions) == 1:
                lower1, upper1 = dimensions[0]
                expr += f" = [{data_type}()] * ({upper1 - lower1 + 1})"
            else:
                lower1, upper1 = dimensions[0]
                lower2, upper2 = dimensions[1]
                expr += f" = [[{data_type}()] * ({upper2 - lower2 + 1}) for _ in range({upper1 - lower1 + 1})]"
        return expr

    def convert_datatype(self, value: str = None) -> str:
        """Convert a pseudocode datatype to Python datatype."""
        value = value if value is not None else self.peek().value
        match value:
            case 'INTEGER':
                return 'int'
            case 'REAL':
                return 'float'
            case 'BOOLEAN':
                return 'bool'
            case 'STRING' | 'CHAR':
                return 'str'
            case 'ARRAY':
                return 'list'
            case 'OBJECT':
                return 'object'
            case _:
                return 'UnknownType'

    def parse_array_declaration(self, declaration: str) -> Union[dict, str]:
        """Parse an array declaration and return its structure."""
        match = re.match(
            r'ARRAY\s*\[(\d+):(\d+)(?:,(\d+):(\d+))?\]\s*OF\s*(\w+)', 
            declaration
        )

        if not match:
            return "Invalid array declaration format."

        lower1, upper1 = int(match.group(1)), int(match.group(2))
        lower2, upper2 = (int(match.group(3)), int(match.group(4))) if match.group(3) and match.group(4) else (None, None)
        data_type = match.group(5)

        if data_type not in self.datatypes:
            raise SyntaxError(f"Invalid data type '{data_type}'.")

        dimensions = [(lower1, upper1)]
        if lower2 is not None and upper2 is not None:
            dimensions.append((lower2, upper2))

        return {
            "dimensions": dimensions,
            "data_type": data_type
        }

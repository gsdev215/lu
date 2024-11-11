from typing import List, Tuple, Union
import ast , re
from lu_errors import SyntaxError
class elements:

    def parse_declare(self):
        self.advance() # consume 'DECLARE'
        identifier = self.advance().value
        self.advance() # consume ':'
        expr =  ('  '*self.indent) + f"{identifier} : "

        datatype = self.convert_datatype()
        expr += datatype
        self.advance() # consume type
        if datatype == 'list' and not self.is_at_line_end():
                args = self.collect_arguments()
                array = self.parse_array_declaration("ARRAY"+args)
                dimensions = array["dimensions"]
                data_type = self.convert_datatype(array["data_type"])
                if len(dimensions) == 1:
                    lower1, upper1 = dimensions[0]
                    expr += f" = [{data_type}()] * ({upper1 - lower1 + 1})"
                else:
                    lower1, upper1 = dimensions[0] 
                    lower2, upper2 =  dimensions[1]
                    expr += f" = [[{data_type}()] * ({upper2 - lower2 + 1}) for _ in range({upper1 - lower1 + 1})]"
        return expr


    def convert_datatype(self,value = None):
        if value is None:
            value = self.peek().value
        match value:
            case 'INTEGER':
                return 'int'
            case 'REAL':
                return 'float'
            case 'BOOLEAN':
                return 'bool'
            case 'STRING':
                return 'str'
            case 'CHAR':  
                return 'str'  
            case 'ARRAY': 
                return 'list'
            case 'OBJECT':  
                return 'object'
            case _:
                return 'UnknownType'  # In case an unrecognized type is encountered


    def parse_array_declaration(self , declaration: str) -> Union[dict, str]:
        # Define allowed data types
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
            SyntaxError(f"Invalid data type '{data_type}'.")

        if lower2 is not None and upper2 is not None:
            # Two-dimensional array
            dimensions = [(lower1, upper1), (lower2, upper2)]
        else:
            # One-dimensional array
            dimensions = [(lower1, upper1)]

        return {
            "dimensions": dimensions,
            "data_type": data_type
        }
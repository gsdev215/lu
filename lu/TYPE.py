import ast
class keyword_type:

    def parse_type(self) -> str:
        self.advance() # consume TYPE

        identifier = self.advance().value
        
        if self.is_at_line_end():
            COMPOSITE : 0
        else:
            self.advance() # consume '='
            k =self.enumerated(identifier)
            return k
            # NON_COMPOSITE

    ## Non-composite data type 

    # enumerated

    def enumerated(self,identifier)->str:
        args = self.collect_arguments()

        try:
            # Attempt to parse with literal_eval
            result_tuple = ast.literal_eval(args)
        except ValueError:
            modified_string = args.replace("(", "(\"").replace(",", "\",\"").replace(")", "\")")
            modified_string = modified_string.replace("[\"", "[").replace("\"]", "]")
            result_tuple = ast.literal_eval(modified_string)
        indent_level = self.indent
        en = ('    ' * self.indent) + "from enum import Enum\n"
        en += ('    ' * self.indent) + f"class {identifier}(Enum):\n"
        self.indent += 1
        for i,v in enumerate(result_tuple):
            en += ('    ' * self.indent) + f"{v} = {i}\n"
        self.indent = indent_level
        return en
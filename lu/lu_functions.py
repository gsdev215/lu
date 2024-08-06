from typing import List, Dict, Any
from lu_errors import Error, SyntaxError, TypeError, NameError

class LuFunction:
    def __init__(self, name: str, parameters: List[Dict[str, str]], return_type: str, body: List[str]):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

class FunctionManager:
    def __init__(self):
        self.functions: Dict[str, LuFunction] = {}

    def define_function(self, function: LuFunction):
        if function.name in self.functions:
            raise NameError(f"Function '{function.name}' is already defined", None)
        self.functions[function.name] = function

    def get_function(self, name: str) -> LuFunction:
        if name not in self.functions:
            raise NameError(f"Function '{name}' is not defined", None)
        return self.functions[name]

    def compile_function(self, function: LuFunction) -> List[str]:
        py_tokens = [f"def {function.name}({', '.join(param['name'] for param in function.parameters)}):\n"]
        for line in function.body:
            py_tokens.append(f"    {line}\n")
        return py_tokens
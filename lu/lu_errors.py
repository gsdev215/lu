class LuError(Exception):
    def __init__(self, message: str, token):
        self.message = message
        self.token = token
        super().__init__(self.full_message)

    @property
    def full_message(self):
        return f"Error at line {self.token.line}, column {self.token.column}: {self.message}"

class LuSyntaxError(LuError):
    pass

class LuTypeError(LuError):
    pass

class LuNameError(LuError):
    pass
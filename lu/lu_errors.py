from lu_logger import error as log_error

class Error(Exception):
    def __init__(self, message: str, token=None):
        self.message = message
        self.token = token
        super().__init__(self.full_message)
        log_error(self.log_message)

    @property
    def full_message(self):
        if self.token:
            return f"{self.__class__.__name__} at line {self.token.line}, column {self.token.column}: {self.message}"
        return f"{self.__class__.__name__}: {self.message}"

    @property
    def log_message(self):
        return f"{self.full_message} | Token: {self.token}"

class SyntaxError(Error):
    def __init__(self, message: str, token=None, expected: str = None):
        self.expected = expected
        super().__init__(message, token)

    @property
    def full_message(self):
        base_message = super().full_message
        if self.expected:
            return f"{base_message}. Expected: {self.expected}"
        return base_message

class TypeError(Error):
    def __init__(self, message: str, token=None, expected_type: str = None, actual_type: str = None):
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(message, token)

    @property
    def full_message(self):
        base_message = super().full_message
        if self.expected_type and self.actual_type:
            return f"{base_message}. Expected type: {self.expected_type}, got: {self.actual_type}"
        return base_message

class NameError(Error):
    pass

class ArgumentError(Error):
    pass

class ReturnError(Error):
    pass

class RuntimeError(Error):
    pass
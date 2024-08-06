import logging
import sys
import os

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        formatted_message = super().format(record)
        if record.levelno == logging.ERROR:
            return f"{RED}ERROR: {formatted_message}{RESET}"
        elif record.levelno == logging.WARNING:
            return f"{YELLOW}WARNING: {formatted_message}{RESET}"
        return formatted_message

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a formatter that includes the calling function's filename and line number
    formatter = ColoredFormatter('%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('lu_compiler.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create a global logger instance
lu_logger = setup_logger('lu_compiler')

# Function to get the caller's information
def get_caller_info():
    frame = sys._getframe(2)  # Get the frame two levels up (skipping this function and the logging function)
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno
    return filename, lineno

# Custom logging functions that include caller info
def debug(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.debug(f"[{filename}:{lineno}] {msg}", *args, **kwargs)

def info(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.info(f"[{filename}:{lineno}] {msg}", *args, **kwargs)

def warning(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.warning(f"[{filename}:{lineno}] {msg}", *args, **kwargs)

def error(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.error(f"[{filename}:{lineno}] {msg}", *args, **kwargs)

def critical(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.critical(f"[{filename}:{lineno}] {msg}", *args, **kwargs)

def exception(msg, *args, **kwargs):
    filename, lineno = get_caller_info()
    lu_logger.exception(f"[{filename}:{lineno}] {msg}", *args, **kwargs)
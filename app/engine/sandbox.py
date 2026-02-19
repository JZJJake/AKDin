
import math
import numpy as np
import pandas as pd
from app.engine.base import BaseStrategy

def execute_strategy_code(code_str: str) -> BaseStrategy:
    """
    Executes the user's strategy code and returns the class object.
    """

    # Safe globals
    safe_globals = {
        '__builtins__': {
            '__build_class__': __build_class__,
            '__name__': '__main__',
            # '__import__': __import__, # Disabled for security. Use pre-injected modules.
        },
        'math': math,
        'np': np,
        'pd': pd,
        'BaseStrategy': BaseStrategy,
        'print': print, # Allow print for debugging
        'range': range,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'min': min,
        'max': max,
        'sum': sum,
        'abs': abs,
        'bool': bool,
        'enumerate': enumerate,
        'zip': zip,
        'sorted': sorted,
        'reversed': reversed,
        'set': set,
        'tuple': tuple,
        'any': any,
        'all': all,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'type': type,
        'super': super,
        'slice': slice,
    }

    local_vars = {}

    try:
        exec(code_str, safe_globals, local_vars)
    except Exception as e:
        raise ValueError(f"Error executing strategy code: {e}")

    # Find the class that inherits from BaseStrategy
    strategy_class = None
    for name, obj in local_vars.items():
        if isinstance(obj, type) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
            strategy_class = obj
            break

    if not strategy_class:
        raise ValueError("No strategy class inheriting from BaseStrategy found in the code.")

    return strategy_class

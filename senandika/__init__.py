"""
SenandCode - Bahasa pemrograman puitis dalam Bahasa Indonesia 🌸

Setiap baris adalah puisi. Setiap program adalah antologi.
"""

__version__ = "0.1.0"
__author__ = "SenandCode Team"
__license__ = "MIT"

from senandika.lexer import Lexer
from senandika.parser import Parser
from senandika.interpreter import Interpreter

__all__ = ["Lexer", "Parser", "Interpreter", "__version__"]

import os
from .error import ErrorHandler

class Lexer:
    def __init__(self, syntax):
        self.syntax = syntax

    def process_file(self, filepath):
        if not os.path.exists(filepath):
            ErrorHandler.fatal(f"Source file not found", context=filepath)

        clean_lines = []
        with open(filepath, 'r') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line: continue
                
                comment_char = self.syntax.get('COMMENT', '~~~')
                if line.startswith(comment_char): continue
                
                clean_lines.append((idx + 1, line))
        
        return clean_lines
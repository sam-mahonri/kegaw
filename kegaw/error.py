import sys

class ErrorHandler:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @staticmethod
    def fatal(message, context=None, line_num=None):
        prefix = f"{ErrorHandler.FAIL}[FATAL ERROR]{ErrorHandler.ENDC}"
        loc = f" (Line {line_num})" if line_num else ""
        ctx = f" [{context}]" if context else ""
        print(f"{prefix}{ctx}{loc}: {message}", file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def warn(message):
        print(f"{ErrorHandler.WARNING}[WARN] {message}{ErrorHandler.ENDC}")

    @staticmethod
    def info(message):
        print(f"{ErrorHandler.OKBLUE}[INFO] {message}{ErrorHandler.ENDC}")

    @staticmethod
    def success(message):
        print(f"{ErrorHandler.OKGREEN}[SUCCESS] {message}{ErrorHandler.ENDC}")
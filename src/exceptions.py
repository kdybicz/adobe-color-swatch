"""
Exceptions used in the app.
"""

class ValidationError(Exception):
    """Error raised in case of any data validation problems"""
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    def __str__(self) -> str:
        return repr(self.message)

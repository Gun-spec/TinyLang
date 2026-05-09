"""Shared error helpers for TinyScript."""


def location_suffix(line=None, column=None):
    if line is None:
        return ""
    if column is not None:
        return f" (line {line}, column {column})"
    return f" (line {line})"


class TinyScriptRuntimeError(RuntimeError):
    """Runtime error carrying optional source location."""

    def __init__(self, message, *, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self):
        return super().__str__() + location_suffix(self.line, self.column)

from .context import ContextManager


class AbortException(Exception):
    def __init__(self, message: str, ctx: ContextManager, suppress_response: bool = False, log_message: bool = False):
        self.message = message
        self.ctx = ctx
        self.suppress_response = suppress_response
        self.log_message = log_message

        super().__init__(message)

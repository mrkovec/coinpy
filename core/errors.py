class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, msg: str, original_exception: Exception = None) -> None:
        # super(Error, self).__init__(msg + (": %s" % original_exception))
        super().__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception


# class HashError(Error):
#     # """Exception raised for errors in the input.
#     #
#     # Attributes:
#     #     expression -- input expression in which the error occurred
#     #     message -- explanation of the error
#     # """
#
#     def __init__(self, message: str) -> None:
#         self.message = message
#
# class DataError(Error):
#     def __init__(self, message: str) -> None:
#         self.message = message

class DjangoNetboxConfluenceException(Exception):
    """
    Base exceptions for app.
    """


class WikiUpdateException(DjangoNetboxConfluenceException):
    """
    Exception class for WikiPageUpdater exceptions.
    """

class AuthorizationException(DjangoNetboxConfluenceException):
    """
    Exception for the case when webhook request is not authorized.
    """

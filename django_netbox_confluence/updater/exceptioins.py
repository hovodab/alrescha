class DjangoNetboxConfluenceException(Exception):
    """
    Base exceptions for app.
    """


class WikiUpdateException(DjangoNetboxConfluenceException):
    """
    Exception class for WikiPageUpdater exceptions.
    """

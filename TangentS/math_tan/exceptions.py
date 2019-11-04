__author__ = 'Nidhin'


class UnknownTagException(Exception):
    """
    An exception to indicate unknown Mathml tag
    """

    def __init__(self, tag):
        self.tag = tag
"""This module exports auxiliary classes and functions."""
import sys
import threading


class SysRedirect():
    """Class to redirect stdout to a file-like object."""

    def __init__(self):
        """Class contructor."""
        self.stdout = sys.stdout
        self.redirections = {}

    @classmethod
    def register(cls, out_file):
        """Redirect current thread stdout to a file-like object.

        :param out_file: object to write output to
        :type out_file: file-like object
        """
        cls.install()
        ident = threading.currentThread().ident
        if ident in sys.stdout.redirections:
            sys.stdout.redirections[ident].close()
        sys.stdout.redirections[ident] = out_file

    def write(self, message):
        """Write a message to the registered file-like object or stdout as appropriate.

        The main purpose of this function is to be called by the `print` function. Calling
        this function directly is not encouraged.

        :param message: message to write
        :type message: str
        """
        ident = threading.currentThread().ident
        if ident in self.redirections:
            self.redirections[ident].write(message)
        else:
            self.stdout.write(message)

    def flush(self):
        """Do nothing.

        This is required to replace stdout.
        """
        pass

    @classmethod
    def install(cls):
        """Install the redirector on stdout."""
        if not isinstance(sys.stdout, cls):
            sys.stdout = cls()

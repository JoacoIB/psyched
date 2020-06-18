import sys
import threading


class SysRedirect(object):
    def __init__(self):
        self.stdout = sys.stdout
        self.redirections = {}

    @classmethod
    def register(cls, f):
        cls.install()
        ident = threading.currentThread().ident
        if ident in sys.stdout.redirections:
            sys.stdout.redirections[ident].close()
        sys.stdout.redirections[ident] = f

    def write(self, message):
        ident = threading.currentThread().ident
        if ident in self.redirections:
            self.redirections[ident].write(message)
        else:
            self.stdout.write(message)

    def flush(self):
        pass

    @classmethod
    def install(cls):
        if type(sys.stdout) != cls:
            sys.stdout = cls()

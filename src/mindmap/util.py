import os
import sys
import tempfile
from contextlib import contextmanager
from html.parser import HTMLParser
from io import StringIO


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class DevNull:
    def write(self, msg):
        pass


@contextmanager
def redirect_stderr_to_stdout():
    stderr = sys.stderr
    sys.stderr = sys.stdout
    try:
        yield None
    finally:
        sys.stderr = stderr


# from https://stackoverflow.com/questions/23212435/permission-denied-to-write-to-my-temporary-file
class CustomNamedTemporaryFile:
    """
    This custom implementation is needed because of the following limitation of tempfile.NamedTemporaryFile:

    > Whether the name can be used to open the file a second time, while the named temporary file is still open,
    > varies across platforms (it can be so used on Unix; it cannot on Windows NT or later).
    """

    def __init__(self, mode='wb', delete=True):
        self._mode = mode
        self._delete = delete

    def __enter__(self):
        # Generate a random temporary file name
        file_name = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        # Ensure the file is created
        open(file_name, "x").close()
        # Open the file in the given mode
        self._tempFile = open(file_name, self._mode)
        return self._tempFile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tempFile.close()
        if self._delete:
            os.remove(self._tempFile.name)


def named_temporary_file(name, mode):
    file_name = os.path.join(tempfile.gettempdir(), name)
    # Ensure the file is created
    open(file_name, "w").close()
    # Open the file in the given mode
    return open(file_name, mode)

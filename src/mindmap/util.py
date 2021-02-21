import sys
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

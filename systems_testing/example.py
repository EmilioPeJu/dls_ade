from pkg_resources import require
require('nose')
from nose.tools import assert_equal
import sys


class InputTest(object):
    def __init__(self, settings):
        self.description = settings  # Use to name the individual tests
        self.settings = settings

    def test_settings(self):
        assert_equal(self.settings % 2, 0)

    def run_script(self):
        self.settings += 1

    def __call__(self):
        self.run_script()
        self.test_settings()


def test_generator():
    for i in range(0, 10):
        yield InputTest(i)

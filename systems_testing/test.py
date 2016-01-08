#! /bin/env dls-python
from test2 import MyError

raise MyError("This "
              "is "
              "the expected message\n"
              "for the test\n"
              "ing")
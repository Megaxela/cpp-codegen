import os
import sys
import argparse

import pytest


def main():
    pytest_args = [
        "-vvv",
        os.path.join(os.path.dirname(__file__), "tests"),
    ] + sys.argv

    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main())

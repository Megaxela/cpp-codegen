import os
import sys
import argparse

import pytest


def parse_arguments():
    args = argparse.ArgumentParser()

    args.add_argument("--report", type=str)

    return args.parse_args()


def main(args):
    pytest_args = [
        "-vvv",
        os.path.join(os.path.dirname(__file__), "tests"),
    ]

    if args.report is not None:
        pytest_args.append(f"--junitxml={args.report}")

    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))

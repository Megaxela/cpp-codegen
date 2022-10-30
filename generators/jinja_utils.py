import re
import json

CAMEL_TO_SNAKE_RE_1 = re.compile("(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_RE_2 = re.compile("([a-z0-9])([A-Z])")

# taken from https://stackoverflow.com/a/1176023
def camel_to_snake(name):
    name = CAMEL_TO_SNAKE_RE_1.sub(r"\1_\2", name)
    return CAMEL_TO_SNAKE_RE_2.sub(r"\1_\2", name).lower()


def to_cpp_str(content):
    return json.dumps(content)

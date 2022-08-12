import clang.cindex

from generators.basic_generator import BasicGenerator
from generators.enum.conversions.to_string_conversion import ToStringConversion


class EnumGenerator(BasicGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._conversions = {
            ToStringConversion(),
        }

    def need_to_generate(node: clang.cindex.Cursor) -> bool:
        if node.kind == clang.cindex.CursorKind.ENUM_DECL:
            return True
        return False

    def generate(node: clang.cindex.Cursor):
        comment = node.brief_comment

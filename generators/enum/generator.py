import clang.cindex
import re
import dataclasses
import typing as tp
import enum
import os

import jinja2

from generators.basic_generator import (
    BasicGenerator,
    FileInfo,
    GeneratingConfig,
)
from generators.enum.conversions.basic_conversion import ConversionResults
from generators.enum.conversions.to_string_conversion import ToStringConversion
from generators.enum.conversions.to_json_conversion import ToJsonConversion

# from generators.enum.conversions.to_json_conversion import ToJsonConversion
from generators.enum.enum_value_configuration import (
    EnumValueConfiguration,
    EnumConfiguration,
)


@dataclasses.dataclass()
class EnumConversionConfiguration:
    converters: tp.Set[str]


class ConversionEntryParseState(enum.Enum):
    BEGIN = enum.auto()
    VALUE = enum.auto()
    POSTFIX = enum.auto()


@dataclasses.dataclass()
class ConversionEntryContext:
    state: ConversionEntryParseState
    comment_line: str
    symbol_index: int
    result: tp.Dict[str, str]
    value_cached: str = ""


class EnumGenerator(BasicGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._header_template = self._load_template("header.jinja2")
        self._source_template = self._load_template("source.jinja2")

        self._comment_begin_regex = re.compile(r"^(\*|//<|//)\s*")

        self._conversions = {
            ToStringConversion(),
            ToJsonConversion(),
        }

        self._conversion_entry_parse_states = {
            ConversionEntryParseState.BEGIN: self._parse_conversion_entry_begin,
            ConversionEntryParseState.VALUE: self._parse_conversion_entry_value,
            ConversionEntryParseState.POSTFIX: self._parse_conversion_entry_postfix,
        }

    def need_to_generate(self, node: clang.cindex.Cursor) -> bool:
        if node.kind == clang.cindex.CursorKind.ENUM_DECL:
            return True
        return False

    @staticmethod
    def _fetch_full_name(node: clang.cindex.Cursor):
        result = []

        while node is not None:
            if node.kind != clang.cindex.CursorKind.TRANSLATION_UNIT:
                # result.append((node.spelling, node.kind))
                result.append(node.spelling)
            node = node.semantic_parent

        return list(reversed(result))

    @staticmethod
    def _fetch_namespace(node: clang.cindex.Cursor):
        result = []

        node = node.semantic_parent
        while node is not None:
            if node.kind == clang.cindex.CursorKind.NAMESPACE:
                result.append(node.spelling)
            node = node.semantic_parent

        return list(reversed(result))

    def generate(
        self,
        node: clang.cindex.Cursor,
        file_info: FileInfo,
        generating_config: GeneratingConfig,
    ):
        # Getting codegen config
        config = self._codegen_configuration(node)

        # Getting full enum name
        # This full name contains namespace and parent classes/structs.
        enum_full_name = self._fetch_full_name(node)

        # Getting enum namespace (without parent classes/structs)
        enum_namespace = self._fetch_namespace(node)

        # Getting enum values + configs
        enum_values = self._get_enum_values(node, enum_full_name)

        # Getting enum config
        enum_config = EnumConfiguration(
            typename="::".join(enum_full_name),
            namespace=enum_namespace,
        )

        results: tp.List[ConversionResults] = []
        for converter in self._conversions:
            if converter.name not in config.converters:
                continue

            # Rebuilding mappings
            results.append(
                converter.convert(
                    enum_values={
                        value.enum_value_name: value.conversion_values.get(
                            converter.value_postfix,
                            value.fallback_value,
                        )
                        for value in enum_values
                    },
                    enum_configuration=enum_config,
                    file_info=file_info,
                    generating_config=generating_config,
                )
            )

        include_includes = {
            val for result in results for val in result.required_include_includes
        }

        source_includes = {
            val for result in results for val in result.required_source_includes
        }

        enum_file_include = None
        for include_dir in file_info.project_include_dirs:
            if (
                os.path.commonpath(
                    (
                        file_info.path,
                        include_dir,
                    )
                )
                != "/"
            ):
                enum_file_include = os.path.relpath(file_info.path, include_dir)

        if enum_file_include is None:
            raise RuntimeError(
                f"Unable to find include directory of '{file_info.path}' source file"
            )

        hpp_other_file = os.path.join("converters", f"{node.spelling}.hpp")

        include_path = os.path.join(
            self._include_path,
            hpp_other_file,
        )

        source_path = os.path.join(
            self._source_path,
            "converters",
            f"{node.spelling}.cpp",
        )

        os.makedirs(os.path.dirname(include_path), exist_ok=True)
        os.makedirs(os.path.dirname(source_path), exist_ok=True)

        with open(include_path, "w") as f:
            f.write(
                self._header_template.render(
                    enum_file=enum_file_include,
                    includes=include_includes,
                    converters=[result.header_text for result in results],
                )
            )

        with open(source_path, "w") as f:
            f.write(
                self._source_template.render(
                    other_file=hpp_other_file,
                    includes=source_includes,
                    converters=[result.source_text for result in results],
                )
            )

    @staticmethod
    def _parse_conversion_entry_begin(ctx: ConversionEntryContext):
        while ctx.symbol_index < len(ctx.comment_line):
            if ctx.comment_line[ctx.symbol_index] == '"':
                ctx.symbol_index += 1
                ctx.state = ConversionEntryParseState.VALUE
                break
            elif ctx.comment_line[ctx.symbol_index] == " ":
                ctx.symbol_index += 1
                continue
            raise RuntimeError(
                f"Unknown symbol at index {ctx.symbol_index} of comment '{ctx.comment_line}'"
            )

    @staticmethod
    def _parse_conversion_entry_value(ctx: ConversionEntryContext):
        value_start_index = ctx.symbol_index
        while ctx.symbol_index < len(ctx.comment_line):
            # Processing escaping
            if ctx.comment_line[ctx.symbol_index] == "\\":
                ctx.symbol_index += 1
            elif ctx.comment_line[ctx.symbol_index] == '"':
                ctx.value_cached = (
                    ctx.comment_line[value_start_index : ctx.symbol_index]
                    .replace("\\\\", "\\")
                    .replace('\\"', '"')
                )
                ctx.symbol_index += 1
                ctx.state = ConversionEntryParseState.POSTFIX
                return

            ctx.symbol_index += 1

        raise RuntimeError(
            f"Value has not been closed with '\"' in comment '{ctx.comment_line}'"
        )

    @staticmethod
    def _parse_conversion_entry_postfix(ctx: ConversionEntryContext):
        postfix_start_index = ctx.symbol_index
        while ctx.symbol_index < len(ctx.comment_line):
            if ctx.comment_line[ctx.symbol_index] == " ":
                break
            ctx.symbol_index += 1

        if postfix_start_index == ctx.symbol_index:
            raise RuntimeError(
                f"Postfix can not be empty in comment '{ctx.comment_line}"
            )
        ctx.result[
            ctx.comment_line[postfix_start_index : ctx.symbol_index]
        ] = ctx.value_cached
        ctx.value_cached = ""
        ctx.state = ConversionEntryParseState.BEGIN

    def _parse_conversion_entries(self, lines: tp.List[str]) -> tp.Dict[str, str]:
        ctx = ConversionEntryContext(
            state=ConversionEntryParseState.BEGIN,
            comment_line="",
            symbol_index=0,
            result=dict(),
        )
        for line in lines:
            ctx.comment_line = line
            ctx.symbol_index = 0

            while ctx.symbol_index < len(ctx.comment_line):
                self._conversion_entry_parse_states[ctx.state](ctx)

        return ctx.result

    def _get_enum_values(
        self,
        node: clang.cindex.Cursor,
        full_type_name: tp.List[str],
    ) -> tp.List[EnumValueConfiguration]:
        children = node.get_children()

        result: tp.List[EnumValueConfiguration] = list()
        for child in children:
            enum_value_name = f"{'::'.join(full_type_name)}::{child.spelling}"

            # Parsing raw comment if presented
            comment_lines = self._parse_raw_comment(child.raw_comment)
            entries = {}
            if comment_lines:
                entries = self._parse_conversion_entries(comment_lines)

            result.append(
                EnumValueConfiguration(
                    enum_value_name=enum_value_name,
                    fallback_value=child.spelling,
                    conversion_values=entries,
                )
            )
        return result

    def _parse_raw_comment(self, comment):
        if comment is None:
            return None
        return list(
            map(
                lambda line: self._comment_begin_regex.sub("", line),
                filter(
                    lambda line: any(map(lambda ch: ch.isalpha(), line)),
                    [line.strip() for line in comment.split("\n")],
                ),
            )
        )

    def _codegen_configuration(
        self, node: clang.cindex.Cursor
    ) -> EnumConversionConfiguration:
        # Filtering enum comment
        lines = self._parse_raw_comment(node.raw_comment)

        converters = set()

        mark_found = False
        for line in lines:
            if mark_found:
                converters.add(line)

            if line == "@cpp_codegen":
                mark_found = True

        return EnumConversionConfiguration(converters=converters)

    @staticmethod
    def _load_template(name: str):
        with open(os.path.join(os.path.dirname(__file__), "templates", name), "r") as f:
            return jinja2.Template(f.read())

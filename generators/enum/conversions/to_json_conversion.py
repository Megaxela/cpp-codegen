import jinja2
import typing as tp

from generators.basic_generator import (
    FileInfo,
    GeneratingConfig,
)
from generators.enum.enum_value_configuration import (
    EnumConfiguration,
)
from generators.enum.conversions.basic_conversion import (
    BasicConversion,
    ConversionResults,
)
from generators.jinja_utils import to_cpp_str


class ToJsonConversion(BasicConversion):
    NAME = "json_serialization"
    POSTFIX = "json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._header_template = self._load_template("to_json_header.jinja2")
        self._source_template = self._load_template("to_json_source.jinja2")

    def convert(
        self,
        enum_values: tp.Dict[str, str],
        enum_configuration: EnumConfiguration,
        file_info: FileInfo,
        generating_config: GeneratingConfig,
    ) -> ConversionResults:
        render_data = {
            "enum_values": enum_values,
            "enum_data": enum_configuration,
            "to_cpp_str": to_cpp_str,
        }

        return ConversionResults(
            source_text=self._source_template.render(**render_data),
            header_text=self._header_template.render(**render_data),
            required_include_includes={
                "nlohmann/json.hpp",
            },
            required_source_includes={
                "unordered_map",
                "stdexcept",
            },
        )

import abc
import typing as tp
import dataclasses
import os

import jinja2

from generators.basic_generator import (
    FileInfo,
    GeneratingConfig,
)
from generators.enum.enum_value_configuration import (
    EnumValueConfiguration,
    EnumConfiguration,
)


@dataclasses.dataclass()
class ConversionResults:
    source_text: str
    header_text: str
    required_include_includes: tp.Set[str]
    required_source_includes: tp.Set[str]


class BasicConversion(abc.ABC):
    def __init__(self):
        pass

    @property
    def name(self):
        return self.NAME

    @property
    def value_postfix(self):
        return self.POSTFIX

    @abc.abstractmethod
    def convert(
        self,
        enum_values: tp.Dict[str, str],
        file_info: FileInfo,
        generating_config: GeneratingConfig,
    ) -> ConversionResults:
        pass

    @staticmethod
    def _load_template(name: str):
        with open(os.path.join(os.path.dirname(__file__), "templates", name), "r") as f:
            return jinja2.Template(f.read())

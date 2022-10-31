import abc
import dataclasses

import clang.cindex


@dataclasses.dataclass()
class FileInfo:
    project_include_dirs: str
    path: str


@dataclasses.dataclass()
class GeneratingConfig:
    pass


class BasicGenerator(abc.ABC):
    def __init__(
        self,
        include_path: str,
        source_path: str,
    ):
        self._include_path: str = include_path
        self._source_path: str = source_path

    @abc.abstractmethod
    def need_to_generate(self, node: clang.cindex.Cursor) -> bool:
        pass

    @abc.abstractmethod
    def generate(
        self,
        node: clang.cindex.Cursor,
        file_info: FileInfo,
        generating_config: GeneratingConfig,
    ):
        pass

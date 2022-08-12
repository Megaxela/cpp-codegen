import abc

import clang.cindex


class BasicGenerator(abc.ABC):
    def __init__(
        self,
        include_path: str,
        source_path: str,
    ):
        self._include_path: str = include_path
        self._source_path: str = source_path

    @abc.abstractmethod()
    def need_to_generate(node: clang.cindex.Cursor) -> bool:
        pass

    @abc.abstractmethod()
    def generate(node: clang.cindex.Cursor):
        pass

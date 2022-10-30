import dataclasses
import typing as tp


@dataclasses.dataclass()
class EnumValueConfiguration:
    enum_value_name: str
    fallback_value: str
    conversion_values: tp.Dict[str, str]


@dataclasses.dataclass()
class EnumConfiguration:
    typename: str
    namespace: tp.List[str]

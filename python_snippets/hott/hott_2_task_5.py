from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast
from xml.etree import ElementTree

from core.base_types import Path
from core.univalence import Equivalence, Univalence, create_type_equivalence

# frist task - stack and  list equivalence


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def to_list(self) -> list[T]:
        return self._items.copy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stack):
            return False
        return self._items == cast(Stack[object], other)._items


def stack_to_list[T](stack: Stack[T]) -> list[T]:
    return stack.to_list()


def list_to_stack[T](items: list[T]) -> Stack[T]:
    stack: Stack[T] = Stack()
    for item in items:
        stack.push(item)
    return stack


stack_list_equivalence = create_type_equivalence(
    Stack,
    list,
    stack_to_list,
    list_to_stack,
)


# second task - transport between temp scales


@dataclass(frozen=True)
class Celsius:
    value: float


@dataclass(frozen=True)
class Fahrenheit:
    value: float


def celsius_to_fahrenheit(temperature: Celsius) -> Fahrenheit:
    return Fahrenheit(temperature.value * 9 / 5 + 32)


def fahrenheit_to_celsius(temperature: Fahrenheit) -> Celsius:
    return Celsius((temperature.value - 32) * 5 / 9)


celsius_fahrenheit_equivalence = create_type_equivalence(
    Celsius,
    Fahrenheit,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
)

fahrenheit_celsius_equivalence = create_type_equivalence(
    Fahrenheit,
    Celsius,
    fahrenheit_to_celsius,
    celsius_to_fahrenheit,
)


def transport_celsius_to_fahrenheit(temperature: Celsius) -> Fahrenheit:
    return Univalence.transport_uni_axi(
        Celsius,
        Fahrenheit,
        celsius_fahrenheit_equivalence,
        temperature,
    )


def transport_fahrenheit_to_celsius(temperature: Fahrenheit) -> Celsius:
    return Univalence.transport_uni_axi(
        Fahrenheit,
        Celsius,
        fahrenheit_celsius_equivalence,
        temperature,
    )


# third task - composition of data format equivalences


@dataclass(frozen=True)
class JSONData:
    data: str


@dataclass(frozen=True)
class XMLData:
    data: str


@dataclass
class PythonDict:
    data: dict[str, Any]


def json_to_python_dict(value: JSONData) -> PythonDict:
    parsed = json.loads(value.data)
    if not isinstance(parsed, dict):
        raise TypeError("JSONData must contain a JSON object")
    return PythonDict(cast(dict[str, Any], parsed))


def python_dict_to_json(value: PythonDict) -> JSONData:
    return JSONData(json.dumps(value.data, ensure_ascii=False))


def _encode_xml_value(element: ElementTree.Element, value: Any) -> None:
    if isinstance(value, dict):
        element.set("type", "dict")
        mapping = cast(dict[str, Any], value)
        for key, nested_value in mapping.items():
            child = ElementTree.SubElement(element, key)
            _encode_xml_value(child, nested_value)
        return

    if isinstance(value, list):
        element.set("type", "list")
        sequence = cast(list[Any], value)
        for nested_value in sequence:
            child = ElementTree.SubElement(element, "item")
            _encode_xml_value(child, nested_value)
        return

    if value is None:
        element.set("type", "null")
        return

    if isinstance(value, str):
        element.text = value
        try:
            json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return
        element.set("type", "str")
        return

    if isinstance(value, (bool, int, float)):
        element.text = json.dumps(value)
        return

    raise TypeError(f"Unsupported value for XML conversion: {type(value).__name__}")


def _decode_xml_value(element: ElementTree.Element) -> Any:
    value_type = element.get("type")

    if value_type == "dict":
        return {child.tag: _decode_xml_value(child) for child in element}

    if value_type == "list":
        return [_decode_xml_value(child) for child in element]

    if value_type == "null":
        return None

    text = element.text or ""
    if value_type == "str":
        return text

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def python_dict_to_xml(value: PythonDict) -> XMLData:
    root = ElementTree.Element("person")
    for key, item in value.data.items():
        child = ElementTree.SubElement(root, key)
        _encode_xml_value(child, item)
    return XMLData(ElementTree.tostring(root, encoding="unicode"))


def xml_to_python_dict(value: XMLData) -> PythonDict:
    root = ElementTree.fromstring(value.data)
    return PythonDict({child.tag: _decode_xml_value(child) for child in root})


json_python_dict_equivalence = create_type_equivalence(
    JSONData,
    PythonDict,
    json_to_python_dict,
    python_dict_to_json,
)

python_dict_xml_equivalence = create_type_equivalence(
    PythonDict,
    XMLData,
    python_dict_to_xml,
    xml_to_python_dict,
)

json_xml_equivalence: Equivalence[JSONData, XMLData] = (
    json_python_dict_equivalence.compose(python_dict_xml_equivalence)
)


def compose_format_paths() -> tuple[Path[type], Path[type]]:
    json_dict_path = Univalence.uni_axi(
        JSONData,
        PythonDict,
        json_python_dict_equivalence,
    )
    dict_xml_path = Univalence.uni_axi(
        PythonDict,
        XMLData,
        python_dict_xml_equivalence,
    )
    path_composition = json_dict_path.trans(dict_xml_path)
    equivalence_composition_path = Univalence.uni_axi(
        JSONData,
        XMLData,
        json_xml_equivalence,
    )
    return path_composition, equivalence_composition_path


### some tests


def test_stack_round_trip_returns_original_stack() -> None:
    original = Stack[int]()
    for item in (1, 2, 3):
        original.push(item)

    as_list = stack_list_equivalence.function(original)
    restored = stack_list_equivalence.inverse.backward(as_list)

    assert restored == original
    assert restored is not original


def test_stack_conversion_preserves_order() -> None:
    stack = list_to_stack(["first", "second", "third"])

    assert stack_to_list(stack) == ["first", "second", "third"]
    assert [stack.pop(), stack.pop(), stack.pop()] == ["third", "second", "first"]


def test_empty_stack_and_empty_list_are_equivalent() -> None:
    stack = Stack[object]()

    assert stack_list_equivalence.function(stack) == []
    assert stack_list_equivalence.inverse.backward([]) == stack


# Task 2. Transport along univalence paths


@pytest.mark.parametrize("value", [-40.0, 0.0, 37.0, 100.0])
def test_celsius_fahrenheit_round_trip(value: float) -> None:
    original = Celsius(value)

    fahrenheit = transport_celsius_to_fahrenheit(original)
    restored = transport_fahrenheit_to_celsius(fahrenheit)

    assert restored.value == pytest.approx(original.value)


@pytest.mark.parametrize("value", [-40.0, 32.0, 98.6, 212.0])
def test_fahrenheit_celsius_round_trip(value: float) -> None:
    original = Fahrenheit(value)

    celsius = Univalence.transport_uni_axi(
        Fahrenheit,
        Celsius,
        fahrenheit_celsius_equivalence,
        original,
    )
    restored = Univalence.transport_uni_axi(
        Celsius,
        Fahrenheit,
        celsius_fahrenheit_equivalence,
        celsius,
    )

    assert restored.value == pytest.approx(original.value)


def test_transport_preserves_water_freezing_point() -> None:
    freezing = transport_celsius_to_fahrenheit(Celsius(0.0))

    assert freezing.value == pytest.approx(32.0)


def test_transport_preserves_water_boiling_point() -> None:
    boiling = transport_celsius_to_fahrenheit(Celsius(100.0))

    assert boiling.value == pytest.approx(212.0)


# Task 3. Composition of equivalences


def test_direct_json_to_xml_matches_conversion_via_dictionary() -> None:
    source = JSONData('{"name": "John", "age": 30}')

    direct = json_xml_equivalence.function(source)
    via_dictionary = python_dict_xml_equivalence.function(
        json_python_dict_equivalence.function(source)
    )

    assert direct == via_dictionary
    assert direct == XMLData("<person><name>John</name><age>30</age></person>")


def test_all_format_conversions_preserve_data_structure() -> None:
    structure = {
        "name": "John",
        "age": 30,
        "active": True,
        "address": {"city": "London"},
        "scores": [10, 20],
    }
    source = JSONData(json.dumps(structure))

    as_dictionary = json_python_dict_equivalence.function(source)
    as_xml = python_dict_xml_equivalence.function(as_dictionary)
    dictionary_restored = python_dict_xml_equivalence.inverse.backward(as_xml)
    json_restored = json_xml_equivalence.inverse.backward(as_xml)

    assert as_dictionary == PythonDict(structure)
    assert dictionary_restored == PythonDict(structure)
    assert json.loads(json_restored.data) == structure


def test_composition_of_paths_matches_composition_of_equivalences() -> None:
    path_composition, equivalence_composition_path = compose_format_paths()

    assert isinstance(path_composition, Path)
    assert path_composition.start is JSONData
    assert path_composition.end is XMLData
    assert equivalence_composition_path.start is JSONData
    assert equivalence_composition_path.end is XMLData
    assert path_composition == equivalence_composition_path


def test_composed_equivalence_round_trip() -> None:
    source = JSONData('{"name": "John", "age": 30}')

    xml = json_xml_equivalence.function(source)
    restored = json_xml_equivalence.inverse.backward(xml)

    assert json.loads(restored.data) == json.loads(source.data)


def test_sample_xml_can_be_converted_back_to_dictionary() -> None:
    xml = python_dict_to_xml(PythonDict({"name": "John", "age": 30}))

    assert xml == XMLData("<person><name>John</name><age>30</age></person>")
    assert python_dict_xml_equivalence.inverse.backward(xml) == PythonDict(
        {"name": "John", "age": 30}
    )

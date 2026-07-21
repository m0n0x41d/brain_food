from collections.abc import Callable, Mapping
from dataclasses import dataclass

from core.universes import Level, Universe

# task 1. pc configurator


@dataclass(frozen=True)
class CPU:
    socket: str
    ram_type: str


@dataclass(frozen=True)
class RAM:
    ram_type: str
    size_gb: int


@dataclass(frozen=True)
class GPU:
    minimum_ram_gb: int


@dataclass(frozen=True)
class PCConfiguration:
    cpu: CPU
    ram: RAM
    gpu: GPU


@dataclass(frozen=True)
class BuildTemplate:
    cpu_socket: str
    minimum_ram_gb: int


def is_components_are_compatible(
    template: BuildTemplate,
    cpu: CPU,
    ram: RAM,
    gpu: GPU,
) -> bool:
    return (
        cpu.socket == template.cpu_socket
        and cpu.ram_type == ram.ram_type
        and ram.size_gb >= template.minimum_ram_gb
        and ram.size_gb >= gpu.minimum_ram_gb
    )


def create_configuration(
    template: BuildTemplate,
    cpu: CPU,
    ram: RAM,
    gpu: GPU,
) -> PCConfiguration:
    compatible = is_components_are_compatible(template, cpu, ram, gpu)
    if not compatible:
        raise ValueError("Incompatible components")

    return PCConfiguration(cpu, ram, gpu)


def configure_pc() -> PCConfiguration:
    components: Universe[CPU | RAM | GPU] = Universe(Level(0))
    configs: Universe[PCConfiguration] = Universe(Level(1))
    templates: Universe[BuildTemplate] = Universe(Level(2))

    cpu = CPU("AM5", "DDR5")
    ram = RAM("DDR5", 32)
    gpu = GPU(16)
    template = BuildTemplate("AM5", 16)

    levels = (
        components.level.value,
        configs.level.value,
        templates.level.value,
    )
    assert levels == (0, 1, 2)
    assert is_components_are_compatible(template, cpu, ram, gpu)

    configuration = create_configuration(template, cpu, ram, gpu)
    incompatible_ram = RAM("DDR4", 8)

    assert not is_components_are_compatible(
        template,
        cpu,
        incompatible_ram,
        gpu,
    )
    assert not isinstance(template, PCConfiguration)

    return configuration


# task 2. docs versioning


@dataclass(frozen=True)
class PublicDocument:
    text: str
    version: int


@dataclass(frozen=True)
class InternalDocument:
    text: str
    version: int


@dataclass(frozen=True)
class SecretDocument:
    text: str
    version: int


def promote_public(document: PublicDocument) -> InternalDocument:
    return InternalDocument(document.text, document.version + 1)


def promote_internal(document: InternalDocument) -> SecretDocument:
    return SecretDocument(document.text, document.version + 1)


def demote_secret(document: SecretDocument) -> InternalDocument:
    return InternalDocument(document.text, document.version + 1)


def demote_internal(document: InternalDocument) -> PublicDocument:
    return PublicDocument(document.text, document.version + 1)


def can_read(
    reader_universe: Universe,
    document_universe: Universe,
) -> bool:
    reader_level = reader_universe.level.value
    document_level = document_universe.level.value
    return reader_level >= document_level


def document_system() -> tuple[
    PublicDocument,
    InternalDocument,
    SecretDocument,
]:
    public_universe: Universe[PublicDocument] = Universe(Level(0))
    internal_universe: Universe[InternalDocument] = Universe(Level(1))
    secret_universe: Universe[SecretDocument] = Universe(Level(2))

    public = PublicDocument("Universes", 1)
    internal = promote_public(public)
    secret = promote_internal(internal)

    assert can_read(public_universe, public_universe)
    assert not can_read(public_universe, internal_universe)
    assert not can_read(internal_universe, secret_universe)
    assert can_read(secret_universe, public_universe)

    internal_again = demote_secret(secret)
    public_again = demote_internal(internal_again)

    assert public_again.version == 5

    return public, internal, secret


# task 3. Forms validator


@dataclass(frozen=True)
class BasicType:
    name: str
    validate: Callable[[object], bool]


@dataclass(frozen=True)
class CompositeType:
    name: str
    fields: Mapping[str, BasicType]


@dataclass(frozen=True)
class FormType:
    name: str
    fields: Mapping[str, BasicType | CompositeType]


def extend_composite(
    base: CompositeType,
    name: str,
    extra_fields: Mapping[str, BasicType],
) -> CompositeType:
    fields = dict(base.fields)
    fields.update(extra_fields)
    return CompositeType(name, fields)


def is_valid_form_field(field: object) -> bool:
    if isinstance(field, BasicType):
        return True

    if isinstance(field, CompositeType):
        return all(
            isinstance(nested_field, BasicType)
            for nested_field in field.fields.values()
        )

    return False


def is_valid_form_schema(form: FormType) -> bool:
    return all(is_valid_form_field(field) for field in form.fields.values())


def validate_field(field: BasicType | CompositeType, value: object) -> bool:
    if isinstance(field, BasicType):
        return field.validate(value)

    if not isinstance(value, Mapping):
        return False

    return all(
        name in value and basic.validate(value[name])
        for name, basic in field.fields.items()
    )


def validate_form(form: FormType, data: Mapping[str, object]) -> bool:
    if not is_valid_form_schema(form):
        return False

    return all(
        name in data and validate_field(field, data[name])
        for name, field in form.fields.items()
    )


def form_validator() -> tuple[FormType, FormType]:
    basic_types: Universe[BasicType] = Universe(Level(0))
    composite_types: Universe[CompositeType] = Universe(Level(1))
    forms: Universe[FormType] = Universe(Level(2))

    string = BasicType("string", lambda value: isinstance(value, str))
    number = BasicType("number", lambda value: isinstance(value, (int, float)))

    address = CompositeType("address", {"city": string, "street": string})
    contact = CompositeType("contact", {"email": string})
    contact_with_phone = extend_composite(
        contact,
        "contact_with_phone",
        {"phone": string},
    )

    questionnaire = FormType(
        "questionnaire",
        {"name": string, "address": address},
    )
    application = FormType(
        "application",
        {
            "name": string,
            "age": number,
            "address": address,
            "contact": contact_with_phone,
        },
    )

    valid_data = {
        "name": "Ada",
        "age": 30,
        "address": {"city": "Yerevan", "street": "Abovyan"},
        "contact": {"email": "ada@example.test", "phone": "+374"},
    }
    invalid_data = valid_data | {"address": {"city": "Yerevan"}}

    levels = (
        basic_types.level.value,
        composite_types.level.value,
        forms.level.value,
    )
    assert levels == (0, 1, 2)
    assert questionnaire.fields["address"] is application.fields["address"]
    assert "phone" in contact_with_phone.fields
    assert all(is_valid_form_schema(form) for form in (questionnaire, application))
    assert validate_form(application, valid_data)
    assert not validate_form(application, invalid_data)

    return questionnaire, application

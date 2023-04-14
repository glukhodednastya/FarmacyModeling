from dataclasses import fields


def get_dataclass_field_names(cls):
    return [i.name for i in fields(cls)]

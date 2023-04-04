from datetime import date
from app.modeling.utils import get_dataclass_field_names


class BaseGenerate:

    def __new__(cls, *args, **kwargs):
        attrs = get_dataclass_field_names(cls.model)
        for attr in attrs:
            if attr not in kwargs:
                _attr = getattr(cls, attr)
                if callable(_attr):
                    kwargs[attr] = _attr()
                else:
                    kwargs[attr] = _attr

        return cls.model(**kwargs)


class ModelingConfig:
    cur_date: date = date.today()
    couriers_amount: int
    margin: float = 0.1
    expiration_discount_days: int = 30
    expiration_discount: float = 0.5
    medicines: list = []
    code_to_medicine: dict = {}
    supply_size: int = 50
    budget: float = 100000
    start_budget: float = 100000
    courier_salary: float
    courier_salary_day: int = 25
    date_to: date = None
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

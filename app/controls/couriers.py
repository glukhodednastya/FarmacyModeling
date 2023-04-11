from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.models.courier import Courier
from app.controls.base import BaseControl


class CouriersControl(BaseControl):

    couriers = []

    def __init__(self, couriers: list[Courier] = None):
        if couriers is not None:
            self.couriers = couriers

    def pay_salary(self):
        ModelingConfig().budget -= ModelingConfig().courier_salary * len(self.couriers)
        Logger().add('Выплачена зарплата курьерам', loss=ModelingConfig().courier_salary * len(self.couriers))

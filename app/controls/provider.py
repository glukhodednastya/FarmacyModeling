from collections import defaultdict
from datetime import date, timedelta
from random import randint

from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.models.medicine import MedicineItem
from app.controls.base import BaseControl


class ProviderControl(BaseControl):

    supply_queue = defaultdict(list)  # type: dict[date, list[MedicineItem]]
    requested_items = defaultdict(int)  # type: dict[str, int]

    def get_supply(self, date_: date) -> list[MedicineItem]:
        return self.supply_queue.get(date_, [])

    def create_supply(self, code):
        supply_date = ModelingConfig().cur_date + timedelta(randint(1, 10))
        medicine = ModelingConfig().code_to_medicine[code]
        self.supply_queue[supply_date].extend([
            MedicineItem(
                medicine=medicine,
                expires_at=ModelingConfig().cur_date + timedelta(randint(10, 20)),
            )
            for _ in range(ModelingConfig().supply_size)
        ])

        Logger().add(
            f'Заказан прерапат {medicine.name} '
            f'на сумму {medicine.retail_price * ModelingConfig().supply_size} рублей. '
            f'Заказ прибудет на склад {supply_date.strftime("%d.%m.%Y")}',
            loss=medicine.retail_price * ModelingConfig().supply_size,
        )

    def request(self, medicines: dict[str, int]):
        for code, amount in medicines.items():
            self.requested_items[code] += amount
            if self.requested_items[code] > 0:
                self.create_supply(code)
                self.requested_items[code] -= ModelingConfig().supply_size
                ModelingConfig().budget -= (
                    ModelingConfig().supply_size * ModelingConfig().code_to_medicine[code].retail_price
                )

    def reset(self):
        self.supply_queue = defaultdict(list)
        self.requested_items = defaultdict(int)

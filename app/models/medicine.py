from dataclasses import dataclass
from datetime import date, timedelta
from functools import reduce

from app.exceptions import MedicineItemExpiredError
from app.modeling.config import ModelingConfig
from app.models.utils import BarcodeGenerator


@dataclass
class Medicine:
    name: str
    code: str
    retail_price: float
    medication_size: int
    group: str = ''
    type: str = ''


@dataclass
class MedicineItem:
    medicine: Medicine
    expires_at: date

    def __post_init__(self):
        self.barcode = BarcodeGenerator.generate(self)

    @property
    def price(self):
        if ModelingConfig().cur_date > self.expires_at:
            raise MedicineItemExpiredError(self, ModelingConfig().cur_date)
        if ModelingConfig().cur_date + timedelta(ModelingConfig().discount_days) >= self.expires_at:
            return reduce(
                lambda x, y: x * y,
                [
                    self.medicine.retail_price,
                    (1 - ModelingConfig().discount),
                    1 + ModelingConfig().margin,
                ],
                1,
            )

        return self.medicine.retail_price * (1 + ModelingConfig().margin)

    def __str__(self):
        return f'{self.medicine.name} [{self.barcode}]'

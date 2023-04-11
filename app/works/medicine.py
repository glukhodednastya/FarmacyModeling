from random import randint
from datetime import date, timedelta

from app.models.medicine import MedicineItem

from app.factories.base import BaseWork


class MedicineItemWork(BaseWork):
    model = MedicineItem

    medication_size = 100
    group = ''
    type = ''
    retail_price = (lambda: float(randint(100, 500)))
    expires_at = (lambda: date.today() + timedelta(randint(5, 20)))

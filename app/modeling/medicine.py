from random import randint
from datetime import date, timedelta

from app.models.medicine import MedicineItem
from app.modeling.config import BaseGenerate


class MedicineItemGenerate(BaseGenerate):
    model = MedicineItem
    portion_size = 50
    group = ''
    type = ''
    retail_price = (lambda: float(randint(100, 500)))
    expires_at = (lambda: date.today() + timedelta(randint(5, 20)))

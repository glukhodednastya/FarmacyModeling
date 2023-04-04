from random import randint

from app.models.customer import Customer
from app.modeling.config import BaseGenerate

FIRST_NAMES = [
    'Денис',
    'Александр',
    'Иван',
    'Алексей',
    'Петр'
]

SECOND_NAMES = [
    'Сидоров',
    'Иванов',
    'Петров',
    'Васильев',
    'Сергеев'
]


class CustomerGenerate(BaseGenerate):
    model = Customer
    first_name = (lambda: FIRST_NAMES[randint(0, len(FIRST_NAMES) - 1)])
    last_name = (lambda: SECOND_NAMES[randint(0, len(SECOND_NAMES) - 1)])
    phone = '+78005553535'
    address = 'Moscow'
    card = None

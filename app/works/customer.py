from random import randint

from app.models.customer import Customer
from app.works.base import BaseWork

FIRST_NAMES = [
    'Денис',
    'Антон',
    'Александр',
    'Павел',
    'Артем'
]

SECOND_NAMES = [
    'Петров',
    'Иванов',
    'Сергеев',
    'Антонов',
    'Денисов'
]


class CustomerWork(BaseWork):
    model = Customer
    first_name = (lambda: FIRST_NAMES[randint(0, len(FIRST_NAMES) - 1)])
    last_name = (lambda: SECOND_NAMES[randint(0, len(SECOND_NAMES) - 1)])
    phone_number = '+7905467283'
    address = 'Moscow'
    card = None

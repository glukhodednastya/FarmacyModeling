from datetime import date, timedelta

import eel

from app.controls.orders import OrdersControl
from app.controls.provider import ProviderControl
from app.controls.stock import StockControl
from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.modeling.manager import ModelingManager
from app.models.courier import Courier
from app.models.medicine import Medicine

mngr: ModelingManager or None = None


def _clean_medicines(raw_medicines: list[dict]):
    return [
        Medicine(
            name=med['name'],
            code=med['code'],
            retail_price=float(med['retail_price']),
            medication_size=int(med['medication_size'])
        )
        for med in raw_medicines
    ]


def clean(data):

    cleaned_data = {}
    invalid_field_names = []

    cleaners = {
        'margin': (lambda x: float(x) / 100),
        'budget': (lambda x: float(x)),
        'courier_salary': float,
        'discount': (lambda x: float(x) / 100),
        'supply_size': int,
        'couriers_amount': int,
        'working_hours': int,
        'date_from': (lambda x: date.fromisoformat(x)),
        'date_to': (lambda x: date.fromisoformat(x)),
        'medicines': _clean_medicines,
    }

    for field_name, cleaner in cleaners.items():
        try:
            cleaned_data[field_name] = cleaner(data[field_name])
        except Exception:
            invalid_field_names.append(field_name)

    positive_fields = [
        'margin',
        'budget',
        'courier_salary',
        'discount',
        'supply_size',
        'couriers_amount',
        'working_hours',
    ]
    for field_name in positive_fields:
        if field_name not in invalid_field_names and cleaned_data[field_name] <= 0:
            invalid_field_names.append(field_name)

    return cleaned_data, invalid_field_names


@eel.expose
def get_next_day(data=None):
    global mngr

    if mngr is None:
        cleaned_data, errors = clean(data)

        if errors:
            eel.highlightErrors(errors)
            return

        cleaned_data['couriers'] = [
            Courier(
                name=f'Курьер',
                working_hours=timedelta(hours=cleaned_data['working_hours']),
            )
        ]

        mngr = ModelingManager(**cleaned_data)
        ModelingConfig().cur_date = cleaned_data['date_from']

    mngr.run_day()
    eel.showResults(
        ModelingConfig().budget - ModelingConfig().start_budget,
        Logger().get_delivered_orders_amount(),
        Logger().get_average_waiting_time(),
        StockControl().total_price,
        Logger().last_day_log,
        Logger().get_average_couriers_load(),
        Logger().get_money_lost_from_utilization(),
    )


@eel.expose
def run_until_complete():
    mngr.run(
        date_from=ModelingConfig().cur_date,
        date_to=ModelingConfig().date_to,
        progress_callback=eel.showProgress,
    )
    eel.showResults(
        ModelingConfig().budget - ModelingConfig().start_budget,
        Logger().get_delivered_orders_amount(),
        Logger().get_average_waiting_time(),
        StockControl().total_price,
        Logger().last_day_log,
        Logger().get_average_couriers_load(),
        Logger().get_money_lost_from_utilization(),
    )


@eel.expose
def start_again():
    global mngr

    StockControl().reset()
    OrdersControl().reset()
    Logger().reset()
    ProviderControl().reset()
    ModelingConfig().budget = ModelingConfig().start_budget

    mngr = None


def run():
    eel.init('app/interface/web')
    eel.start('index.html', mode='default')

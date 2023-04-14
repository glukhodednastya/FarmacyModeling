from datetime import date, datetime, time, timedelta
from random import randint
from typing import Callable

from app.controls.couriers import CouriersControl
from app.controls.orders import OrdersControl
from app.controls.provider import ProviderControl
from app.controls.stock import StockControl
from app.exceptions import BadModelingDateRange
from app.modeling.logger import Logger
from app.modeling.config import ModelingConfig
from app.modeling.utils import shuffle, random_split
from app.works.customer import CustomerWork
from app.models.medicine import Medicine
from app.models.courier import Courier
from app.models.order import Order, OrderedItem


class ModelingManager:
    orders_ctl = OrdersControl()
    stock_ctl = StockControl()
    logs = []

    def __init__(
        self,
        medicines: list[Medicine],
        couriers: list[Courier],
        margin: float,
        date_to: date,
        courier_salary: float,
        discount_days: int = 30,
        discount: float = 0.5,
        budget: float = 0,
        supply_size: int = 100,
        **kwargs,
    ):
        exp_conf = ModelingConfig()
        exp_conf.medicines = medicines
        for med in medicines:
            exp_conf.code_to_medicine[med.code] = med
        exp_conf.margin = margin
        exp_conf.budget = budget
        exp_conf.start_budget = budget
        exp_conf.courier_salary = courier_salary
        exp_conf.discount_days = discount_days
        exp_conf.discount = discount
        exp_conf.cur_date = date.today()
        exp_conf.supply_size = supply_size
        exp_conf.date_to = date_to

        CouriersControl().couriers = couriers
        Logger().reset()
        StockControl().reset()
        ProviderControl().reset()

    def run(
        self,
        date_from,
        date_to,
        progress_callback: Callable = (lambda x: print(f'Progress: {x}%')),
    ):
        if date_from > date_to:
            raise BadModelingDateRange()

        ModelingConfig().cur_date = date_from
        period_len = (date_to - date_from + timedelta(1)).days

        for i in range(period_len):
            progress_callback(int(i * 100 / period_len))
            self.run_day()

    def run_day(self):
        StockControl().utilize()
        StockControl().accept_items_from_provider()
        OrdersControl().distribute_orders_to_couriers()

        if ModelingConfig().cur_date.day == ModelingConfig().courier_salary_day:
            CouriersControl().pay_salary()

        self.create_new_orders()
        OrdersControl().make_new_requests()
        if ModelingConfig().cur_date.day <= ModelingConfig().date_to.day-1:
            ModelingConfig().cur_date += timedelta(1)

    def create_new_orders(self):
        max_delivered_minutes = max(
            [
                int(courier.working_hours.seconds / 60)
                for courier in CouriersControl().couriers
            ],
        )

        new_ordered_meds = []
        for med in ModelingConfig().medicines:
            med: Medicine
            new_ordered_meds_amount = int(randint(50, 120))
            new_ordered_meds.extend([med for _ in range(new_ordered_meds_amount)])

        shuffle(new_ordered_meds)
        customers_amount = int(len(new_ordered_meds) / randint(3, 6))
        split_orders = random_split(new_ordered_meds, customers_amount)

        new_orders = []
        new_ordered_items = []
        for raw_order in split_orders:
            order = Order(
                delivered=timedelta(minutes=randint(15, max_delivered_minutes)),
                order_date=datetime.combine(ModelingConfig().cur_date, time(hour=randint(10, 22))),
                total_price=0,
                customer=CustomerWork(),
            )
            for med in raw_order:
                new_ordered_items.append(OrderedItem(med, order))
                order.total_price += med.retail_price * (1 + ModelingConfig().margin)

            Logger().add(
                f'{order.customer.first_name} {order.customer.last_name}'
                f' заказал {", ".join(med.name for med in raw_order)} на сумму {order.total_price:.2f} рублей',
                profit=order.total_price,
            )
            ModelingConfig().budget += order.total_price

            new_orders.append(order)

        OrdersControl().orders_queue.extend(new_orders)
        OrdersControl().ordered_items.extend(new_ordered_items)

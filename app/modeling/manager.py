from datetime import date, datetime, time, timedelta
from random import randint
from typing import Callable
import yaml

from app.controls.couriers import CouriersControl
from app.controls.orders import OrdersControl
from app.controls.provider import ProviderControl
from app.controls.storage import StorageControl
from app.modeling.logger import Logger
from app.modeling.customer import CustomerGenerate
from app.modeling.config import ModelingConfig
from app.modeling.utils import shuffle, random_split
from app.models.medicine import Medicine
from app.models.courier import Courier
from app.models.order import Order, OrderedItem


class ModelingManager:

    orders_ctl = OrdersControl()
    storage_ctl = StorageControl()
    logs = []

    def __init__(
        self,
        medicines: list[Medicine],
        couriers: list[Courier],
        margin: float,
        date_to: date,
        courier_salary: float,
        expiration_discount_days: int = 30,
        expiration_discount: float = 0.5,
        budget: float = 0,
        supply_size: int = 50,
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
        exp_conf.expiration_discount_days = expiration_discount_days
        exp_conf.expiration_discount = expiration_discount
        exp_conf.cur_date = date.today()
        exp_conf.supply_size = supply_size
        exp_conf.date_to = date_to

        CouriersControl().couriers = couriers
        Logger().reset()
        StorageControl().reset()
        ProviderControl().reset()

    @classmethod
    def from_yaml(
        cls,
        filename: str,
        margin: float = None,
        expiration_discount_days: int = None,
        expiration_discount: float = None,
    ):
        with open(filename, 'r') as f:
            try:
                config_dict = yaml.safe_load(f)
            except yaml.YAMLError:
                raise

        medicines = [
            Medicine(name=med_name, **med_params)
            for med_name, med_params in config_dict.get('medicines', {}).items()
        ]
        couriers = [
            Courier(name=courier_name, working_hours=timedelta(hours=courier_params['working_hours']))
            for courier_name, courier_params in config_dict.get('couriers', {}).items()
        ]
        margin = config_dict.get('margin', margin)
        date_to = config_dict.get('date_to')
        budget = config_dict.get('budget', 0)
        courier_salary = config_dict.get('courier_salary', 0)
        supply_size = config_dict.get('supply_size', 100)
        expiration_discount_days = config_dict.get(
            'expiration_discount_days',
            expiration_discount_days,
        )
        expiration_discount = config_dict.get(
            'expiration_discount',
            expiration_discount,
        )

        return cls(
            medicines=medicines,
            couriers=couriers,
            margin=margin,
            expiration_discount_days=expiration_discount_days,
            expiration_discount=expiration_discount,
            budget=budget,
            supply_size=supply_size,
            courier_salary=courier_salary,
            date_to=date_to,
        )

    def run(
        self,
        date_from: date,
        date_to: date
    ):
        ModelingConfig().cur_date = date_from
        period_len = (date_to - date_from).days
        for i in range(period_len):
            self.run_day()

    def run_day(self):
        StorageControl().utilize_expired()
        StorageControl().accept_items_from_provider()
        OrdersControl().distribute_orders_to_couriers()

        if ModelingConfig().cur_date.day == ModelingConfig().courier_salary_day:
            CouriersControl().pay_salary()

        self.create_new_orders()
        OrdersControl().make_new_requests()
        ModelingConfig().cur_date += timedelta(1)

    def create_new_orders(self):
        max_delivery_time_minutes = max(
            [int(courier.working_hours.seconds / 60)
             for courier in CouriersControl().couriers])

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
                delivery_time=timedelta(minutes=randint(15, max_delivery_time_minutes)),
                ordered_at=datetime.combine(ModelingConfig().cur_date, time(hour=randint(10, 22))),
                total_price=0,
                customer=CustomerGenerate(),
            )
            for med in raw_order:
                new_ordered_items.append(OrderedItem(med, order))
                order.total_price += med.retail_price * (1 + ModelingConfig().margin)

            Logger().add(
                f'{order.customer.first_name} {order.customer.last_name}'
                f'. Заказ: {", ".join(med.name for med in raw_order)}. Сумма заказа: {order.total_price:.2f} рублей',
                profit=order.total_price,
            )
            ModelingConfig().budget += order.total_price
            new_orders.append(order)

        OrdersControl().orders_queue.extend(new_orders)
        OrdersControl().ordered_items.extend(new_ordered_items)

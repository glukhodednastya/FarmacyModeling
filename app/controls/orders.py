from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.models.medicine import MedicineItem
from app.models.order import Order, OrderedItem
from app.controls.provider import ProviderControl
from app.controls.base import BaseControl
from app.controls.couriers import CouriersControl
from app.controls.storage import StorageControl


class OrdersControl(BaseControl):
    orders_queue: list[Order] = []
    ordered_items: list[OrderedItem] = []

    def distribute_orders_to_couriers(self):
        couriers = CouriersControl().couriers
        for courier in couriers:
            courier_time_left = courier.working_hours
            orders_to_delete = []
            profit_by_courier = 0
            for order in self.orders_queue:
                if self.order_in_stock(order) and courier_time_left >= order.delivery_time:
                    courier_time_left -= order.delivery_time
                    items_to_deliver = self.pop_items_to_deliver(order)
                    profit = sum(i.price for i in items_to_deliver)
                    profit_by_courier += profit
                    self.ordered_items = [item for item in self.ordered_items if item.order != order]
                    orders_to_delete.append(order)

            if profit_by_courier:
                delivery_time = int((courier.working_hours - courier_time_left).seconds / 3600)
                Logger().add(
                    f'Курьер доставит сегодня {len(orders_to_delete)} заказа на '
                    f'сумму {profit_by_courier:.2f} рублей. Это займет {delivery_time} часа.',
                )

            Logger().add(
                tag='courier_load',
                meta={'courier_load': (courier.working_hours - courier_time_left) / courier.working_hours},
                hidden=True,
            )

            for order in orders_to_delete:
                Logger().add(
                    '',
                    meta={'wait_time': (ModelingConfig().cur_date - order.ordered_at.date()).days},
                    hidden=True,
                )
                self.orders_queue.remove(order)

    def order_in_stock(self, order):
        ordered_items = self.get_ordered_items_by_order(order)
        storage = StorageControl()
        medicines_in_order = {}

        for item in ordered_items:
            code = item.medicine.code
            if code in medicines_in_order:
                medicines_in_order[code] += 1
            else:
                medicines_in_order[code] = 1

        for code in medicines_in_order:
            if storage.amount_of_medicine_in_stock(code) < medicines_in_order[code]:
                return False
        return True

    def get_ordered_items_by_order(self, order):
        return [item for item
                in self.ordered_items
                if item.order == order]

    def make_new_requests(self):
        storage = StorageControl()
        medicines_in_queue = {}
        medicines_to_request = {}
        for ordered_item in self.ordered_items:
            code = ordered_item.medicine.code
            if code in medicines_in_queue:
                medicines_in_queue[code] += 1
            else:
                medicines_in_queue[code] = 1

        for code in medicines_in_queue:
            medicines_in_stock = storage.amount_of_medicine_in_stock(code)
            if medicines_in_stock < medicines_in_queue[code]:
                medicines_to_request[code] = medicines_in_queue[code] - medicines_in_stock

        ProviderControl().request(medicines_to_request)

    def count_profit(self, order):
        return sum(
            item.item.price for item in self.ordered_items
            if item.order == order
        )

    def pop_items_to_deliver(self, order):
        storage = StorageControl()
        storage.utilize_expired()
        print('Expired items –', len([i for i in storage.items.values() if i.expires_at < ModelingConfig().cur_date]))
        return [storage.pop_by_code(item.medicine.code)
                for item in self.ordered_items
                if item.order == order]

    def reset(self):
        self.orders_queue = []
        self.ordered_items = []

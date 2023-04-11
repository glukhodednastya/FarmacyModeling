from app.controls.provider import ProviderControl
from app.controls.base import BaseControl
from app.controls.couriers import CouriersControl
from app.controls.stock import StockControl
from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.models.medicine import MedicineItem
from app.models.order import Order, OrderedItem, RegularOrderedMedicineItem


class OrdersControl(BaseControl):

    orders_queue: list[Order] = []
    ordered_items: list[OrderedItem] = []
    regular_ordered_items: list[RegularOrderedMedicineItem] = []

    def distribute_orders_to_couriers(self) -> None:
        couriers = CouriersControl().couriers
        for courier in couriers:
            courier_time_left = courier.working_hours
            orders_to_delete = []
            profit_by_courier = 0
            for order in self.orders_queue:
                if self.order_in_stock(order) and courier_time_left >= order.delivered:
                    courier_time_left -= order.delivered
                    items_to_deliver = self.pop_items_to_deliver(order)
                    profit = sum(i.price for i in items_to_deliver)
                    profit_by_courier += profit
                    self.ordered_items = [item for item in self.ordered_items if item.order != order]
                    orders_to_delete.append(order)

            if profit_by_courier:
                delivered = int((courier.working_hours - courier_time_left).seconds / 3600)
                Logger().add(
                    f'Курьер доставил {len(orders_to_delete)} заказа на '
                    f'сумму {profit_by_courier:.2f} рублей. Это заняло {delivered} часов.',
                )

            Logger().add(
                tag='courier_load',
                meta={'courier_load': (courier.working_hours - courier_time_left) / courier.working_hours},
                hidden=True,
            )

            for order in orders_to_delete:
                Logger().add(
                    '',
                    meta={'wait_time': (ModelingConfig().cur_date - order.order_date.date()).days},
                    hidden=True,
                )
                self.orders_queue.remove(order)  # процесс доставки/приемки не моделируется

    def order_in_stock(self, order: Order) -> bool:
        ordered_items = self.get_ordered_items_by_order(order)
        stock = StockControl()
        medicines_in_order = {}
        for item in ordered_items:
            code = item.medicine.code
            if code in medicines_in_order:
                medicines_in_order[code] += 1
            else:
                medicines_in_order[code] = 1
        for code in medicines_in_order:
            if stock.amount_in_stock(code) < medicines_in_order[code]:
                return False
        return True

    def get_ordered_items_by_order(self, order: Order) -> list[OrderedItem]:
        return [
            item for item
            in self.ordered_items
            if item.order == order
        ]


    def make_new_requests(self) -> None:
        """
        Смотрит, каких лекарств из очереди нет на складе и создает заказы поставщику
        """
        stock = StockControl()
        medicines_in_queue = {}  # {код_лекарства: количество}
        medicines_to_request = {}  # {код_лекарства: количество}
        for ordered_item in self.ordered_items:
            code = ordered_item.medicine.code
            if code in medicines_in_queue:
                medicines_in_queue[code] += 1
            else:
                medicines_in_queue[code] = 1

        for code in medicines_in_queue:
            medicines_in_stock = stock.amount_in_stock(code)
            if medicines_in_stock < medicines_in_queue[code]:
                medicines_to_request[code] = medicines_in_queue[code] - medicines_in_stock

        # поставщик отправляет товары партиями фиксированного размера,
        # поэтому новая партия формируется только если в прошлой не хватает
        # эта логика находится не в OrdersControl, а в ProviderControl
        ProviderControl().request(medicines_to_request)

    def count_profit(self, order: Order):
        return sum(
            item.item.price for item in self.ordered_items
            if item.order == order
        )

    def pop_items_to_deliver(self, order: Order) -> list[MedicineItem]:
        stock = StockControl()
        stock.utilize()
        print('Expired items –', len([i for i in stock.items.values() if i.expires_at < ModelingConfig().cur_date]))
        return [
            stock.pop_by_code(item.medicine.code)
            for item in self.ordered_items
            if item.order == order
        ]

    def reset(self):
        self.orders_queue = []
        self.ordered_items = []
        self.regular_ordered_items = []

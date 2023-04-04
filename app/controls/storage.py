from app.controls.base import BaseControl
from app.controls.provider import ProviderControl
from app.modeling.config import ModelingConfig
from app.modeling.logger import Logger
from app.models.medicine import MedicineItem, Medicine


class StorageControl(BaseControl):
    items = {}

    def add(self, items: list[MedicineItem]):
        for item in items:
            self.items[item.barcode] = item

    def pop(self, barcode):
        return self.items.pop(barcode)

    def pop_by_code(self, code):
        for barcode, item in self.items.items():
            if item.medicine.code == code:
                return self.pop(barcode)

    def item_in_stock(self, item):
        return item.barcode in self.items

    def medicine_in_stock(self, medicine):
        for item in self.items.values():
            if item.medicine == medicine:
                return item.barcode
        return None

    def amount_of_medicine_in_stock(self, medicine_code):
        return len([item for item
                    in self.items.values()
                    if item.medicine.code == medicine_code])

    def utilize_expired(self):
        not_expired = {}
        for barcode, item in self.items.items():
            if item.expires_at >= ModelingConfig().cur_date:
                not_expired[barcode] = item
        if len(self.items) != len(not_expired):
            print(
                f'Утилизация {len(self.items) - len(not_expired)} лекарств:',
                ', '.join([code for code in (set(self.items) - set(not_expired))]),
            )
            Logger().add(
                msg='Утилизация просроченнных лекарств',
                tag='utilization',
                loss=sum(self.items[code].medicine.retail_price for code in (set(self.items) - set(not_expired))),
            )

        self.items = not_expired

    def utilize_expired(self):
        not_expired = {}
        for barcode, item in self.items.items():
            if item.expires_at >= ModelingConfig().cur_date:
                not_expired[barcode] = item
        if len(self.items) != len(not_expired):
            print(
                f'utilized {len(self.items) - len(not_expired)} items:',
                ', '.join([code for code in (set(self.items) - set(not_expired))]),
            )
            Logger().add(
                msg='Утилизация просроченнных товаров',
                tag='utilization',
                loss=sum(self.items[code].medicine.retail_price for code in (set(self.items) - set(not_expired))),
            )

        self.items = not_expired

    def accept_items_from_provider(self):
        provider = ProviderControl()
        today = ModelingConfig().cur_date
        supply = provider.get_supply(today)
        self.add(supply)

        if supply:
            Logger().add(f'На склад поступило {len(supply)} лекарств.'
                         f' ({", ".join(set([med.medicine.name for med in supply]))})')

    @property
    def total_price(self):
        return sum(
            med.price for med in self.items.values()
            if med.expires_at >= ModelingConfig().cur_date
        )

    def reset(self):
        self.items = {}

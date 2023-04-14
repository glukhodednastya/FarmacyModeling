class DrugstoreError(Exception):
    pass


class MedicineItemExpiredError(DrugstoreError):
    def __init__(self, medicine_item, cur_date=None):
        super().__init__(
            f'Medicine {medicine_item} expired at {medicine_item.expires_at} (today is {cur_date})',
        )


class MedicineNotFound(DrugstoreError):
    def __init__(self, medicine_item):
        super().__init__(f'There is no {medicine_item} in the stock')


class BadModelingDateRange(DrugstoreError):
    def __init__(self):
        super().__init__('Date_to should be greater than date_from')

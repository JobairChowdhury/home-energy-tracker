# Appliance class - stores the details of one electrical appliance

MAX_WATTAGE = 10000
MAX_QUANTITY = 50

CATEGORIES = ["Cooling", "Lighting", "Kitchen", "Entertainment", "Laundry", "Other"]


class Appliance:

    def __init__(self, name, wattage, hours_per_day, quantity=1,
                 days_per_month=30, category="Other"):
        # check the values before saving them
        if not name or not str(name).strip():
            raise ValueError("Appliance name cannot be empty.")
        if not 0 < wattage <= MAX_WATTAGE:
            raise ValueError(f"Wattage must be between 1 and {MAX_WATTAGE} W.")
        if not 0 <= hours_per_day <= 24:
            raise ValueError("Hours per day must be between 0 and 24.")
        if not 1 <= quantity <= MAX_QUANTITY:
            raise ValueError(f"Quantity must be between 1 and {MAX_QUANTITY}.")
        if not 1 <= days_per_month <= 31:
            raise ValueError("Days per month must be between 1 and 31.")
        if category not in CATEGORIES:
            category = "Other"

        self.name = str(name).strip().title()
        self.wattage = float(wattage)
        self.hours_per_day = float(hours_per_day)
        self.quantity = int(quantity)
        self.days_per_month = int(days_per_month)
        self.category = category

    def daily_kwh(self):
        # kWh = watt x hours / 1000
        return (self.wattage * self.hours_per_day * self.quantity) / 1000

    def monthly_kwh(self):
        return self.daily_kwh() * self.days_per_month

    def to_dict(self):
        return {
            "name": self.name,
            "wattage": self.wattage,
            "hours_per_day": self.hours_per_day,
            "quantity": self.quantity,
            "days_per_month": self.days_per_month,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["wattage"], data["hours_per_day"],
                   data.get("quantity", 1), data.get("days_per_month", 30),
                   data.get("category", "Other"))

    def __str__(self):
        return (f"{self.name} ({self.category}) - {self.wattage:.0f} W x "
                f"{self.quantity} unit(s), {self.hours_per_day:g} h/day")

# Household class - keeps the list of appliances in the house

from energy_tracker.models.appliance import Appliance


class Household:

    def __init__(self, owner_name="My Home", occupants=1):
        self.owner_name = owner_name
        self.occupants = max(1, int(occupants))
        self.appliances = []

    def add_appliance(self, appliance):
        # no two appliances with the same name
        if self.find_appliance(appliance.name) is not None:
            raise ValueError(f"'{appliance.name}' already exists.")
        self.appliances.append(appliance)

    def find_appliance(self, name):
        for appliance in self.appliances:
            if appliance.name.lower() == name.strip().lower():
                return appliance
        return None

    def remove_appliance(self, name):
        appliance = self.find_appliance(name)
        if appliance is None:
            return False
        self.appliances.remove(appliance)
        return True

    def is_empty(self):
        return len(self.appliances) == 0

    def total_daily_kwh(self):
        return sum(a.daily_kwh() for a in self.appliances)

    def total_monthly_kwh(self):
        total = 0.0
        for appliance in self.appliances:
            total += appliance.monthly_kwh()
        return total

    def kwh_by_category(self):
        totals = {}
        for appliance in self.appliances:
            totals[appliance.category] = totals.get(appliance.category, 0.0) + appliance.monthly_kwh()
        return totals

    def sorted_by_usage(self):
        # highest usage first
        return sorted(self.appliances, key=lambda a: a.monthly_kwh(), reverse=True)

    def to_dict(self):
        return {
            "owner_name": self.owner_name,
            "occupants": self.occupants,
            "appliances": [a.to_dict() for a in self.appliances],
        }

    @classmethod
    def from_dict(cls, data):
        household = cls(data.get("owner_name", "My Home"), data.get("occupants", 1))
        for item in data.get("appliances", []):
            household.add_appliance(Appliance.from_dict(item))
        return household

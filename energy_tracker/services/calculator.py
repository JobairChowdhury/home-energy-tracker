# EnergyCalculator - works out the bill, carbon emission and usage rating

from energy_tracker.services.tariff import Tariff

DEFAULT_EMISSION_FACTOR = 0.585   # kg CO2 per kWh (approx.)
LOW_USAGE = 80                    # kWh per person per month
HIGH_USAGE = 150
CO2_PER_TREE = 21                 # kg CO2 one tree absorbs in a year


class EnergyCalculator:

    def __init__(self, tariff=None, emission_factor=DEFAULT_EMISSION_FACTOR):
        self.tariff = tariff if tariff else Tariff()
        if emission_factor < 0:
            raise ValueError("Emission factor cannot be negative.")
        self.emission_factor = emission_factor

    def carbon_kg(self, kwh):
        return kwh * self.emission_factor

    def trees_to_offset_yearly(self, monthly_kwh):
        return self.carbon_kg(monthly_kwh) * 12 / CO2_PER_TREE

    def appliance_cost_share(self, household):
        # use the average rate per kWh to share the bill between appliances
        total_kwh = household.total_monthly_kwh()
        if total_kwh == 0:
            return []
        avg_rate = self.tariff.total_bill(total_kwh) / total_kwh
        results = []
        for appliance in household.sorted_by_usage():
            kwh = appliance.monthly_kwh()
            results.append({
                "appliance": appliance,
                "kwh": kwh,
                "percent": kwh / total_kwh * 100,
                "cost": kwh * avg_rate,
            })
        return results

    def usage_rating(self, household):
        per_person = household.total_monthly_kwh() / household.occupants
        if per_person <= LOW_USAGE:
            return "LOW", per_person
        elif per_person <= HIGH_USAGE:
            return "MODERATE", per_person
        else:
            return "HIGH", per_person

    def monthly_summary(self, household):
        kwh = household.total_monthly_kwh()
        rating, per_person = self.usage_rating(household)
        bill = self.tariff.total_bill(kwh)
        return {
            "daily_kwh": household.total_daily_kwh(),
            "monthly_kwh": kwh,
            "breakdown": self.tariff.breakdown(kwh),
            "energy_charge": self.tariff.energy_charge(kwh),
            "total_bill": bill,
            "yearly_bill": bill * 12,
            "carbon_kg": self.carbon_kg(kwh),
            "trees": self.trees_to_offset_yearly(kwh),
            "rating": rating,
            "kwh_per_person": per_person,
        }

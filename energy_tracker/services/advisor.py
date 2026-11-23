# SavingsAdvisor - energy saving tips, what-if simulation and upgrade comparison

TIPS = {
    "Cooling": [
        "Use a fan instead of the air-conditioner when it is not too hot.",
        "Set the air-conditioner to 24-25 C and use the timer or sleep mode.",
        "Close doors and windows while cooling, clean the filters every month.",
    ],
    "Lighting": [
        "Change to LED bulbs.",
        "Switch off lights in empty rooms and use daylight when possible.",
    ],
    "Kitchen": [
        "Keep the fridge door closed and set it to 3-5 C.",
        "Cook with the lid on and boil only the water you need.",
    ],
    "Entertainment": [
        "Turn devices off at the switch instead of leaving them on standby.",
        "Use a power strip to switch off many devices at once.",
    ],
    "Laundry": [
        "Wash full loads and use cold water.",
        "Dry clothes in the sun instead of using a dryer.",
    ],
    "Other": [
        "Unplug chargers and appliances when not in use.",
        "Buy appliances with a higher energy star rating.",
    ],
}


class SavingsAdvisor:

    def __init__(self, calculator):
        self.calculator = calculator

    def tips_for_household(self, household, top_n=3):
        # tips for the appliances that use the most energy
        advice = []
        for appliance in household.sorted_by_usage()[:top_n]:
            advice.append((appliance, TIPS.get(appliance.category, TIPS["Other"])))
        return advice

    def simulate_reduction(self, household, appliance, hours_saved_per_day):
        # what if this appliance is used fewer hours per day?
        if hours_saved_per_day <= 0:
            raise ValueError("Hours saved must be more than 0.")
        hours_saved = min(hours_saved_per_day, appliance.hours_per_day)

        tariff = self.calculator.tariff
        current_kwh = household.total_monthly_kwh()
        kwh_saved = (appliance.wattage * hours_saved * appliance.quantity
                     * appliance.days_per_month) / 1000
        new_kwh = current_kwh - kwh_saved

        # recalculate the full bill so the block rates are correct
        money_saved = tariff.total_bill(current_kwh) - tariff.total_bill(new_kwh)
        return {
            "hours_saved": hours_saved,
            "kwh_saved": kwh_saved,
            "money_saved_month": money_saved,
            "money_saved_year": money_saved * 12,
            "co2_saved_year": self.calculator.carbon_kg(kwh_saved) * 12,
            "new_bill": tariff.total_bill(new_kwh),
        }

    def compare_upgrade(self, old_watts, new_watts, hours_per_day,
                        new_price, days_per_month=30, quantity=1,
                        household_kwh=None):
        # old appliance vs new energy efficient one + payback period
        if old_watts <= 0 or new_watts <= 0:
            raise ValueError("Wattage must be greater than 0.")
        if new_price < 0:
            raise ValueError("Price cannot be negative.")

        old_kwh = old_watts * hours_per_day * days_per_month * quantity / 1000
        new_kwh = new_watts * hours_per_day * days_per_month * quantity / 1000
        kwh_saved = old_kwh - new_kwh

        tariff = self.calculator.tariff
        if household_kwh and household_kwh > 0 and kwh_saved > 0:
            new_total = max(0.0, household_kwh - kwh_saved)
            money_saved_month = tariff.total_bill(household_kwh) - tariff.total_bill(new_total)
        else:
            # no household data, so just use the highest rate
            top_rate = max(rate for _, rate in tariff.tiers)
            money_saved_month = kwh_saved * top_rate * (1 + tariff.service_tax_rate)

        if money_saved_month > 0:
            payback_months = new_price / money_saved_month
        else:
            payback_months = None

        return {
            "old_kwh": old_kwh,
            "new_kwh": new_kwh,
            "kwh_saved": kwh_saved,
            "percent_saved": (kwh_saved / old_kwh * 100) if old_kwh else 0,
            "money_saved_month": money_saved_month,
            "money_saved_year": money_saved_month * 12,
            "co2_saved_year": self.calculator.carbon_kg(kwh_saved) * 12,
            "payback_months": payback_months,
        }

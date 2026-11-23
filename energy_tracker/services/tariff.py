# Tariff class - calculates the electricity bill using block (tiered) rates
# the more you use, the higher the rate for the extra units

# (upper limit in kWh, rate per kWh) - None means no limit
# sample rates, can be changed in the settings menu
DEFAULT_TIERS = [
    (200, 0.218),
    (300, 0.334),
    (600, 0.516),
    (900, 0.546),
    (None, 0.571),
]


class Tariff:

    def __init__(self, tiers=None, currency="RM", service_tax_rate=0.0):
        self.tiers = list(tiers) if tiers else list(DEFAULT_TIERS)
        self.currency = currency
        self.service_tax_rate = service_tax_rate
        self._validate_tiers()

    def _validate_tiers(self):
        previous_limit = 0
        for i, (limit, rate) in enumerate(self.tiers):
            if rate < 0:
                raise ValueError("Tariff rates cannot be negative.")
            if limit is None and i != len(self.tiers) - 1:
                raise ValueError("Only the last tier can have no upper limit.")
            if limit is not None:
                if limit <= previous_limit:
                    raise ValueError("Tier limits must be in increasing order.")
                previous_limit = limit

    def breakdown(self, kwh):
        # split the units into each block and work out the cost
        if kwh < 0:
            raise ValueError("kWh cannot be negative.")

        rows = []
        remaining = kwh
        lower = 0
        for limit, rate in self.tiers:
            if remaining <= 0:
                break
            if limit is None:
                units = remaining
                label = f"Above {lower} kWh"
            else:
                units = min(remaining, limit - lower)
                label = f"{lower + 1}-{limit} kWh"
            rows.append({"label": label, "kwh": units, "rate": rate, "cost": units * rate})
            remaining -= units
            if limit is not None:
                lower = limit

        # if usage goes past the last limit, charge the rest at the last rate
        if remaining > 0:
            last_rate = self.tiers[-1][1]
            rows.append({"label": f"Above {lower} kWh", "kwh": remaining,
                         "rate": last_rate, "cost": remaining * last_rate})
        return rows

    def energy_charge(self, kwh):
        return sum(row["cost"] for row in self.breakdown(kwh))

    def total_bill(self, kwh):
        charge = self.energy_charge(kwh)
        return charge + charge * self.service_tax_rate

    def to_dict(self):
        return {"tiers": [list(t) for t in self.tiers],
                "currency": self.currency,
                "service_tax_rate": self.service_tax_rate}

    @classmethod
    def from_dict(cls, data):
        tiers = [tuple(t) for t in data.get("tiers", DEFAULT_TIERS)]
        return cls(tiers, data.get("currency", "RM"), data.get("service_tax_rate", 0.0))

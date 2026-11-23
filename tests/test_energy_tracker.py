# unit tests - run with: python -m unittest discover tests -v

import os
import tempfile
import unittest

from energy_tracker.models import Appliance, Household
from energy_tracker.services import Tariff, EnergyCalculator, SavingsAdvisor
from energy_tracker.storage import DataStorage


class TestAppliance(unittest.TestCase):

    def test_monthly_kwh(self):
        # 1000 W x 8 h x 1 unit x 30 days = 240 kWh
        ac = Appliance("Air Conditioner", 1000, 8, 1, 30, "Cooling")
        self.assertAlmostEqual(ac.daily_kwh(), 8.0)
        self.assertAlmostEqual(ac.monthly_kwh(), 240.0)

    def test_quantity_multiplies_usage(self):
        lights = Appliance("LED", 10, 5, 4, 30, "Lighting")
        self.assertAlmostEqual(lights.monthly_kwh(), 6.0)

    def test_invalid_values_raise_error(self):
        with self.assertRaises(ValueError):
            Appliance("", 100, 1)
        with self.assertRaises(ValueError):
            Appliance("Fan", -5, 1)
        with self.assertRaises(ValueError):
            Appliance("Fan", 100, 25)

    def test_unknown_category_becomes_other(self):
        self.assertEqual(Appliance("X", 10, 1, category="Bad").category, "Other")


class TestHousehold(unittest.TestCase):

    def setUp(self):
        self.home = Household("Test", 2)
        self.home.add_appliance(Appliance("Fan", 100, 10, 1, 30, "Cooling"))
        self.home.add_appliance(Appliance("TV", 200, 5, 1, 30, "Entertainment"))

    def test_total_kwh(self):
        self.assertAlmostEqual(self.home.total_monthly_kwh(), 60.0)

    def test_duplicate_name_rejected(self):
        with self.assertRaises(ValueError):
            self.home.add_appliance(Appliance("fan", 50, 1))

    def test_remove(self):
        self.assertTrue(self.home.remove_appliance("tv"))
        self.assertFalse(self.home.remove_appliance("tv"))
        self.assertEqual(len(self.home.appliances), 1)

    def test_by_category(self):
        self.assertEqual(self.home.kwh_by_category(),
                         {"Cooling": 30.0, "Entertainment": 30.0})


class TestTariff(unittest.TestCase):

    def setUp(self):
        self.tariff = Tariff([(100, 0.10), (None, 0.20)])

    def test_within_first_tier(self):
        self.assertAlmostEqual(self.tariff.energy_charge(50), 5.0)

    def test_across_tiers(self):
        # 100 x 0.10 + 50 x 0.20 = 20.0
        self.assertAlmostEqual(self.tariff.energy_charge(150), 20.0)

    def test_zero_usage(self):
        self.assertEqual(self.tariff.energy_charge(0), 0)

    def test_service_tax(self):
        taxed = Tariff([(None, 0.5)], service_tax_rate=0.08)
        self.assertAlmostEqual(taxed.total_bill(100), 54.0)

    def test_invalid_tiers(self):
        with self.assertRaises(ValueError):
            Tariff([(300, 0.1), (200, 0.2)])

    def test_negative_kwh(self):
        with self.assertRaises(ValueError):
            self.tariff.breakdown(-1)


class TestCalculatorAndAdvisor(unittest.TestCase):

    def setUp(self):
        self.home = Household("Test", 1)
        self.ac = Appliance("AC", 1000, 8, 1, 30, "Cooling")      # 240 kWh
        self.home.add_appliance(self.ac)
        self.calc = EnergyCalculator(Tariff([(100, 0.10), (None, 0.20)]), 0.5)
        self.advisor = SavingsAdvisor(self.calc)

    def test_carbon(self):
        self.assertAlmostEqual(self.calc.carbon_kg(240), 120.0)

    def test_rating_high(self):
        rating, per_person = self.calc.usage_rating(self.home)
        self.assertEqual(rating, "HIGH")
        self.assertAlmostEqual(per_person, 240.0)

    def test_simulate_reduction(self):
        # Saving 2 h/day = 60 kWh, all from the 0.20 tier -> 12.00 saved
        result = self.advisor.simulate_reduction(self.home, self.ac, 2)
        self.assertAlmostEqual(result["kwh_saved"], 60.0)
        self.assertAlmostEqual(result["money_saved_month"], 12.0)

    def test_compare_upgrade_payback(self):
        # 100 W -> 50 W, 10 h/day, 30 days = 15 kWh saved x 0.20 = 3.00/month
        r = self.advisor.compare_upgrade(100, 50, 10, new_price=30)
        self.assertAlmostEqual(r["kwh_saved"], 15.0)
        self.assertAlmostEqual(r["money_saved_month"], 3.0)
        self.assertAlmostEqual(r["payback_months"], 10.0)

    def test_compare_upgrade_uses_household_tiers(self):
        # Household uses 110 kWh: saving 15 kWh removes 10 kWh at 0.20
        # and 5 kWh at 0.10 -> 2.50 saved per month
        r = self.advisor.compare_upgrade(100, 50, 10, new_price=25,
                                         household_kwh=110)
        self.assertAlmostEqual(r["money_saved_month"], 2.5)
        self.assertAlmostEqual(r["payback_months"], 10.0)


class TestStorage(unittest.TestCase):

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = DataStorage(os.path.join(folder, "data.json"))
            home = Household("Saved Home", 3)
            home.add_appliance(Appliance("Fridge", 150, 24, 1, 30, "Kitchen"))
            self.assertTrue(storage.save(home, Tariff(), 0.6))

            loaded_home, tariff, factor = storage.load()
            self.assertEqual(loaded_home.owner_name, "Saved Home")
            self.assertEqual(loaded_home.appliances[0].name, "Fridge")
            self.assertEqual(factor, 0.6)

    def test_missing_file_returns_none(self):
        self.assertIsNone(DataStorage("does/not/exist.json").load())


if __name__ == "__main__":
    unittest.main()

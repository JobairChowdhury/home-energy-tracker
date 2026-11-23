# ConsoleMenu - the main menu that the user interacts with

from energy_tracker.models.appliance import (
    Appliance, CATEGORIES, MAX_WATTAGE, MAX_QUANTITY,
)
from energy_tracker.models.household import Household
from energy_tracker.services.tariff import Tariff
from energy_tracker.services.calculator import EnergyCalculator
from energy_tracker.services.advisor import SavingsAdvisor
from energy_tracker.storage.data_storage import DataStorage
from energy_tracker.ui import input_helper as ih

LINE = "=" * 62
THIN = "-" * 62

# sample data to test the program quickly
SAMPLE_APPLIANCES = [
    ("Air Conditioner", 1000, 8, 1, 30, "Cooling"),
    ("Refrigerator", 150, 24, 1, 30, "Kitchen"),
    ("LED Light", 10, 6, 8, 30, "Lighting"),
    ("Ceiling Fan", 70, 10, 3, 30, "Cooling"),
    ("Television", 120, 5, 1, 30, "Entertainment"),
    ("Washing Machine", 500, 1, 1, 12, "Laundry"),
    ("Rice Cooker", 700, 1, 1, 30, "Kitchen"),
    ("Water Heater", 3000, 0.5, 1, 30, "Other"),
]


class ConsoleMenu:

    def __init__(self, storage=None):
        self.storage = storage if storage else DataStorage()
        self.household = Household()
        self.calculator = EnergyCalculator(Tariff())
        self.advisor = SavingsAdvisor(self.calculator)
        self.running = True

    # ---- helpers ----
    def money(self, amount):
        return f"{self.calculator.tariff.currency} {amount:,.2f}"

    @staticmethod
    def header(title):
        print("\n" + LINE)
        print(title.center(62))
        print(LINE)

    def _require_appliances(self):
        if self.household.is_empty():
            print("\n  No appliances recorded yet. Use option 1 or load sample data.")
            return False
        return True

    def _pick_appliance(self):
        names = [a.name for a in self.household.appliances]
        name = ih.get_choice("  Select appliance number: ", names)
        return self.household.find_appliance(name)

    # ---- menu ----
    def display_main_menu(self):
        self.header("HOME ENERGY USAGE TRACKER & BILL ESTIMATOR")
        print("  SDG 7: Affordable and Clean Energy".center(62))
        print(THIN)
        print(f"  Household: {self.household.owner_name}  |  "
              f"Occupants: {self.household.occupants}  |  "
              f"Appliances: {len(self.household.appliances)}")
        print(THIN)
        print("  1. Add appliance")
        print("  2. View appliances")
        print("  3. Edit / remove appliance")
        print("  4. Calculate monthly bill & carbon footprint")
        print("  5. Energy usage report (by appliance & category)")
        print("  6. Energy-saving tips & what-if simulator")
        print("  7. Compare energy-efficient appliance upgrade")
        print("  8. Household & tariff settings")
        print("  9. Save / load data")
        print("  0. Exit")
        print(THIN)

    def run(self):
        self.welcome()
        while self.running:
            self.display_main_menu()
            choice = ih.get_text("  Enter your choice (0-9): ")
            if choice == "1":
                self.add_appliance()
            elif choice == "2":
                self.view_appliances()
            elif choice == "3":
                self.edit_or_remove_appliance()
            elif choice == "4":
                self.show_monthly_bill()
            elif choice == "5":
                self.show_usage_report()
            elif choice == "6":
                self.savings_menu()
            elif choice == "7":
                self.compare_upgrade()
            elif choice == "8":
                self.settings_menu()
            elif choice == "9":
                self.data_menu()
            elif choice == "0":
                self.exit_application()
                continue
            else:
                print("  [!] Invalid choice. Please enter a number from 0 to 9.")
                continue
            ih.pause()

    def welcome(self):
        self.header("WELCOME")
        print("  This tool helps you understand where your electricity goes,")
        print("  estimate your monthly bill and carbon footprint, and find")
        print("  practical ways to save energy and money.")
        loaded = self.storage.load()
        if loaded:
            if ih.confirm("\n  Saved data found. Load it?"):
                self.household, tariff, factor = loaded
                self._apply_settings(tariff, factor)
                print("  Data loaded successfully.")
        elif ih.confirm("\n  Load sample household data to try the app?"):
            self.load_sample_data()

    # ---- enter / record information ----
    def add_appliance(self):
        self.header("ADD APPLIANCE")
        name = ih.get_text("  Appliance name: ")
        if self.household.find_appliance(name):
            print(f"  [!] '{name.title()}' already exists. Use Edit instead.")
            return
        wattage = ih.get_float(f"  Power rating in watts (1-{MAX_WATTAGE}): ",
                               1, MAX_WATTAGE)
        hours = ih.get_float("  Hours used per day (0-24): ", 0, 24)
        quantity = ih.get_int(f"  Quantity (1-{MAX_QUANTITY}) [1]: ",
                              1, MAX_QUANTITY, default=1)
        days = ih.get_int("  Days used per month (1-31) [30]: ", 1, 31, default=30)
        print("  Category:")
        category = ih.get_choice("  Select category number: ", CATEGORIES)

        appliance = Appliance(name, wattage, hours, quantity, days, category)
        self.household.add_appliance(appliance)
        print(f"\n  Added: {appliance}")
        print(f"  Estimated use: {appliance.monthly_kwh():.2f} kWh per month")

    def view_appliances(self):
        self.header("APPLIANCE LIST")
        if not self._require_appliances():
            return
        print(f"  {'No':<3}{'Name':<18}{'Category':<14}{'Watt':>7}"
              f"{'Qty':>5}{'h/day':>7}{'kWh/mth':>9}")
        print(THIN)
        for number, a in enumerate(self.household.appliances, start=1):
            print(f"  {number:<3}{a.name[:17]:<18}{a.category:<14}"
                  f"{a.wattage:>7.0f}{a.quantity:>5}{a.hours_per_day:>7g}"
                  f"{a.monthly_kwh():>9.2f}")
        print(THIN)
        print(f"  {'TOTAL':<54}{self.household.total_monthly_kwh():>6.2f}")

    def edit_or_remove_appliance(self):
        self.header("EDIT / REMOVE APPLIANCE")
        if not self._require_appliances():
            return
        appliance = self._pick_appliance()
        print(f"\n  Selected: {appliance}")
        action = ih.get_choice("  Choose action: ",
                               ["Edit hours per day", "Edit quantity",
                                "Edit wattage", "Remove appliance", "Cancel"])
        if action == "Edit hours per day":
            appliance.hours_per_day = ih.get_float("  New hours per day (0-24): ", 0, 24)
        elif action == "Edit quantity":
            appliance.quantity = ih.get_int("  New quantity: ", 1, MAX_QUANTITY)
        elif action == "Edit wattage":
            appliance.wattage = ih.get_float("  New wattage: ", 1, MAX_WATTAGE)
        elif action == "Remove appliance":
            if ih.confirm(f"  Remove '{appliance.name}'?"):
                self.household.remove_appliance(appliance.name)
                print("  Appliance removed.")
            return
        else:
            print("  Cancelled.")
            return
        print(f"  Updated: {appliance}  ->  {appliance.monthly_kwh():.2f} kWh/month")

    # ---- calculations and results ----
    def show_monthly_bill(self):
        self.header("MONTHLY BILL & CARBON FOOTPRINT")
        if not self._require_appliances():
            return
        s = self.calculator.monthly_summary(self.household)

        print(f"  Daily energy use     : {s['daily_kwh']:.2f} kWh")
        print(f"  Monthly energy use   : {s['monthly_kwh']:.2f} kWh")
        print("\n  Tariff breakdown:")
        print(f"    {'Block':<20}{'kWh':>10}{'Rate':>10}{'Cost':>16}")
        for row in s["breakdown"]:
            print(f"    {row['label']:<20}{row['kwh']:>10.2f}"
                  f"{row['rate']:>10.3f}{self.money(row['cost']):>16}")
        print(f"\n  Energy charge        : {self.money(s['energy_charge'])}")
        tax_rate = self.calculator.tariff.service_tax_rate
        if tax_rate > 0:
            print(f"  Service tax ({tax_rate * 100:.0f}%)    : "
                  f"{self.money(s['total_bill'] - s['energy_charge'])}")
        print(f"  ESTIMATED BILL       : {self.money(s['total_bill'])}")
        print(f"  Estimated yearly cost: {self.money(s['yearly_bill'])}")
        print(THIN)
        print(f"  Carbon footprint     : {s['carbon_kg']:.1f} kg CO2 / month")
        print(f"  Trees needed to offset 1 year of emissions: {s['trees']:.0f}")
        print(f"  Usage per person     : {s['kwh_per_person']:.1f} kWh/month "
              f"-> {s['rating']} usage")
        if s["rating"] == "HIGH":
            print("  Tip: see option 6 for ways to reduce your consumption.")

    def show_usage_report(self):
        self.header("ENERGY USAGE REPORT")
        if not self._require_appliances():
            return
        print("  By appliance (highest first):")
        for row in self.calculator.appliance_cost_share(self.household):
            bar = "#" * int(row["percent"] / 2.5)      # text bar chart
            print(f"    {row['appliance'].name[:16]:<17}{row['kwh']:>8.1f} kWh "
                  f"{row['percent']:>5.1f}% {self.money(row['cost']):>12}  {bar}")

        print("\n  By category:")
        total = self.household.total_monthly_kwh()
        categories = sorted(self.household.kwh_by_category().items(),
                            key=lambda item: item[1], reverse=True)
        for category, kwh in categories:
            percent = kwh / total * 100 if total else 0
            print(f"    {category:<17}{kwh:>8.1f} kWh {percent:>5.1f}%  "
                  f"{'#' * int(percent / 2.5)}")

        top = self.household.sorted_by_usage()[0]
        print(f"\n  Biggest energy user: {top.name} "
              f"({top.monthly_kwh() / total * 100:.0f}% of total)")

    def savings_menu(self):
        self.header("ENERGY-SAVING TIPS & WHAT-IF SIMULATOR")
        if not self._require_appliances():
            return
        print("  Top energy users and how to reduce them:\n")
        for appliance, tips in self.advisor.tips_for_household(self.household):
            print(f"  > {appliance.name} ({appliance.monthly_kwh():.1f} kWh/month)")
            for tip in tips:
                print(f"      - {tip}")

        if not ih.confirm("\n  Run a what-if simulation?"):
            return
        appliance = self._pick_appliance()
        hours = ih.get_float(
            f"  Reduce '{appliance.name}' usage by how many hours/day "
            f"(currently {appliance.hours_per_day:g}): ",
            0.1, max(0.1, appliance.hours_per_day))
        result = self.advisor.simulate_reduction(self.household, appliance, hours)
        print(THIN)
        print(f"  Using {appliance.name} {result['hours_saved']:g} h less per day saves:")
        print(f"    Energy  : {result['kwh_saved']:.1f} kWh per month")
        print(f"    Money   : {self.money(result['money_saved_month'])} per month "
              f"({self.money(result['money_saved_year'])} per year)")
        print(f"    Carbon  : {result['co2_saved_year']:.1f} kg CO2 per year")
        print(f"    New estimated bill: {self.money(result['new_bill'])}")

    def compare_upgrade(self):
        self.header("ENERGY-EFFICIENT UPGRADE COMPARISON")
        print("  Compare your current appliance with a more efficient model.\n")
        old_w = ih.get_float("  Current appliance wattage (W): ", 1, MAX_WATTAGE)
        new_w = ih.get_float("  New efficient appliance wattage (W): ", 1, MAX_WATTAGE)
        hours = ih.get_float("  Hours used per day (0-24): ", 0, 24)
        quantity = ih.get_int("  Quantity [1]: ", 1, MAX_QUANTITY, default=1)
        price = ih.get_float(f"  Price of new appliance "
                             f"({self.calculator.tariff.currency}): ", 0)
        r = self.advisor.compare_upgrade(
            old_w, new_w, hours, price, quantity=quantity,
            household_kwh=self.household.total_monthly_kwh())

        print(THIN)
        print(f"  {'':<22}{'Current':>14}{'Efficient':>14}")
        print(f"  {'Monthly energy (kWh)':<22}{r['old_kwh']:>14.1f}{r['new_kwh']:>14.1f}")
        print(THIN)
        if r["kwh_saved"] <= 0:
            print("  The new appliance does NOT save energy. Not recommended.")
            return
        print(f"  Energy saved : {r['kwh_saved']:.1f} kWh/month ({r['percent_saved']:.0f}%)")
        print(f"  Money saved  : {self.money(r['money_saved_month'])}/month, "
              f"{self.money(r['money_saved_year'])}/year")
        print(f"  CO2 avoided  : {r['co2_saved_year']:.1f} kg per year")
        months = r["payback_months"]
        if months <= 12:
            verdict = "Excellent - pays for itself within a year."
        elif months <= 60:
            verdict = "Good long-term investment."
        else:
            verdict = "Long payback - upgrade only when the old unit needs replacing."
        print(f"  Payback      : {months:.1f} months ({months / 12:.1f} years)")
        print(f"  Verdict      : {verdict}")

    # ---- settings and data ----
    def _apply_settings(self, tariff, emission_factor):
        self.calculator = EnergyCalculator(tariff, emission_factor)
        self.advisor = SavingsAdvisor(self.calculator)

    def settings_menu(self):
        self.header("HOUSEHOLD & TARIFF SETTINGS")
        tariff = self.calculator.tariff
        print(f"  Household name   : {self.household.owner_name}")
        print(f"  Occupants        : {self.household.occupants}")
        print(f"  Currency         : {tariff.currency}")
        print(f"  Service tax      : {tariff.service_tax_rate * 100:.1f}%")
        print(f"  Emission factor  : {self.calculator.emission_factor} kg CO2/kWh")
        print("  Tariff tiers     :")
        for limit, rate in tariff.tiers:
            print(f"     up to {limit if limit else 'above'} kWh -> {rate} per kWh")
        print("  (Default tariff rates are sample values - update them to")
        print("   match your own electricity bill for accurate results.)\n")

        option = ih.get_choice("  Change: ", [
            "Household name & occupants", "Tariff rates", "Service tax",
            "Emission factor", "Back"])
        if option == "Household name & occupants":
            self.household.owner_name = ih.get_text("  Household name: ")
            self.household.occupants = ih.get_int("  Number of occupants: ", 1, 30)
        elif option == "Tariff rates":
            new_tiers = []
            for limit, rate in tariff.tiers:
                label = f"up to {limit} kWh" if limit else "above last tier"
                new_rate = ih.get_float(f"  Rate for {label} [{rate}]: ",
                                        0, 10, default=rate)
                new_tiers.append((limit, new_rate))
            tariff.tiers = new_tiers
        elif option == "Service tax":
            percent = ih.get_float("  Service tax % (0-30): ", 0, 30)
            tariff.service_tax_rate = percent / 100
        elif option == "Emission factor":
            factor = ih.get_float("  kg CO2 per kWh (0-2): ", 0, 2)
            self._apply_settings(tariff, factor)
        else:
            return
        print("  Settings updated.")

    def data_menu(self):
        self.header("SAVE / LOAD DATA")
        option = ih.get_choice("  Choose: ", [
            "Save data", "Load saved data", "Load sample household",
            "Clear all appliances", "Back"])
        if option == "Save data":
            self.save_data()
        elif option == "Load saved data":
            loaded = self.storage.load()
            if loaded:
                self.household, tariff, factor = loaded
                self._apply_settings(tariff, factor)
                print("  Data loaded successfully.")
            else:
                print("  [!] No valid saved data found.")
        elif option == "Load sample household":
            self.load_sample_data()
        elif option == "Clear all appliances":
            if ih.confirm("  Delete ALL appliances?"):
                self.household.appliances.clear()
                print("  All appliances cleared.")

    def save_data(self):
        ok = self.storage.save(self.household, self.calculator.tariff,
                               self.calculator.emission_factor)
        if ok:
            print(f"  Data saved to {self.storage.file_path}")
        else:
            print("  [!] Could not save data.")

    def load_sample_data(self):
        self.household = Household("Sample Family", 4)
        for item in SAMPLE_APPLIANCES:
            self.household.add_appliance(Appliance(*item))
        print(f"  Loaded {len(SAMPLE_APPLIANCES)} sample appliances.")

    # ---- exit ----
    def exit_application(self):
        if not self.household.is_empty() and ih.confirm("  Save before exiting?"):
            self.save_data()
        self.header("THANK YOU")
        print("  Every kWh saved lowers your bill and the planet's emissions.")
        print("  Goodbye!")
        self.running = False

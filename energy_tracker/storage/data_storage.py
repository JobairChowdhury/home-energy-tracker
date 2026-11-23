# DataStorage - save and load the data using a JSON file

import json
import os

from energy_tracker.models.household import Household
from energy_tracker.services.tariff import Tariff

DEFAULT_FILE = os.path.join("data", "household_data.json")


class DataStorage:

    def __init__(self, file_path=DEFAULT_FILE):
        self.file_path = file_path

    def save(self, household, tariff, emission_factor):
        data = {
            "household": household.to_dict(),
            "tariff": tariff.to_dict(),
            "emission_factor": emission_factor,
        }
        try:
            folder = os.path.dirname(self.file_path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            return True
        except OSError:
            return False

    def load(self):
        # returns (household, tariff, emission_factor) or None
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            household = Household.from_dict(data["household"])
            tariff = Tariff.from_dict(data.get("tariff", {}))
            emission_factor = data.get("emission_factor", 0.585)
            return household, tariff, emission_factor
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
            return None

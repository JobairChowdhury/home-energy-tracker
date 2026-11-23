# Home Energy Usage Tracker & Bill Estimator

This is my Python console application for the Computational Thinking project.
I chose **SDG 7: Affordable and Clean Energy**.

The idea is simple. Most people only look at the total on their electricity bill
and don't really know which appliance is using the most power. This program lets
you enter your home appliances, then it calculates your monthly usage, estimated
bill and carbon emission, and gives some tips on how to save.

## Why SDG 7

SDG 7 is about making energy affordable and using it more efficiently. This app
helps with that by:
- showing which appliances use the most electricity
- estimating the monthly bill so people can plan and save money
- showing how much you can save by using an appliance less or buying a more
  energy efficient one
- converting the usage into CO2 emission (this also links to SDG 13)

## Features

1. Add appliance (name, watt, hours per day, quantity, days per month, category)
2. View all appliances in a table
3. Edit or remove an appliance
4. Calculate monthly bill and carbon footprint
5. Energy usage report by appliance and by category
6. Energy saving tips and "what if" simulator (e.g. use the aircond 2 hours less)
7. Compare an old appliance with an energy efficient one (with payback period)
8. Settings (household name, number of people, tariff rates, tax, emission factor)
9. Save / load data (saved as a JSON file)
0. Exit

## How to run

You need Python 3.8 or above. No extra libraries needed.

```
python main.py
```

When the program starts it asks if you want to load sample data. Type `y` to try
it with a sample household.

To run the tests:

```
python -m unittest discover tests -v
```

## Project structure

```
home-energy-tracker/
├── main.py                  start the program here
├── energy_tracker/
│   ├── models/              Appliance, Household
│   ├── services/            Tariff, EnergyCalculator, SavingsAdvisor
│   ├── storage/             DataStorage (save/load JSON)
│   └── ui/                  ConsoleMenu, input_helper
├── tests/                   unit tests
├── docs/                    UML class diagram (draw.io)
└── data/                    saved data goes here
```

## Calculations

- Daily kWh = watt x hours per day x quantity / 1000
- Monthly kWh = daily kWh x days used per month
- Bill is calculated using block rates (the more you use, the higher the rate):

| Block | Rate (RM/kWh) |
|---|---|
| 1 - 200 kWh | 0.218 |
| 201 - 300 kWh | 0.334 |
| 301 - 600 kWh | 0.516 |
| 601 - 900 kWh | 0.546 |
| above 900 kWh | 0.571 |

  These are sample rates. They can be changed in the Settings menu.
- CO2 (kg) = kWh x 0.585
- Trees needed = yearly CO2 / 21 (one tree absorbs about 21 kg CO2 a year)
- Payback period = price of new appliance / money saved per month

## Limitations

- The usage is an estimate based on the appliance's watt, not a real meter
  reading, so the actual bill can be different.
- Tariff rates and the emission factor are sample values.
- Appliances like inverter aircond or fridge don't run at full power all the
  time, but the program treats them like they do.
- Only one household can be saved.

## Future improvements

- GUI version using Tkinter
- Compare with real monthly bills
- Add a solar panel savings calculator
- Keep monthly history to see progress

## Author

Name: Chowdhury Md Jobair
Student ID: 202409010676
Programme: BCSSE

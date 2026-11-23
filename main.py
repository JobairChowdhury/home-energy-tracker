# Home Energy Usage Tracker & Bill Estimator
# Author: Chowdhury Md Jobair (202409010676, BCSSE)
# run this file to start the program

from energy_tracker.ui.console_menu import ConsoleMenu


def main():
    app = ConsoleMenu()
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram stopped. Goodbye!")


if __name__ == "__main__":main()

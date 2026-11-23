# functions to get input from the user and check it
# each one keeps asking until the input is valid


def get_text(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("  [!] Input cannot be empty. Please try again.")


def get_float(prompt, min_value=None, max_value=None, default=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = float(raw)
        except ValueError:
            print("  [!] Please enter a valid number.")
            continue
        if min_value is not None and value < min_value:
            print(f"  [!] Value must be at least {min_value}.")
        elif max_value is not None and value > max_value:
            print(f"  [!] Value must be at most {max_value}.")
        else:
            return value


def get_int(prompt, min_value=None, max_value=None, default=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        if not raw.lstrip("-").isdigit():
            print("  [!] Please enter a whole number.")
            continue
        value = int(raw)
        if min_value is not None and value < min_value:
            print(f"  [!] Value must be at least {min_value}.")
        elif max_value is not None and value > max_value:
            print(f"  [!] Value must be at most {max_value}.")
        else:
            return value


def get_choice(prompt, options):
    # show a numbered list and return the chosen item
    for number, option in enumerate(options, start=1):
        print(f"   {number}. {option}")
    index = get_int(prompt, 1, len(options))
    return options[index - 1]


def confirm(prompt):
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  [!] Please type y or n.")


def pause():
    input("\nPress Enter to continue...")

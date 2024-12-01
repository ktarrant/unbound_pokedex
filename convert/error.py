import pprint


errors = []
error_file = "parse_errors.txt"


def report_error(func, message):
    global errors
    errors += [(func, message)]


def save_errors():
    with open(error_file, "w") as file:
        pprint.pprint(errors, file)

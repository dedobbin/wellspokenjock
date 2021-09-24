import logging
from enum import Enum

class BadResponse(Exception):
    def __init__(self, code: int, url: str="", additional_info: str=""):            
        self.code = code
        self.additional_info = additional_info
        message = "BadResponse: %d" % code
        if url:
            message += ", from %s" % url

        super().__init__(message)


def parse_to_int(input: str, type: str or None = None):
    # """Parses values like '94.45 M' to int, optional type is something like 'B' or 'Thousands'"""
    given_input = locals()

    type = type.lower() if type else None
    valid_types = {
        "b": 1000000000,
        "billions": 1000000000,
        "m": 1000000,
        "millions": 1000000,
        "k":1000,
        "thousands" : 1000,
    }

    if type is not None and type not in valid_types:
        logging.warning("parse_to_int: Failed to parse '%s'" % str(given_input))
        return None

    value = input.replace(",", "").strip();
    
    multiplier = 1
    if (value[-1] == 'B'):
        value = value.strip(" B")
        multiplier = 1000000000
    elif (value[-1] == 'M'):
        value = value.strip(" M")
        multiplier = 1000000
    elif (value[-1] == 'K'):
        value = value.strip(" K")
        multiplier = 1000

    if type != None and type in valid_types:
        if multiplier != 1:
            logging.warning("parse_to_int: Failed to parse '%s' type is explicitly given, but number also contains a type" % str(given_input))
            return None
        
        multiplier = valid_types[type]

    try:
        return float(value) * multiplier
    except ValueError:
        logging.warning("parse_to_int: Failed to parse '%s'" % str(given_input))
        return None

def to_file(input: str, filename: str="output.html"):
    with open(filename, "w") as f:
        f.write(input)
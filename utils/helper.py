# utils.py 
import plotly.express as px  # interactive charts
import math

def convert_storage_size(size, from_unit, to_unit):
    """
    Convert between different units of data storage.

    Parameters:
    size (float): the size in the 'from_unit'.
    from_unit (str): the unit of the input size (e.g., 'MB', 'GB').
    to_unit (str): the unit to convert to (e.g., 'GB', 'TB').

    Returns:
    float: the converted size in the 'to_unit'.
    """
    # Define the conversion factor between units
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    factor = 1024

    # Find the index of the from and to units
    from_index = units.index(from_unit)
    to_index = units.index(to_unit)

    # Calculate the power difference between units
    power = from_index - to_index

    # Convert the size to the target unit
    converted_size = size * (factor ** power)

    return converted_size

# backup and archive
retention = {
    'Daily': {
        'typical' : '7 to 31 days',
        'actual' : 7
    },
    'Weekly': {
        'typical' : '4 to 8 weeks',
        'actual' : 30
    },
    'Monthly': {
        'typical' : '2 to 12 months',
        'actual' : 60
    },
    'Yearly': {
        'typical' : '1 to 7 years',
        'actual' : 365
    }
}

frequency_ingestion = {
    'Daily': 365,
    'Weekly': 52,
    'Monthly': 12,
    'Yearly': 1
}

prorated = {
    'S3 Standard - Infrequent Access': 30,
    'S3 One Zone - Infrequent Access': 30,
    'S3 Glacier Flexible Retrieval': 90,
    'S3 Glacier Deep Archive': 180,
    'S3 Glacier Instant Retrieval': 90,
    'S3 Standard': 0,
    'S3 Intelligent-Tiering': 0
}

def get_retention(key):
    return retention[key]

def get_prorated(key):
    return prorated[key]

def get_frequency(key):
    return frequency_ingestion[key]

def to_precision(x,p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """

    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)
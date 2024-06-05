# utils.py 
import plotly.express as px  # interactive charts

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

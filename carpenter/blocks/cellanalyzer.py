# This import fixes sys.path issues
import parentpath

import re
from regex import allregex
from flagable import Flagable

UNITS_DOLLAR = '$'
UNITS_POUND = '\u00A3'
UNITS_EURO = '\u20AC'

def is_empty_cell(cell):
    '''
    Checks for None elements or empty strings.
    '''
    return cell == None or (isinstance(cell, basestring) and not cell)

def is_text_cell(cell):
    '''
    Checks for non-empty strings.
    '''
    return isinstance(cell, basestring) and cell

def is_num_cell(cell):
    '''
    Checks for int or float.
    '''
    return isinstance(cell, (int, float))

def get_cell_type(cell):
    '''
    Returns a type to be used in table cell analysis. This is either 
    'basestring' or '(int, float)'.
    '''
    cell_type = None
    if isinstance(cell, basestring) and cell:
        cell_type = basestring
    elif isinstance(cell, (int, float)):
        cell_type = (int, float)
    return cell_type

def check_cell_type(cell, cell_type):
    '''
    Checks the cell type to see if it represents the cell_type passed in.
    
    Args:
        cell_type: The type id for a cell match or None for empty match.
    '''
    if cell_type == None or cell_type == type(None):
        return cell == None or (isinstance(cell, basestring) and not cell)
    else:
        return isinstance(cell, cell_type)
    
def auto_convert_cell_no_flags(cell, units=None, parens_as_neg=True):
    '''
    Performs a first step conversion of the cell to check
    it's type or try to convert if a valid conversion exists.
    This version of conversion doesn't flag changes nor store
    cell units.
    
    Args:
        units: The dictionary holder for cell units.
        parens_as_neg: Converts numerics surrounded by parens to 
            negative values
    '''
    units = units if units != None else {}
    return auto_convert_cell(flagable=Flagable(), cell=cell, position=None, worksheet=0, 
                             flags={}, units=units, parens_as_neg=parens_as_neg)

def auto_convert_cell(flagable, cell, position, worksheet, flags, units, parens_as_neg=True):
    '''
    Performs a first step conversion of the cell to check
    it's type or try to convert if a valid conversion exists.
    
    Args:
        parens_as_neg: Converts numerics surrounded by parens to negative values
    '''
    conversion = cell
    
    # Is an numeric?
    if isinstance(cell, (int, float)):
        pass
    # Is a string?
    elif isinstance(cell, basestring):
        # Blank cell?
        if not cell:
            conversion = None
        else:
            conversion = auto_convert_string_cell(flagable, cell, position, worksheet, 
                                                  flags, units, parens_as_neg=parens_as_neg)
    # Is something else?? Convert to string
    elif cell != None:
        # Since we shouldn't get this event from most file types,
        # make this a warning level conversion flag
        flagable.flag_change(flags, 'warning', position, worksheet, 
                             flagable.FLAGS['unknown-to-string'])
        conversion = str(cell)
        # Empty cell?
        if not conversion:
            conversion = None
    else:
        # Otherwise we have an empty cell
        pass
    
    return conversion

def auto_convert_string_cell(flagable, cell_str, position, worksheet, flags, 
                             units, parens_as_neg=True):
    '''
    Handles the string case of cell and attempts auto-conversion
    for auto_convert_cell.
    
    Args:
        parens_as_neg: Converts numerics surrounded by parens to negative values
    '''
    conversion = cell_str.strip()
    
    # Wrapped?
    if re.search(allregex.control_wrapping_regex, cell_str):
        # Drop the wrapping characters
        stripped_cell = cell_str.strip()
        mod_cell_str = stripped_cell[1:][:-1].strip()
        neg_mult = False
        # If the wrapping characters are '(' and ')' and the interior is a number,
        # then the number should be interpreted as a negative value
        if (stripped_cell[0] == '(' and stripped_cell[-1] == ')' and 
                re.search(allregex.contains_numerical_regex, mod_cell_str)):
            # Flag for conversion to negative
            neg_mult = True
        flagable.flag_change(flags, 'interpreted', position, worksheet, 
                            flagable.FLAGS['removed-wrapping'])
        # Try again without wrapping
        converted_value = auto_convert_cell(flagable, mod_cell_str, position, 
                                            worksheet, flags, units)
        neg_mult = neg_mult and check_cell_type(converted_value, get_cell_type(0))
        if neg_mult and parens_as_neg:
            flagable.flag_change(flags, 'interpreted', position, worksheet, 
                                 flagable.FLAGS['converted-wrapping-to-neg'])
        return -converted_value if neg_mult else converted_value
    # Is a string containing numbers?
    elif re.search(allregex.contains_numerical_regex, cell_str):
        conversion = auto_convert_numeric_string_cell(flagable, conversion, position, 
                                                      worksheet, flags, units)
    elif re.search(allregex.bool_regex, cell_str):
        flagable.flag_change(flags, 'interpreted', position, worksheet, 
                             flagable.FLAGS['bool-to-int'])
        conversion = 1 if re.search(allregex.true_bool_regex, cell_str) else 0
        
    return conversion

def auto_convert_numeric_string_cell(flagable, cell_str, position, worksheet, flags, units):
    '''
    Handles the string containing numeric case of cell and attempts 
    auto-conversion for auto_convert_cell.
    '''
    def numerify_str(cell_str, flag_level='minor', flag_text=""):
        '''
        Differentiates between int and float strings. Expects a numeric string.
        '''
        if re.search(allregex.integer_regex, cell_str):
            flagable.flag_change(flags, flag_level, position, worksheet)
            return int(cell_str)
        else:
            flagable.flag_change(flags, flag_level, worksheet, position)
            return float(cell_str)
    
    def convert_to_int_or_float(cell_str, flag_level='minor', flag_text=""):
        if not cell_str:
            conversion = 0
            flagable.flag_change(flags, 'warning', position, worksheet,
                                 flagable.FLAGS['empty-to-zero-string'])
        if re.search(allregex.numerical_regex, cell_str):
            conversion = numerify_str(cell_str, flag_level, flag_text)
        # Comma separated?
        elif re.search(allregex.comma_sep_numerical_regex, cell_str):
            smashed_cell = ''.join(cell_str.split(','))
            conversion = numerify_str(smashed_cell, flag_level, flag_text)
        # Begins with money symbol?
        elif re.search(allregex.begins_with_monetary_symbol_regex, cell_str):
            symbol = cell_str[0]
            cell_str = cell_str[1:]
            try:
                conversion = convert_to_int_or_float(cell_str, 'interpreted', 
                        flagable.FLAGS['monetary-removal'])
                if re.search(allregex.contains_dollar_symbol_regex, symbol):
                    units[position] = UNITS_DOLLAR
                elif re.search(allregex.contains_pound_symbol_regex, symbol):
                    units[position] = UNITS_POUND
                elif re.search(allregex.contains_euro_symbol_regex, symbol):
                    units[position] = UNITS_EURO
            except ValueError:
                conversion = cell_str
                flagable.flag_change(flags, 'warning', position, worksheet,
                                    flagable.FLAGS['failed-monetary-convert'])
        # Number ending in 'k'?
        elif re.search(allregex.ends_with_thousands_scaling_regex, cell_str):
            cell_str = cell_str.rstrip()[:-1]
            try:
                conversion = 1000*convert_to_int_or_float(cell_str, 'interpreted', 
                                  flagable.FLAGS['thousands-convert'])
            except ValueError:
                flagable.flag_change(flags, 'warning', position, worksheet,
                                    flagable.FLAGS['failed-thousands-convert'])
        # Number ending in 'M' or 'MM'?
        elif re.search(allregex.ends_with_millions_scaling_regex, cell_str):
            if cell_str[-2] == "M":
                cell_str = cell_str[:-2]
            else:
                cell_str = cell_str[:-1]
            try:
                conversion = 1000000*convert_to_int_or_float(cell_str, 'interpreted', 
                        flagable.FLAGS['millions-convert'])
            except ValueError:
                flagable.flag_change(flags, 'warning', position, worksheet,
                                     flagable.FLAGS['failed-millions-convert'])
        else:
            raise ValueError("Cannot convert cell")
        return conversion
            
            
    # Try converting
    try:
        return convert_to_int_or_float(cell_str)
    # Couldn't convert?
    except ValueError:
        flagable.flag_change(flags, 'minor', position, worksheet,
                             flagable.FLAGS['failed-convert-numeric-string'])
        return cell_str

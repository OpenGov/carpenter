'''
Regular expressions used to match various date time stamps.
'''

import re
from location import _not_prefixed_impl, _not_followed_impl

'''
This matches any year or fiscal year indicator.
'''
# Inefficient detector, but doesn't need any flags
_contains_fiscal_year_impl = (
    r"(?:(?:[fF][iI][sS][cC][aA][lL] ?)?"+
    r"[yY][eE][aA][rR])")

contains_year_regex = re.compile(_contains_fiscal_year_impl)

'''
Like containsYear but also doesn't allow for trailing or following characters 
other than whitespace
'''
_year_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_fiscal_year_impl+
    _not_followed_impl+r")")

year_regex = re.compile(_year_impl)


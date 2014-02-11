'''
Regular expressions for matching contained data.
'''

import re
from location import _not_prefixed_impl, _not_followed_impl

'''
The following are common string cases used in transparency data extraction.

These checks find the pressense of monetary value indicators, $, pound sign, euro sign.
'''
_dollar_amount_impl = r"\$"
_pound_amount_impl = ur"\u00A3"
_euro_amount_impl = ur"\u20AC"
_contains_monetary_symbol_impl = (
    r"(?:["+_dollar_amount_impl+
    _pound_amount_impl+
    _euro_amount_impl+r"])")

contains_monetary_symbol_regex = re.compile(_contains_monetary_symbol_impl)
contains_dollar_symbol_regex = re.compile(_dollar_amount_impl)
contains_pound_symbol_regex = re.compile(_pound_amount_impl)
contains_euro_symbol_regex = re.compile(_euro_amount_impl)

'''
Like containsMonetarySymbol but requires that the string be preceded by whitespace 
or nothing.
'''
_begins_with_monetary_symbol_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_monetary_symbol_impl+r")")
_begins_with_dollar_symbol_impl = (
    r"(?:"+_not_prefixed_impl+
    _dollar_amount_impl+r")")
_begins_with_pound_symbol_impl = (
    r"(?:"+_not_prefixed_impl+
    _pound_amount_impl+r")")
_begins_with_euro_symbol_impl = (
    r"(?:"+_not_prefixed_impl+
    _euro_amount_impl+r")")

begins_with_monetary_symbol_regex = re.compile(_begins_with_monetary_symbol_impl)
begins_with_dollar_symbol_regex = re.compile(_begins_with_dollar_symbol_impl)
begins_with_pound_symbol_regex = re.compile(_begins_with_pound_symbol_impl)
begins_with_euro_symbol_regex = re.compile(_begins_with_euro_symbol_impl)

'''
Indicators for being scaled by a thousand or million. These only match if following 
a numeric value.
'''
_prefaced_by_numeric_impl = r"(?:(?:[0-9]\.?)\s*)"
_ends_with_thousands_scaling_impl = r"(?:"+_prefaced_by_numeric_impl+"k"+_not_followed_impl+r")"
ends_with_thousands_scaling_regex = re.compile(_ends_with_thousands_scaling_impl)

_ends_with_millions_scaling_impl = r"(?:"+_prefaced_by_numeric_impl+r"M{1,2}"+_not_followed_impl+r")"
ends_with_millions_scaling_regex = re.compile(_ends_with_millions_scaling_impl)

'''
Regex for capturing wrapped information. Brackets, parens, and curly brackets 
can all be detected.
'''
# White space or non-whitespace repeated => match everything
_anthing_impl = r"[\s\S]*"
# Bracket type
_contains_bracketed_impl = r"(?:\["+_anthing_impl+"\])"
_bracketed_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_bracketed_impl+
    _not_followed_impl+r")")

contains_bracketed_regex = re.compile(_contains_bracketed_impl)
bracketed_regex = re.compile(_bracketed_impl)

# Curly Bracket type
_contains_curly_bracketed_impl = r"(?:{"+_anthing_impl+"})"
_curly_bracketed_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_curly_bracketed_impl+
    _not_followed_impl+r")")

curly_bracketed_regex = re.compile(_curly_bracketed_impl)
contains_curly_bracketed_regex = re.compile(_contains_curly_bracketed_impl)

# Parens type
_contains_parens_impl = r"(?:\("+_anthing_impl+"\))"
_parens_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_parens_impl+
    _not_followed_impl+r")")

contains_parens_regex = re.compile(_contains_parens_impl)
parens_regex = re.compile(_parens_impl)

# Single quotes type
_contains_single_quotes_impl = r"(?:'"+_anthing_impl+"')"
_single_quotes_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_single_quotes_impl+
    _not_followed_impl+r")")

contains_single_quotes_regex = re.compile(_contains_single_quotes_impl)
single_quotes_regex = re.compile(_single_quotes_impl)

# Double quotes type
contains_double_quotes_impl = r'(?:"'+_anthing_impl+'")'
_double_quotes_impl = (
    r"(?:"+_not_prefixed_impl+
    contains_double_quotes_impl+
    _not_followed_impl+r")")

contains_double_quotes_regex = re.compile(contains_double_quotes_impl)
double_quotes_regex = re.compile(_double_quotes_impl)

# Any of the above types
_contains_control_wrapping_impl = (
    r"(?:"+_contains_bracketed_impl+
    r"|"+_contains_curly_bracketed_impl+
    r"|"+_contains_parens_impl+
    r"|"+_contains_single_quotes_impl+
    r"|"+contains_double_quotes_impl+r")")
_control_wrapping_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_control_wrapping_impl+
    _not_followed_impl+r")")

contains_control_wrapping_regex = re.compile(_contains_control_wrapping_impl)
control_wrapping_regex = re.compile(_control_wrapping_impl)

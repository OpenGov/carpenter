'''
Regular expressions used to match various titles.
'''

import re
from location import _not_prefixed_impl, _not_followed_impl

'''
Account strings are usually all numbers and '-' characters.
They can also include capital characters in some datasets, but we discount those here.
'''
_contains_account_string_impl = (r"(?:[0-9-]*)")
_account_string_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_account_string_impl+
    _not_followed_impl+r")")

account_string_regex = re.compile(_account_string_impl)

'''
Finds a variety of 'transfer' spelling variations which can be found in COA data.
'''
_contains_transfer_impl = (
     # Must start with 'tran'
     r"(?:[tT][rR][aA][nN]"
     # followed by an optional 's' and/or '.'
     r"((?:[sS]?\.?)|"
     # or 'sfer' and an optional 's'
     r"(?:[sS][fF][eE][rR][sS]?)))")

# Can be 'In' or 'From'
_contains_in_impl = r"(?:(?:[iI][nN])|(?:[fF][rR][oO][mM]))"
# Can be 'Out' or 'To'
_contains_out_impl = r"(?:(?:[oO][uU][tT])|(?:[tT][oO]))"

_contains_transfer_in_impl = (
    r"(?:"+_contains_transfer_impl+
    # Any following whitespace
    r"\s*"+
    _contains_in_impl+r")")

_contains_transfer_out_impl = (
    r"(?:"+_contains_transfer_impl+
    # Any following whitespace
    r"\s*"+
    _contains_out_impl+r")")
_contains_transfer_any_impl = (
    r"(?:"+_contains_transfer_impl+
    # Any following whitespace
    r"\s*"
    r"(?:"+_contains_in_impl+r"|"+
    _contains_out_impl+r"))")

contains_transfer_in_regex = re.compile(_contains_transfer_in_impl)
contains_transfer_out_regex = re.compile(_contains_transfer_out_impl)
contains_transfer_any_regex = re.compile(_contains_transfer_any_impl)

'''
Like containsTransferRegex but also doesn't allow for trailing or following 
characters other than whitespace
'''
_transfer_in_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_transfer_in_impl+
    _not_followed_impl+r")")
_transfer_out_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_transfer_out_impl+
    _not_followed_impl+r")")
_transfer_any_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_transfer_any_impl+
    _not_followed_impl+r")")

transfer_in_regex = re.compile(_transfer_in_impl)
transfer_out_regex = re.compile(_transfer_out_impl)
transfer_any_regex = re.compile(_transfer_any_impl)

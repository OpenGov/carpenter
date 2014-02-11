'''
Regular expressions for matching primitive types.
'''
import re
from location import _not_prefixed_impl, _not_followed_impl

'''
This matches any integer based number with a possible '+-' prepended.

It does not match any floating point numbers
'''
_contains_integer_impl = r"(?:[-+]?(?:[0-9]+))"

contains_integer_regex = re.compile(_contains_integer_impl)

'''
Like containsInteger but also doesn't allow for trailing or following characters 
other than whitespace
'''
_integer_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_integer_impl+
    _not_followed_impl+r")")

integer_regex = re.compile(_integer_impl)

'''
This matches any floating or integer based number with a possible '+-' prepending 
_numerical_impl values with one or zero 
'.' characters.

This does not handle exponential cases indicated by 'e'.
'''
_contains_numerical_non_exp_impl = (
    # Can start with or without a '-+'
    r"(?:[-+]?"
    # Can be either a number-'.'-(possible:number)
    r"(?:(?:[0-9]+(?:\.[0-9]*))|"
    # Or a (possible:number-'.')-number
    r"(?:(?:[0-9]*\.)?[0-9]+)))")

# Faster than contains_numerical_regex
contains_numerical_non_exp_regex = re.compile(_contains_numerical_non_exp_impl)

'''
Like contains_numerical_non_exp_regex but also doesn't allow for trailing or following 
characters other than whitespace
'''
_numerical_non_exp_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_numerical_non_exp_impl+
    _not_followed_impl+r")")

numerical_non_exp_regex = re.compile(_numerical_non_exp_impl)

'''
Like containsNumericalNonExp but also catches exponentials marked by 'e'.
'''
_contains_numerical_impl = (
    r"(?:"+_contains_numerical_non_exp_impl+
    # Can contain an 'e'
    r"(?:[eE]"+
        # 'e' must be followed by an integer
        _contains_integer_impl+
    r")?)")

contains_numerical_regex = re.compile(_contains_numerical_impl)

'''
Like containsNumericalImpl but also doesn't allow for trailing or following characters 
other than whitespace
'''
_numerical_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_numerical_impl+
    _not_followed_impl+r")")

numerical_regex = re.compile(_numerical_impl)
    
'''
This matches any floating based number with a possible '+-' prepending numericalImpl 
values with one '.' character.

Integers without a '.' character are not matched.

This does not handle exponential cases indicated by 'e'.
'''
_contains_floating_non_exp_impl = (
    # Can start with or without a '-+'
    r"(?:[-+]?"
    # Can be either a number-'.'-(possible:number)
    r"(?:(?:[0-9]+(?:\.[0-9]*))|"
    # Or a (possible:number)-'.'-number
    r"(?:(?:[0-9]*)(?:\.[0-9]+))))")

# Faster than contains_floating_regex
contains_floating_non_exp_regex = re.compile(_contains_floating_non_exp_impl)

'''
Like containsNonExpFloating but also doesn't allow for trailing or following 
characters other than whitespace
'''
_floating_non_exp_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_floating_non_exp_impl+
    _not_followed_impl+r")")

floating_non_exp_regex = re.compile(_floating_non_exp_impl)
    
'''
Like containsNonExpFloating but also catches exponentials marked by 'e'.
'''
_contains_floating_impl = (
    # Can be an exponential numerical
    r"(?:(?:"+_contains_numerical_non_exp_impl+
    # Must contain an 'e'
    r"(?:[eE]"+
        # 'e' must be followed by an integer
        _contains_integer_impl+
     # Or must be non-exp floating value
    r"))|"+_contains_floating_non_exp_impl+r")")

contains_floating_regex = re.compile(_contains_floating_impl)
    
'''
Like containsFloating but also doesn't allow for trailing or following characters 
other than whitespace
'''
_floating_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_floating_impl+
    _not_followed_impl+r")")

floating_regex = re.compile(_floating_impl)

'''
This matches any string based boolean indicator.
'''
# Inefficient detector, but doesn't need any flags
_contains_true_impl = r"(?:[tT][rR][uU][eE])"
_contains_false_impl = r"(?:[fF][aA][lL][sS][eE])"
_contains_bool_impl = r"(?:"+_contains_true_impl+r"|"+_contains_false_impl+r")"

contains_bool_regex = re.compile(_contains_bool_impl)
contains_true_regex = re.compile(_contains_true_impl)
contains_false_regex = re.compile(_contains_false_impl)

'''
Like containsBool but also doesn't allow for trailing or following characters 
other than whitespace
'''
_true_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_true_impl+
    _not_followed_impl+r")")
_false_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_false_impl+
    _not_followed_impl+r")")
_bool_impl = (
    r"(?:"+_not_prefixed_impl+
    _contains_bool_impl+
    _not_followed_impl+r")")

bool_regex = re.compile(_bool_impl)
true_bool_regex = re.compile(_true_impl)
false_bool_regex = re.compile(_false_impl)

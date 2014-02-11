'''
Regular expressions for matching location of data within a string.
'''

'''
Defines regex strings which block prefixing or postfixing

Must be prefixed/trailed by whitespace/nothing
'''
_not_prefixed_impl = r"(?=^)(?:\s*)"
_not_followed_impl = r"(?:\s*)(?=$)"

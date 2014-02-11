import collections

class Flagable(object):
    '''
    Defines an object which can flag various levels of
    errors and changes within a grid/table.
    '''
    
    FLAG_LEVELS = {'minor' : 0,
                   'interpreted' : 3,
                   'warning' : 5,
                   'error' : 8,
                   'fatal' : 10}
    FLAG_LEVEL_CODES = { v: k for k,v in FLAG_LEVELS.iteritems() }
    
    # Add to these as subclasses need more messages.
    # Keeping these with one dictionary saves a lot of space
    # when they are generated on the fly and gives consistency
    # across functions when the message is changed.
    _ACTUAL_FLAGS = {
         None : "",
         '' : "",
         '0-size' : "Block width and/or height is 0",
         '1-size' : "Block width and/or height is 1",
         'used' : "Cell already used by another block",
         'unexpected-change' : "Cell type unexpectedly changed",
         'converted-to-string' : "Converted non-string title to string",
         'copied-title' : "Copied prior title into cell",
         'unknown-to-string' : "Unknown cell type converted to string",
         'removed-wrapping' : "Removed wrapping",
         'converted-wrapping-to-neg' : "Removed parenthesis wrapping and swapped sign of value",
         'bool-to-int' : "Boolean to integer",
         'empty-to-zero-string' : "Converted empty string to 0",
         'monetary-removal' : "Converted string beginning with monetary symbol to numeric",
         'failed-monetary-convert' : "Unable to convert numeric string beginning with monetary symbol to numeric",
         'thousands-convert' : "Converted string ending in 'k' to numeric",
         'failed-thousands-convert' : "Unable to convert numeric string ending in 'k' to numeric",
         'millions-convert' : "Converted string ending in 'M' to numeric",
         'failed-millions-convert' : "Unable to convert numeric string ending in 'M' to numeric",
         'failed-convert-numeric-string' : "Unable to convert string containing numeric to pure numeric"}
    
    # Give FLAGS a default error code, in case someone misspells an input
    FLAGS = collections.defaultdict(lambda: "Unrecognized error code")
    # Copy _ACTUAL_FLAGS into FLAGS
    for k in _ACTUAL_FLAGS:
        FLAGS[k] = _ACTUAL_FLAGS[k]
    
    FlagLevelTuple = collections.namedtuple('FlagLevelTuple', 
                                            ['level', 'location', 'worksheet', 'message'])
    
    def flag_change(self, flags, level, location=None, worksheet=None, message=''):
        '''
        Wraps the pushing of a change flag into the flags dictionary to handle
        all edge cases/auto-filling.
        '''
        if not isinstance(level, basestring):
            try:
                level = self.FLAG_LEVEL_CODES[level]
            except KeyError:
                level = 'fatal'
                
        if location == None:
            location = (-1, -1)
        
        ftuple = self.FlagLevelTuple(level, location, worksheet, message)
        
        # Handle flags[level] not being present
        try:
            flags[level].append(ftuple)
        except KeyError:
            flags[level] = [ftuple]
    
    def get_worst_flag_level(self, flags):
        '''
        Determines the worst flag present in the provided flags. If no
        flags are given then a 'minor' value is returned.
        '''
        worst_flag_level = 0
        for flag_level_name in flags:
            flag_level = self.FLAG_LEVELS[flag_level_name] 
            if flag_level > worst_flag_level:
                worst_flag_level = flag_level
        return self.FLAG_LEVEL_CODES[worst_flag_level]
    
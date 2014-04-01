# This import fixes sys.path issues
import parentpath

import unittest
import re
import itertools
from carpenter.regex import allregex

def all_casings(in_str):
    '''
    Helper used to create all cases of an input string
    '''
    return (''.join(t) for t in itertools.product(*zip(in_str.lower(), in_str.upper())))
    
def prefix_suffix_whitespace(prefix, suffix):
    '''
    Helper to identify when prefix and suffix are whitespace or empty
    '''  
    return (not prefix or prefix.isspace()) and (not suffix or suffix.isspace())

class RegexTypesTest(unittest.TestCase):
    '''
    Tests all of the regular expressions in this repository for 
    consistent matching.
    '''
    def setUp(self):
        # Don't put any 'true' or 'false' statements in false_checks, prefixes, or suffixes
        self.false_checks = ["", " \t \n ", "a", "a ", " a", " a ", ".", " . ", "e", " e ", "-", "+"]
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep "]
        self.suffixes = self.prefixes
        self.integer_strs = ["0", "1", "-1", "12345", "-12345"]
        self.float_strs = ["0.0", "0.", ".0",
                           "1.0", "1.", ".1", 
                           "-1.0", "-1.", "-.1",
                           "12345.", "123.45", ".12345",
                           "-12345.", "-123.45", "-.12345"]
        self.comma_sep_strs = ["1,234", "1,234.", "1,234.5", "1,234.5678", 
                               "12,345", "123,456", "1,234,567.89"]
        # Python can't handle floating exponentials in the num-'e'-num format
        self.exp_strs = [exp_str_prefix+"e"+exp_str_postfix 
            for exp_str_prefix in self.integer_strs + self.float_strs
            for exp_str_postfix in self.integer_strs]
        self.true_strs = [tc for tc in all_casings("true")]
        self.false_strs = [fc for fc in all_casings("false")]
    
    # Helper function for function naming
    def none_check_str(self, test_func):
        if test_func == self.assertIsNotNone:
            return "not None"
        elif test_func == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
        
    def run_regex_test(self, regex, int_assert_chooser, float_assert_chooser, 
                       exp_assert_chooser, bool_assert_chooser, additional_tests=None):
        '''
        Runs a suite of tests on a regular expression. The int_assert_chooser
        and other Chooser paramters should be functions of the following form:
        
        Args:
            int_assert_chooser: [assertIsNone or assertIsNotNone]  <= prefix, string, suffix
            float_assert_chooser: [assertIsNone or assertIsNotNone]  <= prefix, string, suffix 
            exp_assert_chooser: [assertIsNone or assertIsNotNone]  <= prefix, string, suffix
            bool_assert_chooser: [assertIsNone or assertIsNotNone]  <= prefix, string, suffix, isTrueStr
            
            additional_tests: Can define an iterable of other tests to be run with the form:
                int_assert_chooser: None  <= prefix, suffix
        '''
        assert_func = self.assertIsNone
        for check_str in self.false_checks:
            assert_func(re.search(regex, check_str),
                       "String '"+check_str+"' should have returned "+
                       self.none_check_str(assert_func))
            
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Test integer strings
                for check_str in self.integer_strs:
                    assert_func = int_assert_chooser(prefix, check_str, suffix)
                    assert_func(re.search(regex, prefix+check_str+suffix), 
                               "String '"+prefix+check_str+suffix+"' should have returned "+
                               self.none_check_str(assert_func))
                    
                # Test float strings
                for check_str in self.float_strs:
                    assert_func = float_assert_chooser(prefix, check_str, suffix)
                    assert_func(re.search(regex, prefix+check_str+suffix), 
                               "String '"+prefix+check_str+suffix+"' should have returned "+
                               self.none_check_str(assert_func))
                    
                # Test exponential strings
                for check_str in self.exp_strs:
                    assert_func = exp_assert_chooser(prefix, check_str, suffix)
                    assert_func(re.search(regex, prefix+check_str+suffix), 
                               "String '"+prefix+check_str+suffix+"' should have returned "+
                               self.none_check_str(assert_func))
            
                for check_str in self.true_strs:
                    assert_func = bool_assert_chooser(prefix, check_str, suffix, True)
                    assert_func(re.search(regex, prefix+check_str+suffix), 
                               "String '"+prefix+check_str+suffix+"' should have returned "+
                               self.none_check_str(assert_func))
                
                for check_str in self.false_strs:
                    assert_func = bool_assert_chooser(prefix, check_str, suffix, False)
                    assert_func(re.search(regex, prefix+check_str+suffix), 
                               "String '"+prefix+check_str+suffix+"' should have returned "+
                               self.none_check_str(assert_func))
                
                # Run any additional tests provided for the prefix/suffix
                if additional_tests != None:
                    for test in additional_tests:
                        test(prefix, suffix)
    
    def test_contains_non_exp_numerical_regex(self):
        '''Numerics Tests'''
        def check_number_exp_matches(prefix, suffix):
            for check_str in self.exp_strs:
                expected_matches = 2
                all_results = len(re.findall(allregex.contains_numerical_non_exp_regex, prefix+check_str+suffix))
                self.assertEqual(all_results, expected_matches, "String '"+prefix+check_str+suffix+
                                 "' should have returned "+str(expected_matches)+
                                 " matches and instead returned " + str(all_results))
        
        self.run_regex_test(regex=allregex.contains_numerical_non_exp_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[check_number_exp_matches])
                    
    def test_non_exp_numerical_regex(self):
        white_space_sens_assert = lambda p,c,s: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                 else self.assertIsNone)
        self.run_regex_test(regex=allregex.numerical_non_exp_regex, 
                            int_assert_chooser=white_space_sens_assert,
                            float_assert_chooser=white_space_sens_assert,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone)

    def test_contains_numerical_regex(self):
        def check_number_exp_matches(prefix, suffix):
            for check_str in self.exp_strs:
                expected_matches = 1
                all_results = len(re.findall(allregex.contains_numerical_regex, prefix+check_str+suffix))
                self.assertEqual(all_results, expected_matches, "String '"+prefix+check_str+suffix+
                                    "' should have returned "+str(expected_matches)+
                                    " matches and instead returned " + str(all_results))
        
        self.run_regex_test(regex=allregex.contains_numerical_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[check_number_exp_matches])
                    
    def test_numerical_regex(self):
        white_space_sens_assert = lambda p,c,s: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                 else self.assertIsNone)
        self.run_regex_test(regex=allregex.numerical_regex, 
                            int_assert_chooser=white_space_sens_assert,
                            float_assert_chooser=white_space_sens_assert,
                            exp_assert_chooser=white_space_sens_assert,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone)
    
    def test_contains_non_exp_float_regex(self):
        '''Float Tests'''
        def check_number_exp_matches(prefix, suffix):
            for check_str in self.exp_strs:
                # Determine how many results we should have from findall
                expected_matches = (prefix+check_str+suffix).count('.')
                all_results = len(re.findall(allregex.contains_floating_non_exp_regex, prefix+check_str+suffix))
                self.assertEqual(all_results, expected_matches, "String '"+prefix+check_str+suffix+
                                 "' should have returned "+str(expected_matches)+
                                 " matches and instead returned " + str(all_results))
        
        self.run_regex_test(regex=allregex.contains_floating_non_exp_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            exp_assert_chooser=lambda p,c,s: (self.assertIsNone if c.count('.') == 0 
                                                                else self.assertIsNotNone),
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[check_number_exp_matches])
                    
    def test_non_exp_float_regex(self):
        white_space_sens_assert = lambda p,c,s: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                 else self.assertIsNone)
        self.run_regex_test(regex=allregex.floating_non_exp_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=white_space_sens_assert,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone)
                    
    def test_contains_float_regex(self):
        def check_number_exp_matches(prefix, suffix):
            for check_str in self.exp_strs:
                # Determine how many results we should have from findall
                expected_matches = 1
                all_results = len(re.findall(allregex.contains_floating_regex, prefix+check_str+suffix))
                self.assertEqual(all_results, expected_matches, "String '"+prefix+check_str+suffix+
                                 "' should have returned "+str(expected_matches)+
                                 " matches and instead returned " + str(all_results))
        
        self.run_regex_test(regex=allregex.contains_floating_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[check_number_exp_matches])
                    
    def test_float_regex(self):
        white_space_sens_assert = lambda p,c,s: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                 else self.assertIsNone)
        def convert_type(prefix, suffix):
            for check_str in self.float_strs + self.exp_strs:
                if prefix_suffix_whitespace(prefix, suffix):
                    # This should not raise an exception
                    float(check_str)
        self.run_regex_test(regex=allregex.floating_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=white_space_sens_assert,
                            exp_assert_chooser=white_space_sens_assert,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[convert_type])
    
    def test_contains_integer_regex(self):
        '''Integer Tests'''
        self.run_regex_test(regex=allregex.contains_integer_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNotNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone)
                    
    def test_integer_regex(self):
        white_space_sens_assert = lambda p,c,s: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                 else self.assertIsNone)
        def convert_type(prefix, suffix):
            for check_str in self.integer_strs:
                if prefix_suffix_whitespace(prefix, suffix):
                    # This should not raise an exception
                    int(check_str)
        self.run_regex_test(regex=allregex.integer_regex, 
                            int_assert_chooser=white_space_sens_assert,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[convert_type])
        
    def test_comma_sep_regex(self):
        '''Comma separated numerics'''
        def comma_check(prefix, suffix):
            for check_str in self.comma_sep_strs:
                if prefix_suffix_whitespace(prefix, suffix):
                    assert_func = self.assertIsNotNone
                else:
                    assert_func = self.assertIsNone
                assert_func(re.search(allregex.comma_sep_numerical_regex, 
                                     prefix+check_str+suffix), 
                           "String '"+prefix+check_str+suffix+"' should have returned "+
                           self.none_check_str(assert_func))
                    
        self.run_regex_test(regex=allregex.comma_sep_numerical_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone,
                            additional_tests=[comma_check])
    
    def test_contains_bool_regex(self):
        '''Bool Tests'''
        self.run_regex_test(regex=allregex.contains_bool_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNotNone)
                    
    def test_contains_true_regex(self):
        self.run_regex_test(regex=allregex.contains_true_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNotNone if t else self.assertIsNone)
                    
    def test_contains_false_regex(self):
        self.run_regex_test(regex=allregex.contains_false_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=lambda p,c,s,t: self.assertIsNone if t else self.assertIsNotNone)
    
    def test_bool_regex(self):
        white_space_sens_assert = lambda p,c,s,t: (self.assertIsNotNone if prefix_suffix_whitespace(p,s) 
                                                   else self.assertIsNone)
        self.run_regex_test(regex=allregex.bool_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=white_space_sens_assert)
        
    def test_true_regex(self):
        white_space_sens_assert = lambda p,c,s,t: (self.assertIsNotNone if 
                                                   t and prefix_suffix_whitespace(p,s) 
                                                   else self.assertIsNone)
        self.run_regex_test(regex=allregex.true_bool_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=white_space_sens_assert)
        
    def test_false_regex(self):
        white_space_sens_assert = lambda p,c,s,t: (self.assertIsNotNone if 
                                                   not t and prefix_suffix_whitespace(p,s) 
                                                   else self.assertIsNone)
        self.run_regex_test(regex=allregex.false_bool_regex, 
                            int_assert_chooser=lambda p,c,s: self.assertIsNone,
                            float_assert_chooser=lambda p,c,s: self.assertIsNone,
                            exp_assert_chooser=lambda p,c,s: self.assertIsNone,
                            bool_assert_chooser=white_space_sens_assert)

class RegexDataTest(unittest.TestCase):
    def setUp(self):
        self.false_checks = ["", " \t \n ", "a", "a ", " a", " a ", 
                             ".", " . ", "e", " e ", "3.14", "0"]
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep "]
        self.suffixes = self.prefixes
    
    # Helper function for function naming
    def none_check_str(self, test_func):
        if test_func == self.assertIsNotNone:
            return "not None"
        elif test_func == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
    
    def test_contains_monetary_symbol(self):
        '''
        Ensure we can detect occurrence of monetary symbol.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Contains Monetary Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM"]:
                    assert_func(re.search(allregex.contains_monetary_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in ["$", u"\u00A3", u"\u20AC", "31.45$"]:
                    assert_func(re.search(allregex.contains_monetary_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                       
                # Contains Dollar Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u00A3", u"\u20AC"]:
                    assert_func(re.search(allregex.contains_dollar_symbol_regex, 
                                              prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in ["$", "31.45$"]:
                    assert_func(re.search(allregex.contains_dollar_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Contains Pound Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u20AC", "$", "31.45$"]:
                    assert_func(re.search(allregex.contains_pound_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in [u"\u00A3", u"end pound\u00A3"]:
                    assert_func(re.search(allregex.contains_pound_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                # Contains Euro Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u00A3", "$", "31.45$"]:
                    assert_func(re.search(allregex.contains_euro_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in [u"\u20AC", u"end euro\u20AC"]:
                    assert_func(re.search(allregex.contains_euro_symbol_regex, 
                                              prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
    
    def test_begins_monetary_symbol(self):
        '''
        Ensure we can detect beginning of monetary symbol.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Begins with Monetary Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", "31.45$"]:
                    assert_func(re.search(allregex.begins_with_monetary_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for check_str in ["$", u"\u00A3", u"\u20AC"]:
                    assert_func(re.search(allregex.begins_with_monetary_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Begins with Dollar Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u00A3", u"\u20AC", "31.45$"]:
                    assert_func(re.search(allregex.begins_with_dollar_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for check_str in ["$"]:
                    assert_func(re.search(allregex.begins_with_dollar_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Begins with Pound Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u20AC", "$", "31.45$", u"end pound\u00A3"]:
                    assert_func(re.search(allregex.begins_with_pound_symbol_regex, 
                                              prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for check_str in [u"\u00A3"]:
                    assert_func(re.search(allregex.begins_with_pound_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                # Begins with Euro Symbol
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["k", "3.24", "2MM", u"\u00A3", "$", "31.45$", u"end euro\u20AC"]:
                    assert_func(re.search(allregex.begins_with_euro_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for check_str in [u"\u20AC"]:
                    assert_func(re.search(allregex.begins_with_euro_symbol_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
    def test_end_scaling(self):
        '''
        Ensure we can detect numeric endings with multiplier symbols.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Ends with Thousands Indicator
                assert_func = self.assertIsNone
                
                for check_str in self.false_checks + ["k", ".k", "3.24", "2MM", "31.45$"]:
                    assert_func(re.search(allregex.ends_with_thousands_scaling_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not suffix or suffix.isspace() else self.assertIsNone
                for check_str in ["3.14k", "1.k", "0k \t ", "2k \t\r"]:
                    assert_func(re.search(allregex.ends_with_thousands_scaling_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Ends with Millions Indicator
                assert_func = self.assertIsNone
                for check_str in self.false_checks + ["M", "MM", "3.14mm", ".M", ".MM", "2.14k", "3.24", "31.45$"]:
                    assert_func(re.search(allregex.ends_with_millions_scaling_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if not suffix or suffix.isspace() else self.assertIsNone
                for check_str in ["3.14M", "1.M", "0M \t ", "2M \t\r",
                                  "3.14MM", "1.MM", "0MM \t ", "2MM \t\r"]:
                    assert_func(re.search(allregex.ends_with_millions_scaling_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))

    def test_contains_wrapped_regex(self):
        '''
        Ensure we can detect wrapped data.
        '''
        bracket_tests = ["[3.14]", "[]", "[0] \t "]
        parens_tests = ["(3.14)", "()", "(0) \t "]
        curly_bracket_tests = ["{3.14}", "{}", "{0} \t "]
        false_brackets = self.false_checks + ["[", "]", "(", ")", "{", "}" "3.24"]
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Wrapped by any of brackets, curly brackets, or parens
                assert_func = self.assertIsNone
                for check_str in false_brackets:
                    assert_func(re.search(allregex.contains_control_wrapping_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in bracket_tests + parens_tests + curly_bracket_tests:
                    assert_func(re.search(allregex.contains_control_wrapping_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by brackets
                assert_func = self.assertIsNone
                for check_str in false_brackets + parens_tests + curly_bracket_tests:
                    assert_func(re.search(allregex.contains_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in bracket_tests:
                    assert_func(re.search(allregex.contains_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by parens
                assert_func = self.assertIsNone
                for check_str in false_brackets + bracket_tests + curly_bracket_tests:
                    assert_func(re.search(allregex.contains_parens_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in parens_tests:
                    assert_func(re.search(allregex.contains_parens_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by curly brackets
                assert_func = self.assertIsNone
                for check_str in false_brackets + bracket_tests + parens_tests:
                    assert_func(re.search(allregex.contains_curly_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone
                for check_str in curly_bracket_tests:
                    assert_func(re.search(allregex.contains_curly_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
               
    def test_wrapped_regex(self):
        '''
        Ensure we can detect current depth wrapped data.
        '''
        bracket_tests = ["[3.14]", "[]", "[0] \t "]
        parens_tests = ["(3.14)", "()", "(0) \t "]
        curly_bracket_tests = ["{3.14}", "{}", "{0} \t "]
        single_quotes_tests = ["'3.14'", "''", "'0' \t "]
        double_quotes_tests = ['"3.14"', '""', '"0" \t ']
        false_brackets = self.false_checks + ["[", "]", "(", ")", "{", "}" , "'", '"', 
                                              "[ )", "( ]", "{ ]", "[ }", "'\"", "\"'",
                                              "3.24"]
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Wrapped by brackets
                assert_func = self.assertIsNone
                for check_str in (false_brackets + parens_tests + curly_bracket_tests + 
                                 single_quotes_tests + double_quotes_tests):
                    assert_func(re.search(allregex.bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in bracket_tests:
                    assert_func(re.search(allregex.bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by parens
                assert_func = self.assertIsNone
                for check_str in (false_brackets + bracket_tests + curly_bracket_tests +
                                 single_quotes_tests + double_quotes_tests):
                    assert_func(re.search(allregex.parens_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in parens_tests:
                    assert_func(re.search(allregex.parens_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by curly brackets
                assert_func = self.assertIsNone
                for check_str in (false_brackets + bracket_tests + parens_tests +
                                 single_quotes_tests + double_quotes_tests):
                    assert_func(re.search(allregex.curly_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in curly_bracket_tests:
                    assert_func(re.search(allregex.curly_bracketed_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by single quotes
                assert_func = self.assertIsNone
                for check_str in (false_brackets + bracket_tests + parens_tests +
                                 curly_bracket_tests + double_quotes_tests):
                    assert_func(re.search(allregex.single_quotes_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in single_quotes_tests:
                    assert_func(re.search(allregex.single_quotes_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by double quotes
                assert_func = self.assertIsNone
                for check_str in (false_brackets + bracket_tests + parens_tests +
                                 curly_bracket_tests + single_quotes_tests):
                    assert_func(re.search(allregex.double_quotes_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in double_quotes_tests:
                    assert_func(re.search(allregex.double_quotes_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                # Wrapped by any of brackets, curly brackets, parens, or quotes
                assert_func = self.assertIsNone
                for check_str in false_brackets:
                    assert_func(re.search(allregex.control_wrapping_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in (bracket_tests + parens_tests + curly_bracket_tests + 
                                 single_quotes_tests + double_quotes_tests):
                    assert_func(re.search(allregex.control_wrapping_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))

class RegexDateTest(unittest.TestCase):
    def setUp(self):
        self.false_checks = ["", " \t \n ", "a", "a ", " a", " a ", 
                             ".", " . ", "e", " e ", "3.14", "0", "fiscal"]
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep "]
        self.suffixes = self.prefixes
    
    # Helper function for function naming
    def none_check_str(self, test_func):
        if test_func == self.assertIsNotNone:
            return "not None"
        elif test_func == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
        
    def test_year(self):
        '''
        Ensure we can detect 'year' and 'fiscal year' strings.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                assert_func = self.assertIsNone
                
                for check_str in self.false_checks:
                    assert_func(re.search(allregex.year_regex, prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in ["year", "Year", "fiscal year", "fiscalyear", 
                                 "Fiscal Year", "yEaR", "fiSCalYeaR"]:
                    assert_func(re.search(allregex.year_regex, prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))

class RegexTitlesTest(unittest.TestCase):
    def setUp(self):
        self.transfers = ["Tran", "Trans", "Tran.", "Trans.",
                          "Tran ", "Trans ", "Tran. ", "Trans. ",
                          "Transfer", "Transfers",
                          "Transfer ", "Transfers "]
        self.account_strings = ["0", "103", "321-", "321-85", "103-49572-108945"]
        
        self.false_checks = ["a", "a ", " a", " a ", ".", " . ", 
                             "A", "ABC", "ABC-", "ABC-ZY", " 0A", "1B3", 
                             "32C-", "321-ZY ",
                             "e", " e ", "3.14", "0a", "k", "3.24", "2mm", 
                             "Transportation Out", "Transp In"] + self.transfers
        
        self.transfers_in = [trans + "In" for trans in self.transfers] + [trans + "From" for trans in self.transfers]
        self.transfers_out = [trans + "Out" for trans in self.transfers] + [trans + "To" for trans in self.transfers]
        self.transfers_any = self.transfers_in + self.transfers_out
        
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep ", "524s"]
        self.suffixes = self.prefixes
    
    # Helper function for function naming
    def none_check_str(self, test_func):
        if test_func == self.assertIsNotNone:
            return "not None"
        elif test_func == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
    
    def test_contains_transfer_title(self):
        '''
        Ensure we can detect occurrence of transfer titles.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Contains Transfer Title
                assert_func = self.assertIsNone
                for check_str in self.false_checks:
                    assert_func(re.search(allregex.contains_transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    assert_func(re.search(allregex.contains_transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    assert_func(re.search(allregex.contains_transfer_any_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Transfers In
                for check_str in (self.transfers_in + 
                            [trans.lower() for trans in self.transfers_in] + 
                            [trans.upper() for trans in self.transfers_in]):
                    assert_func = self.assertIsNotNone
                    assert_func(re.search(allregex.contains_transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                    assert_func = self.assertIsNone
                    assert_func(re.search(allregex.contains_transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                
                # Transfers Out
                for check_str in (self.transfers_out + 
                                [trans.lower() for trans in self.transfers_out] + 
                                [trans.upper() for trans in self.transfers_out]):
                    assert_func = self.assertIsNotNone
                    assert_func(re.search(allregex.contains_transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                    assert_func = self.assertIsNone
                    assert_func(re.search(allregex.contains_transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Any Transfers
                assert_func = self.assertIsNotNone
                for check_str in (self.transfers_any + 
                                [trans.lower() for trans in self.transfers_any] + 
                                [trans.upper() for trans in self.transfers_any]):
                    assert_func(re.search(allregex.contains_transfer_any_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))

    def test_transfer_title(self):
        '''
        Ensure we can detect sole occurrence of transfer titles.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Transfer Title
                assert_func = self.assertIsNone
                for check_str in self.false_checks:
                    assert_func(re.search(allregex.transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    assert_func(re.search(allregex.contains_transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    assert_func(re.search(allregex.contains_transfer_any_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Transfers In
                for check_str in (self.transfers_in + 
                            [trans.lower() for trans in self.transfers_in] + 
                            [trans.upper() for trans in self.transfers_in]):
                    assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                    assert_func(re.search(allregex.transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
                    assert_func = self.assertIsNone
                    assert_func(re.search(allregex.transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                   
                
                # Transfers Out
                for check_str in (self.transfers_out + 
                            [trans.lower() for trans in self.transfers_out] + 
                            [trans.upper() for trans in self.transfers_out]):
                    assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                    assert_func(re.search(allregex.transfer_out_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                           self.none_check_str(assert_func))
                    
                    assert_func = self.assertIsNone
                    assert_func(re.search(allregex.contains_transfer_in_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                
                # Any Transfers
                assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                for check_str in (self.transfers_any + 
                            [trans.lower() for trans in self.transfers_any] + 
                            [trans.upper() for trans in self.transfers_any]):
                    assert_func(re.search(allregex.transfer_any_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))
                    
    def test_account_string(self):
        '''
        Ensure we can detect sole occurrence of transfer titles.
        '''
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # False checks
                assert_func = self.assertIsNone
                for check_str in self.false_checks:
                    assert_func(re.search(allregex.account_string_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+
                                          "' should have returned "+self.none_check_str(assert_func))
                    assert_func(re.search(allregex.account_string_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+
                                          "' should have returned "+self.none_check_str(assert_func))
                    assert_func(re.search(allregex.account_string_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+
                                          "' should have returned "+self.none_check_str(assert_func))
                
                # Account String
                for check_str in self.account_strings:
                    assert_func = self.assertIsNotNone if prefix_suffix_whitespace(prefix, suffix) else self.assertIsNone
                    assert_func(re.search(allregex.account_string_regex, 
                                            prefix+check_str+suffix), 
                                          "String '"+prefix+check_str+suffix+"' should have returned "+
                                          self.none_check_str(assert_func))

if __name__ == "__main__":
    unittest.main()

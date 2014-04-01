# This import fixes sys.path issues
import parentpath

import unittest
import os
from os.path import dirname
from carpenter.blocks import tableanalyzer
from datawrap import tableloader
from pprint import pprint

class TableAnalyzerTest(unittest.TestCase):
    '''
    Tests all functionality of the table analyzer tools.
    '''
    def setUp(self):
        self.test_block_file_pairs = []
        self.test_single_block_file_pairs = []
        self.data_dir = os.path.join(dirname(__file__), 'table_data')
        for tnum in range(0,20):
            filename_base = os.path.join(self.data_dir, "test_"+str(tnum))
            self.test_block_file_pairs.append((filename_base, filename_base+"_output"))
            self.test_single_block_file_pairs.append((filename_base, filename_base+"_sblock_output"))
            
    def try_load_data(self, basename):
        '''
        Helper for loading data with an unspecified extension
        '''
        try:
            return tableloader.read(basename+".csv")
        except IOError:
            try:
                return tableloader.read(basename+".xlsx")
            except IOError:
                try:
                    return tableloader.read(basename+".xls")
                except IOError:
                    raise ValueError("Cannot load any data with base name '"+basename+"'")
    
    def load_data_number(self, test_number, complete_blocks_test=False):
        '''
        Loads the input and expected output data for a particular
        test run.
        '''
        if complete_blocks_test:
            raw_file_name, expect_file_name = self.test_single_block_file_pairs[test_number]
        else:
            raw_file_name, expect_file_name = self.test_block_file_pairs[test_number]
        raw_table_analyzer = tableanalyzer.TableAnalyzer(self.try_load_data(raw_file_name))
        convert_expect = self.try_load_data(expect_file_name)
        return raw_table_analyzer, convert_expect
    
    def compare_block(self, result_block, expect_block):
        self.assertEqual(len(result_block), len(expect_block))
        for row_index in range(len(result_block)):
            self.assertEqual(len(result_block[row_index]), len(expect_block[row_index]))
            for column_index in range(len(result_block[row_index])):
                try:
                    self.assertEqual(str(result_block[row_index][column_index]).strip(), 
                                     str(expect_block[row_index][column_index]).strip())
                except:
                    self.assertEqual(result_block[row_index][column_index], 
                                     expect_block[row_index][column_index])
                   
    def compare_conversion(self, test_number, expected_word_flag, num_expected_tables, 
                           num_expected_blocks, complete_blocks_test=False):
        raw_table_analyzer, convert_expect = self.load_data_number(
            test_number, complete_blocks_test)
        self.assertEqual(len(raw_table_analyzer.raw_tables), num_expected_tables)
        self.assertEqual(len(convert_expect), num_expected_blocks, 
                         "Number of expected blocks '%s' does not match "
                         "loaded expectation size '%s'; were there extra "
                         "worksheets attached?" % (len(convert_expect), 
                                                   num_expected_blocks))
        
        block = False
        blocks = False
        try:
            blocks = raw_table_analyzer.generate_blocks(
                assume_complete_blocks=complete_blocks_test)
            self.assertEqual(len(blocks), num_expected_blocks)
            
            for block_index in range(num_expected_blocks):
                block = blocks[block_index]
                self.assertEqual(block.get_worst_flag_level(), 
                                 expected_word_flag[block_index])
                expect_block = convert_expect[block_index]
                
                result_block = block.convert_to_row_table(add_units=False)
                self.compare_block(result_block, expect_block)
        except:
            if block:
                print "Block:"
                try: pprint(block.convert_to_row_table(add_units=False))
                except: pass
                print block.start, block.end
                print "Flags:"
                try: pprint(block.get_relavent_flags())
                except: pass
            elif blocks:
                print "Unprocessed Blocks:"
                try:
                    for block in blocks: 
                        pprint(block.copy_raw_block())
                except: pass
            raise
    
    def test_basic_table(self):
        '''Test test_0.csv => test_0_output.csv'''
        test_number = 0
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['minor']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
    
    def test_offset_multi_title(self):
        '''Test test_1.csv => test_1_output.csv'''
        test_number = 1
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_dual_block(self):
        '''Test test_2.csv => test_2_output.xlsx'''
        test_number = 2
        num_expected_tables = 1
        num_expected_blocks = 2
        expected_flag = ['interpreted', 'minor']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_multi_block(self):
        '''Test test_3.csv => test_3_output.xlsx'''
        test_number = 3
        num_expected_tables = 1
        num_expected_blocks = 4
        expected_flag = ['minor', 'minor', 'minor', 'interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_dollar(self):
        '''Test test_4.csv => test_4_output.csv'''
        test_number = 4
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)

    def test_euro(self):
        '''Test test_5.csv => test_5_output.csv'''
        test_number = 5
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_pound(self):
        '''Test test_6.csv => test_6_output.csv'''
        test_number = 6
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_wrappers(self):
        '''Test test_7.csv => test_7_output.csv'''
        test_number = 7
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['interpreted']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_value_multipliers(self):
        '''Test test_8.csv => test_8_output.csv'''
        test_number = 8
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['warning']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_sparse_block(self):
        '''Test test_9.csv => test_9_output.csv'''
        test_number = 9
        num_expected_tables = 1
        num_expected_blocks = 1
        expected_flag = ['warning']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks)
        
    def test_year_identifier(self):
        '''Test test_10.csv => test_10_output.xlsx'''
        test_number = 10
        num_expected_tables = 1
        num_expected_blocks = 2
        expected_flag = ['interpreted', 'interpreted']
        self.compare_conversion(test_number, expected_flag, 
                               num_expected_tables, num_expected_blocks)
        
    def test_ultimate_sheet(self):
        '''Test test_11.csv => test_11_output.xlsx'''
        test_number = 11
        num_expected_tables = 1
        num_expected_blocks = 4
        expected_flag = ['interpreted', 'minor', 'minor', 'interpreted']
        self.compare_conversion(test_number, expected_flag, 
                               num_expected_tables, num_expected_blocks)
        
    def test_broken_single_block(self):
        '''Test test_12.csv => test_12_sblock_output.xlsx'''
        test_number = 12
        num_expected_tables = 1
        num_expected_blocks = 7
        expected_flag = ['interpreted', 'error', 'minor', 'error', 
                        'error', 'error', 'error']
        self.compare_conversion(test_number, expected_flag, num_expected_tables, num_expected_blocks, 
                                complete_blocks_test=True)

if __name__ == "__main__":
    unittest.main()

import sys
from datawrap.tablewrap import TableTranspose, squarify_table
from block import TableBlock, InvalidBlockError
from flagable import Flagable
from cellanalyzer import is_empty_cell, is_text_cell, is_num_cell, auto_convert_cell
from datawrap import tableloader

class TableAnalyzer(Flagable):
    '''
    Analyzes lists of 2D tables generated from cvs and excel files
    in order to extract and reformat data blocks in an ordered 
    fashion.
    
    The analyzer performs basic data conversions from known string
    patterns into numeric values. It also flags these changes and
    keeps all flag level changes or problems stored in flags_by_table.
    
    Note that the input table is squarified so that all rows are the
    same size. This affects the input table as the original data is
    not copied.
    
    Args:
        tables: The list of 2D tables holding the csv or excel data
        assume_complete_blocks: Optimizes block loopups by not allowing
            titles to be extended. Blocks should be perfectly dense 
            to be found when active.
        parens_as_neg: Converts numerics surrounded by parens to negative 
            values
    '''
    def __init__(self, tables, assume_complete_blocks=False, parens_as_neg=True):
        self.raw_tables = tables
        squarify_table(self.raw_tables)
        self.processed_tables = None
        self.flags_by_table = None
        self.units_by_table = None
        self.processed_blocks = None
        self.assume_complete_blocks = assume_complete_blocks
        self.parens_as_neg = parens_as_neg
    
    def preprocess(self):
        '''
        Performs initial cell conversions to standard types. This will
        strip units, scale numbers, and identify numeric data where it's
        convertible.
        '''
        self.processed_tables = []
        self.flags_by_table = []
        self.units_by_table = []
        for worksheet,rtable in enumerate(self.raw_tables):
            ptable, flags, units = self.preprocessPass(rtable, worksheet)
            self.processed_tables.append(ptable)
            self.flags_by_table.append(flags)
            self.units_by_table.append(units)
            
        return self.processed_tables
    
    def generate_blocks(self, assume_complete_blocks=None):
        '''
        Identifies and extracts all blocks from the input tables. These blocks
        are logical identifiers for where related information resides in the
        original table. Any block can be converted into a row-titled table
        which can then be stitched together with other tables from other blocks
        to form a fully converted data set.
        
        Args:
            assume_complete_blocks: Optimizes block loopups by not allowing titles 
                to be extended. Blocks should be perfectly dense to be found when 
                active. Optional, defaults to constructor value.
        '''
        # Store this value to restore object settings later
        _track_assume_blocks = self.assume_complete_blocks
        try:
            if assume_complete_blocks != None:
                self.assume_complete_blocks = assume_complete_blocks
            if self.processed_tables == None:
                self.preprocess()
            self.processed_blocks = []
            
            for worksheet in range(len(self.processed_tables)):
                ptable = self.processed_tables[worksheet]
                flags = self.flags_by_table[worksheet]
                units = self.units_by_table[worksheet]
                
                if not self.assume_complete_blocks:
                    self.fill_in_table(ptable, worksheet, flags)
                    
                self.processed_blocks.extend(self._findBlocks(
                        ptable, worksheet, flags, units, 
                        { 'worksheet', worksheet }))
                
            return self.processed_blocks
        finally:
            # After execution, reset assume_complete_blocks back
            self.assume_complete_blocks = _track_assume_blocks
    
    def preprocessPass(self, table, worksheet):
        '''
        Performs a preprocess pass of the table to attempt naive conversions 
        of data and to record the initial types of each cell.
        '''
        table_conversion = []
        flags = {}
        units = {}
        for rind, row in enumerate(table):
            conversion_row = []
            table_conversion.append(conversion_row)
            for column_index, cell in enumerate(row):
                position = (rind, column_index)
                # Do the heavy lifting in preProcessCell
                conversion = auto_convert_cell(self, cell, position, worksheet, 
                        flags, units, parens_as_neg=self.parens_as_neg)
                conversion_row.append(conversion)
        # Give back our conversions, type labeling, and conversion flags
        return table_conversion, flags, units
    
    def fill_in_table(self, table, worksheet, flags):
        '''
        Fills in any rows with missing right hand side data with empty cells.
        '''
        max_row = 0
        min_row = sys.maxint
        for row in table:
            if len(row) > max_row:
                max_row = len(row)
            if len(row) < min_row:
                min_row = len(row)
        if max_row != min_row:
            for row in table:
                if len(row) < max_row:
                    row.extend([None]*(max_row-len(row)))
    
    def _findBlocks(self, converted_table, worksheet, flags, units, 
                    block_meta=None, start_pos=None, end_pos=None):
        '''
        A block is considered any region where we have the
        following structure:
        
        text | text or number | ... | text of number
        text | number         | ... | number
        text | number         | ... | number
        ...    .                .     .
        ...    .                .     .
        ...    .                .     .
        
        or:
        
        text           | ... | text           | text
        text or number | ... | text or number | number
        text or number | ... | text of number | number
        ...              .     .                .
        ...              .     .                .
        ...              .     .                .
        
        With the default cases of all text and all numbers
        matching to a single block encompassing the entire
        table.
        '''
        blocks = []
        used_cells = []
        
        if start_pos == None:
            start_pos = (0, 0)
        if end_pos == None:
            end_pos = (len(converted_table), max(
                            len(row) for row in converted_table))
        
        # Track used cells -- these can be non-rectangular, but must be 2D
        for row in converted_table:
            used_cells.append([False]*len(row))
        # Catch an empty table or blank rows
        if not converted_table or all(not row for row in converted_table):
            blocks.append(converted_table)
            self.flag_change(flags, 'error', worksheet=worksheet, 
                            message="Empty table")
            return blocks
        
        # Start with a boolean to get the while loop going
        block = True
        block_search_start = start_pos
        while block:
            # Returns None if no more blocks exist
            block = self._find_valid_block(converted_table, worksheet, 
                                         flags, units, used_cells, 
                                         block_search_start, end_pos)
            if block:
                blocks.append(block)
                # Restart on the row of the last block at the
                # beginning column
                block_search_start = (block.start[0], start_pos[1])
            
        return blocks
    
    def _find_valid_block(self, table, worksheet, flags, units, 
                          used_cells, start_pos, end_pos):
        '''
        Searches for the next location where a valid block could reside
        and constructs the block object representing that location.
        '''
        for row_index in range(len(table)):
            if row_index < start_pos[0] or row_index > end_pos[0]:
                continue
            convRow = table[row_index]
            used_row = used_cells[row_index]
            for column_index, conv in enumerate(convRow):
                if (column_index < start_pos[1] or 
                    column_index > end_pos[1] or used_row[column_index]):
                    continue
                # Is non empty cell?
                if not is_empty_cell(conv):
                    block_start, block_end = self._find_block_bounds(
                             table, used_cells, (row_index, column_index), 
                             start_pos, end_pos)
                    if (block_end[0] > block_start[0] and 
                        block_end[1] > block_start[1]):
                        try: return TableBlock(
                                 table, used_cells, block_start, block_end, worksheet, 
                                 flags, units, self.assume_complete_blocks)
                        except InvalidBlockError: pass
                        # Prevent infinite loops if something goes wrong
                        used_cells[row_index][column_index] = True
    
    def _find_block_bounds(self, table, used_cells, possible_block_start, 
                           start_pos, end_pos):
        '''
        First walk the rows, checking for the farthest left column belonging 
        to the block and the bottom most row belonging to the block. If a 
        blank cell is hit and the column started with a blank cell or has 
        length <= 2, then restart one row to the right. Alternatively, if
        assume_complete_blocks has been set to true, any blank cell stops
        block detection.
        
        Then walk the columns until a column is reached which has blank cells 
        down to the row which marked the as the row end from prior iteration.
        '''
        # If we're only looking for complete blocks, then just walk
        # until we hit a blank cell
        if self.assume_complete_blocks:
            block_start, block_end = self._find_complete_block_bounds(
                                        table, used_cells, possible_block_start, 
                                        start_pos, end_pos)
        # Otherwise do a smart, multi-pass approach to finding blocks
        # with potential missing fields
        else:
            block_start, block_end = self._find_block_start(
                                        table, used_cells, possible_block_start, 
                                        start_pos, end_pos)
                
            block_start, block_end = self._find_block_end(
                                        table, used_cells, block_start, block_end, 
                                        start_pos, end_pos)
        return block_start, block_end
    
    def _find_complete_block_bounds(self, table, used_cells, possible_block_start, 
                                    start_pos, end_pos):
        '''
        Finds the end of a block from a start location and a suggested 
        end location.
        '''
        block_start = list(possible_block_start)
        block_end = list(possible_block_start)
        table_row = table[block_start[0]]
        used_row = used_cells[block_start[0]]
        # Find which column the titles end on
        for column_index in range(block_start[1], end_pos[1]+1):
            # Ensure we catch the edge case of the data reaching the edge of
            # the table -- block_end should then equal end_pos
            block_end[1] = max(block_end[1], column_index)
            if (column_index == end_pos[1] or used_row[column_index] or 
                    is_empty_cell(table_row[column_index])):
                break
        for row_index in range(block_start[0]+1, end_pos[0]+1):
            block_end[0] = row_index
            # Stop if we reach the end of the table space
            if block_end[0] == end_pos[0]:
                break
            table_row = table[row_index]
            blank = False
            for column_index in range(block_start[1], block_end[1]):
                if (column_index == block_end[1] or used_row[column_index] or 
                        is_empty_cell(table_row[column_index])):
                    blank = True
                    break
            if blank:
                break
        return block_start, block_end
    
    def _find_block_start(self, table, used_cells, possible_block_start, 
                          start_pos, end_pos):
        '''
        Finds the start of a block from a suggested start location.
        This location can be at a lower column but not a lower row.
        
        Note this also finds the lowest row of block_end.
        '''
        current_col = possible_block_start[1]
        block_start = list(possible_block_start)
        block_end = list(possible_block_start)
        repeat = True
        checked_all = False
        # Repeat until we've met satisfactory conditions for 
        # catching all edge cases or we've checked all valid
        # block locations
        while(not checked_all and repeat):
            block_end[0] = max(block_end[0], possible_block_start[0])
            block_end[1] = max(block_end[1], current_col)
            table_column = TableTranspose(table)[current_col]
            used_column = TableTranspose(used_cells)[current_col]
            # We need to find a non empty cell before we can stop
            blank_start = is_empty_cell(table_column[possible_block_start[0]])
            # Unless we have assume_complete_blocks set to True
            if blank_start and self.assume_complete_blocks:
                # Found a blank? We're done
                repeat = False
                break
            blank_exited = not blank_start
            blank_repeat_threshold = 3
            parent_title = blank_start or is_text_cell(table_column[possible_block_start[0]])
            #TODO refactor code below into new function for easier reading
            # Analyze the beginning columns
            for row_index in range(possible_block_start[0], end_pos[0]+1):
                # Ensure we catch the edge case of the data reaching the edge of
                # the table -- block_end should then equal end_pos
                if blank_exited:
                    block_end[0] = max(block_end[0], row_index)
                if row_index == end_pos[0] or used_column[row_index]:
                    # We've gone through the whole range
                    checked_all = True
                    break
                elif not blank_exited:
                    blank_exited = not is_empty_cell(table_column[row_index])
                elif is_empty_cell(table_column[row_index]):
                    current_col += 1
                    break
                else:
                    # Go find the left most column that's still valid
                    table_row = table[row_index]
                    used_row = used_cells[row_index]
                    for column_index in range(current_col, start_pos[1]-1, -1):
                        if is_empty_cell(table_row[column_index]) or used_row[column_index]:
                            break
                        else:
                            block_start[1] = min(block_start[1], column_index)
                # Check if we've seen few enough cells to guess that we have a repeating title
                repeat = blank_start or 1+row_index-possible_block_start[0] <= blank_repeat_threshold
            
        return block_start, block_end
    
    def _find_block_end(self, table, used_cells, block_start, block_end, 
                        start_pos, end_pos):
        '''
        Finds the end of a block from a start location and a suggested 
        end location.
        '''
        table_row = table[block_start[0]]
        used_row = used_cells[block_start[0]]
        # Find which column the titles end on
        for column_index in range(block_start[1], end_pos[1]+1):
            # Ensure we catch the edge case of the data reaching the edge of
            # the table -- block_end should then equal end_pos
            block_end[1] = max(block_end[1], column_index)
            if column_index == end_pos[1]:
                break
            if used_row[column_index]:
                break
            elif is_empty_cell(table_row[column_index]):
                table_column = TableTranspose(table)[column_index]
                used_column = TableTranspose(used_cells)[column_index]
                found_cell = False
                for row_index in range(block_start[0], block_end[0]):
                    if not is_empty_cell(table_column[row_index]):
                        found_cell = True
                        break
                # If we have a column of blanks, stop
                if not found_cell:
                    break
        return block_start, block_end
    